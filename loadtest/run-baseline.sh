#!/usr/bin/env bash
# smoke -> load -> stress against nginx; console output lands in loadtest/results/. Needs k6 on the host.
set -u
cd "$(dirname "$0")"
BASE_URL="${BASE_URL:-http://localhost}"
ulimit -n 65535 2>/dev/null
mkdir -p results
for t in smoke load stress; do
  k6 run --quiet -e BASE_URL="$BASE_URL" --summary-trend-stats='med,p(95),p(99),max' "$t.js" > "results/$t.txt" 2>&1
  echo "$t exit=$?"
done
