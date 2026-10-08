#!/usr/bin/env bash
# Choisit la cible des tests API en CI et exporte API_URL. A sourcer : `. scripts/ci-select-api.sh [requetes_necessaires]`
#
# API_MODE=real : toujours Reqres (API_BASE_URL)
# API_MODE=mock : toujours le mock local (mock/reqres-mock.js)
# API_MODE=auto (defaut) : une requete de controle sur Reqres ; si elle renvoie autre chose que 200 (429, quota
#   journalier epuise, reseau) ou si le quota restant (X-Ratelimit-Remaining) est inferieur au besoin, bascule sur le mock.
# La decision est ecrite dans reports/api/cible-api.txt et dans le journal du job : rien n'est masque.

NEEDED="${1:-20}"
MODE="${API_MODE:-auto}"
REAL_URL="${API_BASE_URL:-https://reqres.in}"
KEY="${REQRES_API_KEY:-reqres-free-v1}"
mkdir -p reports/api

ensure_cmd() {
  command -v "$1" >/dev/null 2>&1 && return 0
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq >/dev/null && apt-get install -y -qq --no-install-recommends "$2" >/dev/null
  fi
}

start_mock() {
  ensure_cmd node nodejs
  node mock/reqres-mock.js 3999 > reports/api/mock.log 2>&1 &
  for _ in $(seq 1 20); do
    curl -s -o /dev/null "http://localhost:3999/api/users/2" && break
    sleep 1
  done
  API_URL="http://localhost:3999"
}

ensure_cmd curl curl
REASON=""
case "$MODE" in
  real) API_URL="$REAL_URL"; REASON="API_MODE=real" ;;
  mock) start_mock; REASON="API_MODE=mock" ;;
  *)
    HEADERS="$(curl -s -D - -o /dev/null -m 20 -H "x-api-key: $KEY" "$REAL_URL/api/users/2")"
    CODE="$(printf '%s' "$HEADERS" | head -1 | awk '{print $2}')"
    REMAINING="$(printf '%s' "$HEADERS" | tr -d '\r' | awk -F': ' 'tolower($1)=="x-ratelimit-remaining"{print $2}')"
    if [ "$CODE" = "200" ] && { [ -z "$REMAINING" ] || [ "$REMAINING" -ge "$NEEDED" ]; }; then
      API_URL="$REAL_URL"
      REASON="controle HTTP $CODE, quota restant ${REMAINING:-inconnu}"
    else
      start_mock
      REASON="Reqres indisponible pour ce run (HTTP ${CODE:-aucune reponse}, quota restant ${REMAINING:-inconnu}, besoin $NEEDED)"
    fi
    ;;
esac

echo "Cible API : $API_URL ($REASON)" | tee reports/api/cible-api.txt
export API_URL
