#!/usr/bin/env bash
# Execute la collection Postman avec Newman (reporters cli, htmlextra, junit, json).
# Usage : scripts/run-newman.sh <public|mock> [options newman...]
set -uo pipefail
ENV_NAME="${1:?environnement attendu : public | mock}"
shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="reports/api/newman"
mkdir -p "$OUT"
newman run postman/Reqres.postman_collection.json \
  -e "postman/reqres-$ENV_NAME.postman_environment.json" \
  -r cli,htmlextra,junit,json \
  --reporter-htmlextra-export "$OUT/rapport-newman-$ENV_NAME.html" \
  --reporter-htmlextra-title "Reqres - Newman ($ENV_NAME)" \
  --reporter-junit-export "$OUT/newman-$ENV_NAME-junit.xml" \
  --reporter-json-export "$OUT/newman-$ENV_NAME.json" \
  "$@"
