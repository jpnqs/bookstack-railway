# BookStack application image.
# Pinned by tag AND digest (multi-arch manifest). Renovate bumps both together.
FROM lscr.io/linuxserver/bookstack:v26.09.1-ls287@sha256:99cd1f5707c1911afad213adec5c9739763b76f843d1477142231834ecdcb6f7

# The linuxserver image listens on 80 (nginx) and stores app state
# (uploads, images, logs, generated .env) under /config. Do not add a
# VOLUME line: Railway rejects it; attach a Railway volume at /config instead.
EXPOSE 80
