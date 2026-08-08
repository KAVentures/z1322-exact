#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./verify_release.sh
python3 verify_all.py --verify-dependency --report reports/full_fresh_verification_report.json
printf '%s\n' 'DEPENDENCY-COMPLETE VERIFICATION PASSED'
