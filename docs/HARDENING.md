# Post-install hardening checklist

Work through this list after every new environment is created (local, staging, production).

## Accounts and login
- [ ] Default admin replaced (`scripts/init-admin.sh`) and `scripts/check-default-login.sh` passes.
- [ ] Logged in with the generated password and changed it to a password-manager value.
- [ ] **MFA set up** for your own admin account (My Account → Multi-Factor Authentication).
- [ ] **MFA enforced on roles**: Settings → Roles → *Admin* (and every role with
      settings, user or permission management) → "Requires Multi-Factor Authentication".
- [ ] Registration disabled: Settings → Registration → "Allow registration" **off**.
- [ ] Default role for new users is a low-privilege role (Viewer).
- [ ] "Allow public access" **off** (Settings → Features & Security), unless intended.

## API access (needed by the MCP server later)
- [ ] "Access System API" is granted **only** to dedicated bot roles, not to Admin or Editor.
- [ ] One bot user per AI client, each with its own token, restricted to the
      shelves/books it needs. Writes are limited to the "AI Inbox" book.
- [ ] Token expiry dates are set. Tokens are stored only in Railway variables or a password manager.

## Platform
- [ ] `db` service has **no** public domain and **no** TCP proxy.
- [ ] `SESSION_SECURE_COOKIE=true` and `APP_URL` uses `https://`.
- [ ] `ALLOW_CONTENT_SCRIPTS=false`, and `ALLOWED_IFRAME_SOURCES` contains only trusted hosts.
- [ ] `APP_KEY` is backed up in a password manager.
- [ ] Railway project members are reviewed, and 2FA is enabled on every Railway and GitHub account with access.
- [ ] GitHub: branch protection on `main`, CI required, and secret scanning and Dependabot alerts enabled.

## Ongoing
- [ ] Renovate PRs are reviewed within a week. BookStack security releases are applied the same day.
- [ ] Settings → Audit Log is reviewed regularly, especially for bot users.
- [ ] Backups are taken and restore-tested (see the open item in the README).
