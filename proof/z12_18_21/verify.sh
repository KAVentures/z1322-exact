#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
JOBS="${JOBS:-5}"
if command -v sha256sum >/dev/null 2>&1; then
    sha256sum -c --quiet SHA256SUMS.txt
elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 -c SHA256SUMS.txt >/dev/null
else
    printf '%s\n' 'ERROR: neither sha256sum nor shasum is available' >&2
    exit 1
fi
python3 verify_all_exact.py --root . --jobs "$JOBS" --report reproduced_verification_report.json
python3 compare_report.py reports/reference_verification_report.json reproduced_verification_report.json
python3 mutation_tests.py
printf '%s\n' 'PACKAGE VERIFICATION PASSED'
