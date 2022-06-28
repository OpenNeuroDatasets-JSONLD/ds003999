#!/bin/bash

set -euo pipefail

bids-validator ./ --json --verbose | \
    jq '.issues.warnings[0].files[].file.path' | \
    sed 's/nii\.gz\"/json/; s/^\"//' | \
    xargs code/slice-timing_add.py
