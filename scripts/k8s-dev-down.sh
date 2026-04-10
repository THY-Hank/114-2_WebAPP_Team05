#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

NAMESPACE="team05"
OVERLAY="k8s/overlays/dev"
PURGE_SECRET=false

usage() {
  cat <<'EOF'
Usage: scripts/k8s-dev-down.sh [--purge-secret]

Options:
  --purge-secret   Also delete app-secrets from namespace
EOF
}

for arg in "$@"; do
  case "$arg" in
    --purge-secret) PURGE_SECRET=true ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is not installed or not in PATH" >&2
  exit 1
fi

echo "Deleting dev overlay resources..."
kubectl delete -k "$OVERLAY" --ignore-not-found=true

if [[ "$PURGE_SECRET" == "true" ]]; then
  echo "Deleting app secret..."
  kubectl delete secret app-secrets -n "$NAMESPACE" --ignore-not-found=true
fi

echo "Remaining resources in ${NAMESPACE}:"
kubectl get all -n "$NAMESPACE" || true
