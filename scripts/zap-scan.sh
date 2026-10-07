#!/usr/bin/env bash
# Scan de securite OWASP ZAP de l'application Formy.
#
# Mode par defaut : image Docker officielle (ghcr.io/zaproxy/zaproxy:stable), zap-baseline.py
#   = spider + analyse PASSIVE uniquement (aucune attaque active sur le site tiers).
# Mode complet (optionnel, a n'utiliser que sur une cible dont vous etes proprietaire) :
#   ZAP_MODE=full scripts/zap-scan.sh      -> zap-full-scan.py (analyse active)
# Mode local sans Docker (ZAP installe, Java requis) :
#   ZAP_HOME=/chemin/vers/ZAP_2.17.0 scripts/zap-scan.sh
#
# Rapports produits dans reports/security/ : zap-<mode>.html, zap-<mode>.json, zap-<mode>.md
set -uo pipefail

TARGET="${TARGET_URL:-https://formy-project.herokuapp.com}"
MODE="${ZAP_MODE:-baseline}"
IMAGE="${ZAP_IMAGE:-ghcr.io/zaproxy/zaproxy:stable}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/reports/security"
mkdir -p "$OUT"
chmod 777 "$OUT" 2>/dev/null || true

if [ -n "${ZAP_HOME:-}" ]; then
  echo "ZAP local ($ZAP_HOME) -> plan d'automatisation scripts/zap-baseline-plan.yaml"
  PLAN_TMP="$OUT/.plan.yaml"
  sed -e "s#__TARGET__#${TARGET}#g" -e "s#__OUT__#${OUT}#g" "$ROOT/scripts/zap-baseline-plan.yaml" > "$PLAN_TMP"
  "$ZAP_HOME/zap.sh" -cmd -silent -autorun "$PLAN_TMP"
  rc=$?
  rm -f "$PLAN_TMP"
else
  case "$MODE" in
    full)     SCRIPT="zap-full-scan.py" ;;
    baseline) SCRIPT="zap-baseline.py" ;;
    *) echo "ZAP_MODE inconnu : $MODE (baseline|full)"; exit 2 ;;
  esac
  echo "ZAP $MODE sur $TARGET (image $IMAGE)"
  # -I : ne pas echouer sur des alertes (code 1/2) afin de toujours produire les rapports
  docker run --rm -v "$OUT:/zap/wrk:rw" -t "$IMAGE" "$SCRIPT" \
    -t "$TARGET" \
    -r "zap-$MODE.html" -J "zap-$MODE.json" -w "zap-$MODE.md" -I
  rc=$?
fi

echo "Rapports : $OUT"
exit "$rc"
