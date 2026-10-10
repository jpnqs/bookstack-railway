#!/usr/bin/env sh
# Fails (exit 1) if BookStack still accepts the built-in default credentials
# admin@admin.com / password. Use after every deploy and in CI.
#
#   ./scripts/check-default-login.sh https://bookstack.example.com
set -eu

base="${1:?usage: check-default-login.sh <base-url>}"
base="${base%/}"
jar="$(mktemp)"
trap 'rm -f "$jar"' EXIT

token="$(curl -fsS -c "$jar" -b "$jar" "$base/login" \
  | grep -o 'name="_token" value="[^"]*"' | head -n1 | sed 's/.*value="//; s/"$//')"
[ -n "$token" ] || { echo "ERROR: could not read CSRF token from $base/login" >&2; exit 2; }

# A failed login redirects back to /login; a successful one goes elsewhere.
location="$(curl -sS -o /dev/null -w '%{redirect_url}' -c "$jar" -b "$jar" \
  --data-urlencode "_token=$token" \
  --data-urlencode "email=admin@admin.com" \
  --data-urlencode "password=password" \
  "$base/login")"

case "$location" in
  */login) echo "OK: default admin credentials are rejected." ;;
  *)       echo "FAIL: default admin credentials still work at $base (redirect: $location)" >&2; exit 1 ;;
esac
