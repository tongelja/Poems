#!/bin/bash
# Set up (or update) Poems on the Pi from GitHub.  Usage: deploy/deploy.sh [user@host]
# The Pi keeps a git checkout and pulls every 5 minutes on its own (deploy/pull.sh),
# so this is only needed the first time, or to apply a pushed change right away.
set -euo pipefail

HOST="${1:-pi@pi-hole}"
REPO_URL="https://github.com/tongelja/Poems.git"

if [ -n "$(git status --porcelain)" ] || [ -n "$(git log origin/master..HEAD 2>/dev/null)" ]; then
    echo "Note: the Pi deploys what is on GitHub; local uncommitted or unpushed changes are not included." >&2
fi

ssh "$HOST" REPO_URL="$REPO_URL" bash -s <<'REMOTE'
set -euo pipefail
if [ ! -x ~/.local/bin/uv ]; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
if [ ! -d ~/Poems/.git ]; then
    rm -rf ~/Poems
    git clone --quiet "$REPO_URL" ~/Poems
fi
cd ~/Poems
git fetch --quiet origin master
git merge --quiet --ff-only origin/master
~/.local/bin/uv sync --frozen --no-dev
sudo cp deploy/poems.service deploy/poems-pull.service deploy/poems-pull.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now poems-pull.timer
sudo systemctl enable poems
sudo systemctl restart poems
sleep 3
systemctl is-active poems
git log --oneline -1
REMOTE
