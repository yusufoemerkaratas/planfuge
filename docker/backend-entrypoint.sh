#!/bin/sh
set -eu

runtime_root="${PLANFUGE_RUNTIME_ROOT:-/app}"
case "$runtime_root" in
    ""|"/")
        echo "Refusing to reset unsafe runtime root: $runtime_root" >&2
        exit 1
        ;;
esac

rm -rf -- "$runtime_root/data" "$runtime_root/outputs"
mkdir -p \
    "$runtime_root/data/config" \
    "$runtime_root/data/imports" \
    "$runtime_root/data/metadata" \
    "$runtime_root/data/pages" \
    "$runtime_root/outputs/candidates" \
    "$runtime_root/outputs/contract_exports" \
    "$runtime_root/outputs/crops" \
    "$runtime_root/outputs/debug" \
    "$runtime_root/outputs/exports" \
    "$runtime_root/outputs/overlays" \
    "$runtime_root/outputs/rendered" \
    "$runtime_root/outputs/reviews"

exec "$@"
