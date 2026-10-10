# Deploying to Railway

Railway does not run `docker-compose.yml`. Create **two services from this
repo** in one Railway project (the MCP server will later join the same project
so it can use the private network).

## 1. Project and services

1. Create a Railway project and connect this GitHub repo.
2. Service **`db`** (name it exactly `db`; the reference variables below use it):
   - Settings → Source → Root directory: `/db`
   - Settings → Config-as-code file: `/db/railway.json`
   - Add a **volume** mounted at `/var/lib/mysql`
   - **Do not** generate a domain and **do not** enable a TCP proxy. The database must stay private.
3. Service **`bookstack`**:
   - Root directory: `/bookstack`
   - Config-as-code file: `/bookstack/railway.json`
   - Add a **volume** mounted at `/config` (uploads, images, logs)
   - Networking → Generate domain (or add a custom domain), target port **80**

## 2. Variables

Generate secrets locally first: `sh scripts/gen-secrets.sh`. Paste them into the variables below and nowhere else.

**`db`**
| Variable | Value |
|---|---|
| `MARIADB_DATABASE` | `bookstack` |
| `MARIADB_USER` | `bookstack` |
| `MARIADB_PASSWORD` | *DB_PASSWORD from gen-secrets* |
| `MARIADB_ROOT_PASSWORD` | *DB_ROOT_PASSWORD from gen-secrets* |
| `TZ` | `Etc/UTC` |

**`bookstack`**
| Variable | Value |
|---|---|
| `PORT` | `80` (Railway routes and health-checks this port) |
| `PUID` / `PGID` | `1000` / `1000` |
| `APP_URL` | `https://${{RAILWAY_PUBLIC_DOMAIN}}` (or your custom domain, no trailing slash) |
| `APP_KEY` | *APP_KEY from gen-secrets* |
| `DB_HOST` | `${{db.RAILWAY_PRIVATE_DOMAIN}}` |
| `DB_PORT` | `3306` |
| `DB_DATABASE` | `${{db.MARIADB_DATABASE}}` |
| `DB_USERNAME` | `${{db.MARIADB_USER}}` |
| `DB_PASSWORD` | `${{db.MARIADB_PASSWORD}}` |
| `SESSION_SECURE_COOKIE` | `true` |
| `APP_PROXIES` | `*` (the container is only reachable via Railway's edge proxy) |
| `ALLOW_CONTENT_SCRIPTS` | `false` |
| `ALLOWED_IFRAME_SOURCES` | *(empty, or only hosts you trust)* |
| `API_REQUESTS_PER_MIN` | `120` |
| `MAIL_DRIVER` | `smtp` |
| `MAIL_HOST` / `MAIL_PORT` | your SMTP provider (e.g. port `587`) |
| `MAIL_ENCRYPTION` | `tls` |
| `MAIL_USERNAME` / `MAIL_PASSWORD` | SMTP credentials |
| `MAIL_FROM` / `MAIL_FROM_NAME` | sender address / name |
| `TZ` | `Etc/UTC` |

> **SMTP on Railway:** outbound SMTP is only allowed on the Pro plan.
> On lower plans, password-reset and notification emails will not send. MFA
> through an authenticator app (TOTP) still works without email.

`APP_KEY` encrypts sensitive data such as MFA secrets. **Never rotate it on a
running instance**, and keep a copy in your password manager. Without it, a
backup cannot be fully restored.

## 3. First boot (do this immediately)

Install the Railway CLI, then link it to the project: `railway link`.

```sh
# 1. Replace the built-in admin@admin.com / password account.
#    Prints a one-time generated password.
sh scripts/init-admin.sh you@example.com "Your Name" railway

# 2. Confirm the default credentials no longer work.
sh scripts/check-default-login.sh https://<your-bookstack-domain>
```

Then work through [HARDENING.md](HARDENING.md).

## 4. Updates

Renovate opens PRs that bump the pinned image tag and digest. Read the
[BookStack release notes](https://www.bookstackapp.com/blog/) and merge.
Railway redeploys only the service whose folder changed (`watchPatterns`).
BookStack runs its database migrations automatically on start.
