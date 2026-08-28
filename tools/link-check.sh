#!/usr/bin/env bash
# link-check.sh — HTTP-status every external href in the served pages.
#
#   bash tools/link-check.sh              # index.html book.html teardown.html
#   bash tools/link-check.sh index.html   # just one
#
# Exits non-zero if any link returns >= 400 or fails to resolve, so it can gate
# a deploy. LinkedIn is expected to answer 999 to non-browser clients; that is
# a bot-block, not a broken link, and is reported as SKIP rather than failing
# the run. Click it by hand once per change to its slug.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

FILES=("$@")
if [[ ${#FILES[@]} -eq 0 ]]; then
  FILES=(index.html book.html teardown.html)
fi

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'

urls="$(grep -oE 'https?://[^"'"'"' <>)]+' "${FILES[@]}" \
  | sed 's/^[^:]*://' \
  | sed 's/[.,]$//' \
  | grep -v '^https\?://fonts\.\(googleapis\|gstatic\)\.com' \
  | grep -v '^https\?://schema\.org' \
  | grep -v '^https\?://www\.sitemaps\.org' \
  | grep -v '^https\?://jddavenport\.com' \
  | sort -u)"

fail=0
total=0
while IFS= read -r u; do
  [[ -z "$u" ]] && continue
  total=$((total + 1))
  code="$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 20 -A "$UA" "$u" || echo 000)"
  if [[ "$code" == "999" ]]; then
    printf 'SKIP %s  %s (bot-block, verify by hand)\n' "$code" "$u"
  elif [[ "$code" =~ ^[123] ]]; then
    printf 'ok   %s  %s\n' "$code" "$u"
  else
    printf 'FAIL %s  %s\n' "$code" "$u"
    fail=$((fail + 1))
  fi
done <<< "$urls"

echo
echo "checked $total external links, $fail failing"
exit $(( fail > 0 ? 1 : 0 ))
