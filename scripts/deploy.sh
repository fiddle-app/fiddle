#!/usr/bin/env bash
set -euo pipefail

APP=${1:-}
if [[ -z "$APP" ]]; then
  echo "Usage: deploy.sh <app-dir>"
  echo "  e.g. deploy.sh ear-tuner"
  exit 1
fi

# Map source dir → hosting repo name
case "$APP" in
  ear-tuner)    REPO="ear" ;;
  microbreaker) REPO="practice" ;;
  *)            echo "Unknown app: $APP"; exit 1 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/../$APP"
DEST="/c/Builds/fiddle/$REPO"
GIT_TMP="/tmp/deploy-git-$$"

echo "Deploying $APP → fiddle-app.github.io/$REPO"

# Stash the builds repo's .git so the copy doesn't clobber it
mv "$DEST/.git" "$GIT_TMP"

# Clear dest and copy source
rm -rf "$DEST"
mkdir -p "$DEST"
cp -r "$SRC/." "$DEST/"

# Restore builds repo's .git
rm -rf "$DEST/.git"
mv "$GIT_TMP" "$DEST/.git"

# Remove dev-only files from dest
rm -rf "$DEST/backlog" "$DEST/research" "$DEST/spec" "$DEST/specs" \
       "$DEST/handoffs" "$DEST/node_modules" "$DEST/scripts" "$DEST/log"
find "$DEST" -maxdepth 1 -name "*.md" -delete
find "$DEST" -name "*.svg" -delete
rm -f "$DEST/package.json" "$DEST/package-lock.json" "$DEST/.npmrc"

# Enforce LF line endings in the hosted repo
printf '* text=auto eol=lf\n' > "$DEST/.gitattributes"

cd "$DEST"
git add -A

if git diff --cached --quiet; then
  echo "Nothing to commit — already up to date."
else
  git commit -m "Deploy $(date '+%Y-%m-%d %H:%M')"
  git push
  echo "Done. Live at: https://fiddle-app.github.io/$REPO/"
fi
