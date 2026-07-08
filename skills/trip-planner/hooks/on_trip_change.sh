#!/usr/bin/env bash
# Rebuild trip outputs when a trip bundle changes. Idempotent + cheap (no AI).
set -euo pipefail
ROOT="${CLAUDE_PROJECT_DIR:-.}"
SK="$ROOT/.claude/skills/trip-planner/scripts"
[ -d "$SK" ] || SK="$(dirname "$0")/../scripts"
# Look for a bundle named *trip*.bundle.json or bundle.json at project root
for B in "$ROOT"/*bundle*.json "$ROOT"/trip.bundle.json; do
  [ -f "$B" ] || continue
  OUT="${B%.json}"
  python3 "$SK/generate_workbook.py" "$B" "${OUT}.xlsx" >/dev/null 2>&1 && echo "[trip-planner] rebuilt ${OUT}.xlsx"
  python3 "$SK/generate_brochure.py" "$B" "${OUT}.html" >/dev/null 2>&1 && echo "[trip-planner] rebuilt ${OUT}.html"
done
