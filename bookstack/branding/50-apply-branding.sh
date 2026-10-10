#!/usr/bin/with-contenv bash
# linuxserver custom init hook: runs after DB migrations, before nginx/php-fpm
# start. Runs as the app user so cache files keep the right owner.
# A failure here is logged but does not stop the container from booting.
s6-setuidgid abc php /app/branding/apply-branding.php || echo "[branding] failed, continuing"
