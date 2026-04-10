#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

NAMESPACE="team05"
OVERLAY="k8s/overlays/dev"

usage() {
  cat <<'EOF'
Usage: scripts/k8s-dev-up.sh [--port-forward] [--skip-rollout] [--secret-file <path>]

Options:
  --port-forward   Start port-forward to frontend service on localhost:8080
  --skip-rollout   Skip rollout status checks
  --secret-file    Path to env file containing required secrets (default: .env.k8s.dev)
EOF
}

PORT_FORWARD=false
SKIP_ROLLOUT=false
SECRET_FILE=".env.k8s.dev"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port-forward)
      PORT_FORWARD=true
      shift
      ;;
    --skip-rollout)
      SKIP_ROLLOUT=true
      shift
      ;;
    --secret-file)
      if [[ $# -lt 2 ]]; then
        echo "--secret-file requires a value" >&2
        usage
        exit 1
      fi
      SECRET_FILE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

require_var() {
  local var_name="$1"
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required variable: ${var_name}" >&2
    exit 1
  fi
}

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is not installed or not in PATH" >&2
  exit 1
fi

echo "[1/5] Checking Kubernetes connectivity..."
kubectl cluster-info >/dev/null

echo "[2/5] Ensuring namespace and app secret..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

if [[ -f "$SECRET_FILE" ]]; then
  echo "Loading secrets from ${SECRET_FILE}"
  # Export sourced variables so kubectl receives them.
  set -a
  # shellcheck disable=SC1090
  source "$SECRET_FILE"
  set +a
fi

require_var SECRET_KEY
require_var DB_PASSWORD
require_var JWT_SECRET
require_var AES_KEY
require_var AES_IV

kubectl create secret generic app-secrets \
  -n "$NAMESPACE" \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  --from-literal=DB_PASSWORD="$DB_PASSWORD" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=AES_KEY="$AES_KEY" \
  --from-literal=AES_IV="$AES_IV" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "[3/5] Applying dev overlay..."
kubectl apply -k "$OVERLAY"

echo "[4/5] Current pods in ${NAMESPACE}:"
kubectl get pods -n "$NAMESPACE"

echo "[5/5] Current services in ${NAMESPACE}:"
kubectl get svc -n "$NAMESPACE"

if [[ "$SKIP_ROLLOUT" == "false" ]]; then
  echo "Checking rollout status..."
  kubectl rollout status deployment/postgres -n "$NAMESPACE" --timeout=180s
  kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout=180s
  kubectl rollout status deployment/frontend -n "$NAMESPACE" --timeout=180s
fi

echo "Done."
echo "To test immediately without ingress:"
echo "  kubectl port-forward svc/frontend 8080:80 -n ${NAMESPACE}"

if [[ "$PORT_FORWARD" == "true" ]]; then
  echo "Starting port-forward on http://localhost:8080 ..."
  kubectl port-forward svc/frontend 8080:80 -n "$NAMESPACE"
fi
