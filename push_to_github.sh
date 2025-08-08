#!/bin/bash
set -e
BRANCH=${1:-main}
MSG=${2:-"Automated update from ChatGPT"}
git config user.name  "DeityTradePro Bot"
git config user.email "bot@deitytradepro.local"
git remote set-url origin https://$GITHUB_TOKEN@github.com/primetime318/Deitytradeprobot.git

# Pull latest changes first
git fetch origin $BRANCH
git merge origin/$BRANCH --no-edit || true

# Add and commit
git add -A
git commit -m "$MSG" || echo "Nothing to commit."
git push origin "$BRANCH"