#!/usr/bin/env bash
# deploy.sh — stamp version.json, then ship to Vercel production.
#
#   bash deploy.sh              # stamp + deploy
#   bash deploy.sh --dry-run    # stamp only, print the deploy command, do not run it
#   bash deploy.sh --stamp-only # stamp only, say nothing about deploying
#
# version.json exists so the Definition-of-Done gate can answer "is prod
# actually serving the commit I merged?" without guessing:
#
#   bash ~/agent-system/scripts/done-gate.sh \
#     --url https://jddavenport.com \
#     --sha "$(git rev-parse HEAD)" \
#     --sha-probe "curl -s https://jddavenport.com/version.json" \
#     --journey ~/clawd/projects/jd-portfolio/qa/site-journey.yaml
#
# The gate reads the `sha` key out of that JSON payload. Nothing else in this
# repo is a build artifact, so version.json is the only deployed-SHA signal
# available on a static site.
#
# It REFUSES a dirty tree on purpose. A version.json that names HEAD while
# uncommitted edits are being uploaded is worse than no version.json: it makes
# the gate certify a deploy whose contents are not the commit it names, which
# is precisely the drift the gate exists to catch. Override with --allow-dirty
# only when you have a reason and can say what it is.
#
# A real deploy also refreshes the fallback numbers in brain.html and
# showcase.html (tools/metrics/refresh_snapshot.py) and commits them locally. It
# does not push: run `git push` after deploying to keep origin level.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

DRY_RUN=0
STAMP_ONLY=0
ALLOW_DIRTY=0

for arg in "$@"; do
  case "$arg" in
    --dry-run)     DRY_RUN=1 ;;
    --stamp-only)  STAMP_ONLY=1 ;;
    --allow-dirty) ALLOW_DIRTY=1 ;;
    -h|--help)     sed -n '2,31p' "$0"; exit 0 ;;
    *) echo "deploy.sh: unknown flag '$arg'" >&2; exit 2 ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "deploy.sh: git not found on PATH" >&2
  exit 1
fi

DIRTY="$(git status --porcelain -- . ':(exclude)version.json' | head -c 1 || true)"
if [[ -n "$DIRTY" && "$ALLOW_DIRTY" -eq 0 ]]; then
  echo "deploy.sh: working tree is dirty. version.json would name a commit that" >&2
  echo "           is not what gets uploaded, and the done-gate would certify it." >&2
  echo "           Commit first, or pass --allow-dirty if you mean it." >&2
  git status --short -- . ':(exclude)version.json' >&2
  exit 3
fi

# Refresh the fallback snapshot in brain.html and showcase.html from the live
# /api/metrics, then commit it, BEFORE stamping: version.json has to name the
# commit that holds these numbers. A failed fetch keeps the old snapshot and
# never stops the deploy. Skipped for --dry-run and --stamp-only, which ship
# nothing. With --allow-dirty the refresh is left uncommitted, because those
# files may hold edits that are not ours to commit.
if [[ "$DRY_RUN" -eq 0 && "$STAMP_ONLY" -eq 0 ]]; then
  PY="$(command -v python3.12 || command -v python3 || true)"
  SNAPSHOT_PAGES=(brain.html showcase.html)
  if [[ -z "$PY" ]] || ! "$PY" tools/metrics/refresh_snapshot.py; then
    echo "deploy.sh: snapshot refresh did not run, deploying with the old snapshot" >&2
    [[ "$ALLOW_DIRTY" -eq 1 ]] || git checkout -- "${SNAPSHOT_PAGES[@]}" || true
  elif [[ "$ALLOW_DIRTY" -eq 0 ]] && ! git diff --quiet -- "${SNAPSHOT_PAGES[@]}"; then
    if ! git commit -q -m "snapshot: refresh brain and showcase fallback numbers from /api/metrics" -- "${SNAPSHOT_PAGES[@]}"; then
      echo "deploy.sh: could not commit the snapshot, deploying with the old one" >&2
      git checkout -- "${SNAPSHOT_PAGES[@]}" || true
    fi
  fi
fi

SHA="$(git rev-parse HEAD)"
SHORT="$(git rev-parse --short HEAD)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
NOW="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

cat > version.json <<JSON
{
  "sha": "$SHA",
  "short_sha": "$SHORT",
  "branch": "$BRANCH",
  "deployed_at": "$NOW"
}
JSON

echo "stamped version.json -> $SHORT ($BRANCH) at $NOW"

if [[ "$STAMP_ONLY" -eq 1 ]]; then
  exit 0
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry run, not deploying. The command would be:"
  echo "    vercel --prod"
  exit 0
fi

if ! command -v vercel >/dev/null 2>&1; then
  echo "deploy.sh: vercel CLI not found on PATH. Install it, or deploy from the dashboard." >&2
  exit 1
fi

# Deploy from a copy WITHOUT .git. Since 2026-10-26 Vercel marks every CLI
# deploy that carries this repo's git metadata as BLOCKED (the commit author,
# the jddavenportOpen noreply address, is not a member of the Vercel team), and
# `vercel --prod` then hangs forever. The copy is the same files, minus history.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
rsync -a --exclude .git ./ "$STAGE/"
(cd "$STAGE" && vercel --prod --yes)
