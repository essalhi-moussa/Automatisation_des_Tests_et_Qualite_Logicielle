#!/usr/bin/env bash
# Lance le plan de charge JMeter en mode CLI et genere le tableau de bord HTML.
#
# Usage : scripts/run-jmeter.sh [nom_du_run]
# Variables (valeurs par defaut) :
#   USERS=50  RAMPUP=10  LOOPS=10
#   PROTOCOL=https  HOST=reqres.in  PORT=443  API_KEY=reqres-free-v1
#   JMETER_BIN=jmeter   (chemin du binaire si jmeter n'est pas dans le PATH)
#
# Exemple contre le mock local :
#   PROTOCOL=http HOST=localhost PORT=3999 scripts/run-jmeter.sh mock
set -euo pipefail

RUN_NAME="${1:-reqres}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/reports/perf/$RUN_NAME"
JMETER_BIN="${JMETER_BIN:-jmeter}"

USERS="${USERS:-50}"
RAMPUP="${RAMPUP:-10}"
LOOPS="${LOOPS:-10}"
PROTOCOL="${PROTOCOL:-https}"
HOST="${HOST:-reqres.in}"
PORT="${PORT:-443}"
API_KEY="${API_KEY:-${REQRES_API_KEY:-reqres-free-v1}}"

rm -rf "$OUT"
mkdir -p "$OUT"

echo "JMeter : $USERS utilisateurs, montee en charge ${RAMPUP}s, $LOOPS boucles -> $PROTOCOL://$HOST:$PORT"
cd "$ROOT"
"$JMETER_BIN" -n \
  -t jmeter/reqres-load-test.jmx \
  -l "$OUT/resultats.jtl" \
  -j "$OUT/jmeter.log" \
  -e -o "$OUT/dashboard" \
  -Jusers="$USERS" -Jrampup="$RAMPUP" -Jloops="$LOOPS" \
  -Jprotocol="$PROTOCOL" -Jhost="$HOST" -Jport="$PORT" -Japikey="$API_KEY" \
  -Jjmeter.save.saveservice.output_format=csv \
  -Jjmeter.save.saveservice.response_data.on_error=false

echo "Tableau de bord : $OUT/dashboard/index.html"
