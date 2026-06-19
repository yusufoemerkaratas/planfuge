#!/bin/sh
set -eu

python scripts/bootstrap_candidates.py
exec "$@"
