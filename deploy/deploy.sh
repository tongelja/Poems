#!/bin/bash
# Copy Poems to the Pi and (re)start it.  Usage: deploy/deploy.sh [user@host]
set -euo pipefail

HOST="${1:-pi@pi-hole}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

rsync -az --delete \
    --exclude .git --exclude .venv --exclude __pycache__ --exclude '*.pdf' \
    "$REPO/" "$HOST:Poems/"

ssh "$HOST" bash -s <<'REMOTE'
set -euo pipefail
if [ ! -x ~/.local/bin/uv ]; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
cd ~/Poems
~/.local/bin/uv sync --frozen --no-dev
sudo cp deploy/poems.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable poems
sudo systemctl restart poems
sleep 3
systemctl is-active poems
REMOTE
