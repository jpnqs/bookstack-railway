#!/usr/bin/env sh
# Replaces BookStack's built-in default admin (admin@admin.com / password)
# with your own email and a generated password. Run once per environment,
# immediately after the first boot.
#
#   Local:   ./scripts/init-admin.sh you@example.com "Your Name"
#   Railway: ./scripts/init-admin.sh you@example.com "Your Name" railway
#            (needs the Railway CLI, linked to the project; runs via `railway ssh`)
#
# The generated password is printed once. Log in, change it, then enable MFA.
set -eu

email="${1:?usage: init-admin.sh <email> <name> [local|railway]}"
name="${2:?usage: init-admin.sh <email> <name> [local|railway]}"
target="${3:-local}"

# Stop Git Bash on Windows from rewriting container paths.
export MSYS_NO_PATHCONV=1

# Arguments are passed as separate argv entries (no shell string), so names
# with quotes or spaces cannot alter the command.
set -- php /app/www/artisan bookstack:create-admin --initial \
  "--email=$email" "--name=$name" --generate-password

case "$target" in
  local)   docker compose exec -T bookstack "$@" ;;
  railway) railway ssh --service bookstack -- "$@" ;;
  *)       echo "unknown target: $target" >&2; exit 2 ;;
esac
