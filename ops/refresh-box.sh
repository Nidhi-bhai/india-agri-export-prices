#!/bin/bash
# Weekly refresh run from the box (until the GitHub Actions workflow in ops/refresh.yml is enabled).
set -e
cd /workspace/iaep
git pull -q --rebase || true
python3 scripts/fetch.py && python3 scripts/build.py
git add docs && (git commit -qm "weekly snapshot $(date +%F)" && git push -q) || true
python3 scripts/indexnow.py || true
