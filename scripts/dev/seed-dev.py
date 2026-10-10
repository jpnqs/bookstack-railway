#!/usr/bin/env python3
"""DEV/CI ONLY: seed a fresh local BookStack with test content and MCP bot users.

Creates:
  - shelf "Engineering" with books "Handbook" (chapter + pages) and "Runbooks"
  - book "HR Confidential", restricted so that bot roles cannot see it
  - book "AI Inbox", the only place the writer bot may create content
  - roles "MCP Reader" / "MCP Writer", bot users, and one API token per bot

Writes ids and bot tokens to seed-output.local.json (git-ignored).

Usage (stack running, admin initialised via scripts/init-admin.sh):
  python scripts/dev/seed-dev.py <admin-email> [--url http://localhost:6875]
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUTPUT = os.path.join(REPO, "seed-output.local.json")

VIEW_ALL = ["bookshelf-view-all", "book-view-all", "chapter-view-all", "page-view-all"]


def compose(*args, capture=False):
    env = dict(os.environ, MSYS_NO_PATHCONV="1")
    res = subprocess.run(["docker", "compose", *args], cwd=REPO, env=env,
                         check=True, text=True, capture_output=capture)
    return res.stdout.strip() if capture else None


def create_token(email, name, days):
    expires = (dt.date.today() + dt.timedelta(days=days)).isoformat()
    compose("cp", os.path.join(HERE, "create-api-token.php"), "bookstack:/tmp/create-api-token.php")
    try:
        return compose("exec", "-T", "bookstack", "php", "/tmp/create-api-token.php",
                       email, name, expires, capture=True)
    finally:
        compose("exec", "-T", "bookstack", "rm", "-f", "/tmp/create-api-token.php")


class Api:
    def __init__(self, base, token):
        self.base = base.rstrip("/")
        self.token = token

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(f"{self.base}/api/{path}", data=data, method=method)
        req.add_header("Authorization", f"Token {self.token}")
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read() or b"null")
        except urllib.error.HTTPError as e:
            sys.exit(f"{method} /api/{path} failed: {e.code} {e.read().decode(errors='replace')[:500]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("admin_email")
    ap.add_argument("--url", default="http://localhost:6875")
    args = ap.parse_args()

    api = Api(args.url, create_token(args.admin_email, "seed-dev (temporary)", 1))

    if any(b["name"] == "AI Inbox" for b in api.call("GET", "books?count=500")["data"]):
        sys.exit("Already seeded. Reset with: docker compose down -v")

    # Content
    handbook = api.call("POST", "books", {"name": "Handbook", "description": "Company handbook"})
    onboarding = api.call("POST", "chapters", {"book_id": handbook["id"], "name": "Onboarding"})
    p_laptop = api.call("POST", "pages", {
        "chapter_id": onboarding["id"], "name": "Laptop setup",
        "markdown": "# Laptop setup\n\nInstall the VPN client, then enable disk encryption.\n\n"
                    "- Ask IT for a **hardware key**\n- Read the [security policy](https://example.com/policy)\n",
        "tags": [{"name": "topic", "value": "it"}],
    })
    p_wysiwyg = api.call("POST", "pages", {
        "book_id": handbook["id"], "name": "Office locations",
        "html": "<h2>Berlin</h2><p>Main office, 3rd floor.</p><ul><li>Kitchen</li><li>Library</li></ul>",
    })
    runbooks = api.call("POST", "books", {"name": "Runbooks", "description": "Operational runbooks"})
    p_restart = api.call("POST", "pages", {
        "book_id": runbooks["id"], "name": "Restarting the database",
        "markdown": "# Restarting the database\n\nUse the Railway dashboard. Never restart during backups.\n",
    })
    shelf = api.call("POST", "shelves", {"name": "Engineering", "books": [handbook["id"], runbooks["id"]]})

    hr = api.call("POST", "books", {"name": "HR Confidential", "description": "Salaries and reviews"})
    p_hr = api.call("POST", "pages", {
        "book_id": hr["id"], "name": "Salary bands 2026",
        "markdown": "# Salary bands\n\nCANARY-HR-7f3a: this text must never be visible to MCP bots.\n",
    })
    inbox = api.call("POST", "books", {"name": "AI Inbox", "description": "Drafts created by AI agents, pending human review"})

    # Bot roles and users
    reader_role = api.call("POST", "roles", {
        "display_name": "MCP Reader", "description": "Read-only API access for AI agents",
        "permissions": ["access-api", *VIEW_ALL],
    })
    writer_role = api.call("POST", "roles", {
        "display_name": "MCP Writer", "description": "Read + create in AI Inbox only",
        "permissions": ["access-api", *VIEW_ALL],
    })

    # HR: no inheritance, nobody but admins.
    api.call("PUT", f"content-permissions/book/{hr['id']}", {
        "fallback_permissions": {"inheriting": False, "view": False, "create": False, "update": False, "delete": False},
        "role_permissions": [],
    })
    # AI Inbox: writer role may view + create; no update/delete.
    api.call("PUT", f"content-permissions/book/{inbox['id']}", {
        "fallback_permissions": {"inheriting": True},
        "role_permissions": [
            {"role_id": writer_role["id"], "view": True, "create": True, "update": False, "delete": False},
        ],
    })

    pw = lambda: os.urandom(24).hex()  # never used to log in; bots authenticate via API token only
    reader = api.call("POST", "users", {"name": "MCP Reader Bot", "email": "mcp-reader@bots.local",
                                        "password": pw(), "roles": [reader_role["id"]], "send_invite": False})
    writer = api.call("POST", "users", {"name": "MCP Writer Bot", "email": "mcp-writer@bots.local",
                                        "password": pw(), "roles": [writer_role["id"]], "send_invite": False})

    out = {
        "bookstack_url": args.url,
        "shelves": {"engineering": shelf["id"]},
        "books": {"handbook": handbook["id"], "runbooks": runbooks["id"], "hr": hr["id"], "inbox": inbox["id"]},
        "chapters": {"onboarding": onboarding["id"]},
        "pages": {"laptop": p_laptop["id"], "wysiwyg": p_wysiwyg["id"], "restart": p_restart["id"], "hr": p_hr["id"]},
        "roles": {"reader": reader_role["id"], "writer": writer_role["id"]},
        "users": {"reader": reader["id"], "writer": writer["id"]},
        "tokens": {
            "reader": create_token(reader["email"], "mcp-dev", 30),
            "writer": create_token(writer["email"], "mcp-dev", 30),
        },
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Seeded. Ids and bot tokens written to {os.path.relpath(OUTPUT, REPO)}")


if __name__ == "__main__":
    main()
