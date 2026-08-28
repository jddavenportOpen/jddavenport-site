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
    -h|--help)     sed -n '2,27p' "$0"; exit 0 ;;
    *) echo "deploy.sh: unknown flag '$arg'" >&2; exit 2 ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "deploy.sh: git not found on PATH" >&2
  exit 1
fi

SHA="$(git rev-parse HEAD)"
SHORT="$(git rev-parse --short HEAD)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
NOW="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

DIRTY="$(git status --porcelain -- . ':(exclude)version.json' | head -c 1 || true)"
if [[ -n "$DIRTY" && "$ALLOW_DIRTY" -eq 0 ]]; then
  echo "deploy.sh: working tree is dirty. version.json would name a commit that" >&2
  echo "           is not what gets uploaded, and the done-gate would certify it." >&2
  echo "           Commit first, or pass --allow-dirty if you mean it." >&2
  git status --short -- . ':(exclude)version.json' >&2
  exit 3
fi

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

vercel --prod
