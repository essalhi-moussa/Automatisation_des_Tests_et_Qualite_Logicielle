#!/usr/bin/env bash
# Notification optionnelle de fin de pipeline vers Slack ou Discord.
# Les URL de webhook sont des variables CI masquees : SLACK_WEBHOOK_URL / DISCORD_WEBHOOK_URL.
# Usage : scripts/notify-webhook.sh <success|failed>
set -uo pipefail

STATUS="${1:-unknown}"
PROJECT="${CI_PROJECT_NAME:-qa-automation}"
BRANCH="${CI_COMMIT_REF_NAME:-local}"
URL="${CI_PIPELINE_URL:-}"
PAGES="${CI_PAGES_URL:+Rapport Allure : ${CI_PAGES_URL}}"
MSG="Pipeline ${STATUS} - ${PROJECT} (${BRANCH}) ${URL} ${PAGES}"

if [ -z "${SLACK_WEBHOOK_URL:-}" ] && [ -z "${DISCORD_WEBHOOK_URL:-}" ]; then
  echo "Aucun webhook configure (SLACK_WEBHOOK_URL / DISCORD_WEBHOOK_URL) : notification ignoree."
  exit 0
fi

if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
  curl -fsS -X POST -H 'Content-type: application/json' --data "{\"text\":\"${MSG}\"}" "$SLACK_WEBHOOK_URL" \
    && echo "Notification Slack envoyee." || echo "Echec de la notification Slack."
fi
if [ -n "${DISCORD_WEBHOOK_URL:-}" ]; then
  curl -fsS -X POST -H 'Content-type: application/json' --data "{\"content\":\"${MSG}\"}" "$DISCORD_WEBHOOK_URL" \
    && echo "Notification Discord envoyee." || echo "Echec de la notification Discord."
fi
exit 0
