#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="team05"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is not installed or not in PATH" >&2
  exit 1
fi

echo "Namespace: ${NAMESPACE}"
kubectl get pods -n "$NAMESPACE" -o wide
kubectl get svc -n "$NAMESPACE"
kubectl get ingress -n "$NAMESPACE" || true
