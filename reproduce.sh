#!/usr/bin/env bash
# Reproduce submission.csv from the pinned challenge inputs (see README.md, "Reproduce").
# Snapshot location: $INVOICE_SNAPSHOT, else ../majedzahrani3/invoice-auditing-level-2 (source/SNAPSHOT.md).
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python}
$PY tools/snapshot.py verify                 # the inputs are the pinned commit, file by file
$PY -m audit.build --quiet                   # evidence: claims, site records, daily drilling reports
$PY -m audit.g3_run                          # each line priced and checked on its own
$PY -m audit.g4_run                          # cross-invoice state: bands, limits, duplicates, footage, A3, retention
$PY -m audit.g5_run                          # one outcome per invoice; verification/g5/submission.csv
cp verification/g5/submission.csv submission.csv
$PY tools/check_submission.py submission.csv # independent format and coverage check against the template and inputs
git diff --stat --exit-code -- submission.csv verification/ && echo "REPRODUCED: committed outputs unchanged"
