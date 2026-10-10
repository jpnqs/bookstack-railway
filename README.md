# bookstack-railway

Hardened [BookStack](https://www.bookstackapp.com/) for Railway, with a
Docker Compose stack for local development and CI.

| Service | Image (pinned by tag + digest) | Local | Railway |
|---|---|---|---|
| `bookstack` | `linuxserver/bookstack:v26.09.1-ls287` | http://localhost:6875 | public HTTPS domain, volume `/config` |
| `db` | `mariadb:11.4.13` (LTS) | internal network only | private network only, volume `/var/lib/mysql` |
| `mailpit` | `axllent/mailpit:v1.31.4` | UI at http://localhost:8025 | not deployed |

## Local quick start

```sh
cp .env.example .env
sh scripts/gen-secrets.sh >> .env
docker compose up -d --build --wait

# Replace the built-in admin@admin.com / password account (prints a password).
sh scripts/init-admin.sh you@example.com "Your Name"
sh scripts/check-default-login.sh http://localhost:6875
```

Ports are bound to `127.0.0.1` only. Stop with `docker compose down`. Add `-v`
to also delete the data volumes.

## Deploy

See [docs/DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md), then work through
[docs/HARDENING.md](docs/HARDENING.md).

## Scripts

| Script | Purpose |
|---|---|
| `scripts/gen-secrets.sh` | Prints a new `APP_KEY` and DB passwords in `.env` format |
| `scripts/init-admin.sh` | Replaces the default admin (local or `railway`). A second run is a no-op that exits 2 |
| `scripts/check-default-login.sh` | Exits 1 if `admin@admin.com / password` still works |

## CI

`.github/workflows/ci.yml` builds and starts the stack, replaces the admin,
asserts the default login is rejected, and runs Trivy. It fails on fixable
CRITICAL vulnerabilities and runs again weekly. Renovate keeps image digests
and action SHAs current.

## Open items
- **Backups (M3):** Railway volumes cannot be shared between services, so a
  separate backup service can dump the database but cannot read BookStack's
  `/config` volume (uploads). The options are: move uploads to S3/R2
  (`STORAGE_TYPE=s3`) and back up only the DB, or run the backup inside the
  BookStack container.
