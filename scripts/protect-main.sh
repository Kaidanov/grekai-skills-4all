#!/usr/bin/env bash
# One-shot: protect `main` + enable auto-merge for grekai-skills-4all.
# Run locally where `gh` is authenticated:  bash scripts/protect-main.sh
set -euo pipefail

REPO="Kaidanov/grekai-skills-4all"
BRANCH="main"

echo "==> 1/3  Enabling repo-level auto-merge + squash + branch auto-delete"
gh api -X PATCH "repos/$REPO" \
  -F allow_auto_merge=true \
  -F allow_squash_merge=true \
  -F delete_branch_on_merge=true >/dev/null

echo "==> 2/3  Detecting the Vercel status-check name on $BRANCH"
CHECK="$(
  { gh api "repos/$REPO/commits/$BRANCH/status"      --jq '.statuses[].context' 2>/dev/null
    gh api "repos/$REPO/commits/$BRANCH/check-runs"   --jq '.check_runs[].name'  2>/dev/null; } \
  | grep -i vercel | head -n1 || true
)"
if [ -n "$CHECK" ]; then
  echo "    found required check: \"$CHECK\""
  CONTEXTS="[\"$CHECK\"]"
else
  echo "    no Vercel check found yet — protecting with PR requirement only (no required status check)"
  CONTEXTS="[]"
fi

echo "==> 3/3  Protecting $BRANCH (require PR, require Vercel check, NO required reviews, enforce for admins)"
gh api -X PUT "repos/$REPO/branches/$BRANCH/protection" \
  --input - <<JSON >/dev/null
{
  "required_status_checks": { "strict": true, "contexts": $CONTEXTS },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON

echo "==> Done. main is protected; PRs auto-merge once the Vercel check is green."
