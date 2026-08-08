#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c MANIFEST.sha256
python3 verify_all.py --report reports/verification_report.json
python3 mutation_tests.py
python3 frontier_propagation.py
printf '%s\n' 'RELEASE VERIFICATION PASSED'
