#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${HERE%/scripts}"

cd "$ROOT/test_sites"
echo "Serving test_sites on http://localhost:8000"
echo "- Landing:      http://localhost:8000/landing_static/"
echo "- SPA Tasks:    http://localhost:8000/spa_tasks/"
echo "- Shop (SW):    http://localhost:8000/shop_multipage/"
python -m http.server 8000

