#!/usr/bin/env sh
# Prints freshly generated secrets in .env format.
#   Local:   ./scripts/gen-secrets.sh >> .env
#   Railway: run once, paste the values into the service variables.
set -eu

rand_b64() { openssl rand -base64 "$1" | tr -d '\n'; }
rand_pw()  { openssl rand -base64 48 | tr -d '\n/+=' | cut -c1-40; }

echo "APP_KEY=base64:$(rand_b64 32)"
echo "DB_PASSWORD=$(rand_pw)"
echo "DB_ROOT_PASSWORD=$(rand_pw)"
