#!/usr/bin/env bash
# Execute une suite Maven (ui | api | smoke | external), genere le rapport Allure (fichier unique,
# consultable hors ligne) et archive un resume TestNG dans reports/.
#
# Usage : scripts/run-suite.sh <ui|api|smoke|external> [nom_du_run] [options Maven...]
# Exemple : scripts/run-suite.sh api mock -Dapi.base.url=http://localhost:3999
set -uo pipefail

SUITE="${1:?suite attendue : ui | api | smoke | external}"
NAME="${2:-local}"
shift 2 2>/dev/null || shift $#
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

case "$SUITE" in
  ui|external|smoke) GROUP="ui" ;;
  api) GROUP="api" ;;
  *) echo "Suite inconnue : $SUITE"; exit 2 ;;
esac
OUT="reports/$GROUP/allure-$NAME"

rm -rf target/allure-results target/surefire-reports
mvn -B -ntp -P "$SUITE" test "$@"
RC=$?

mkdir -p "reports/$GROUP"
rm -rf "$OUT"
if command -v allure >/dev/null 2>&1; then
  allure generate target/allure-results --clean --single-file -o "$OUT" >/dev/null && echo "Rapport Allure : $OUT/index.html"
else
  echo "Allure CLI absent (npm i -g allure-commandline) : rapport non genere"
fi
cp target/surefire-reports/testng-results.xml "reports/$GROUP/testng-results-$NAME.xml" 2>/dev/null || true
exit $RC
