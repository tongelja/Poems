#!/bin/bash
# Pull the latest from GitHub. Run on the Pi by poems-pull.timer every few minutes.
# poems.adoc changes show up on their own (the site re-reads the file).
# Any other change (code, templates, dependencies) restarts the site.
set -euo pipefail
cd "$(dirname "$0")/.."

git fetch --quiet origin master
before=$(git rev-parse HEAD)
after=$(git rev-parse origin/master)
[ "$before" = "$after" ] && exit 0

git merge --quiet --ff-only origin/master
echo "Updated $before -> $after"

if git diff --name-only "$before" "$after" | grep -qv '^poems\.adoc$'; then
    ~/.local/bin/uv sync --frozen --no-dev
    sudo cp deploy/poems.service deploy/poems-pull.service deploy/poems-pull.timer /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl restart poems
    echo "Restarted the site"
fi
