# Automatisation des tests et qualité logicielle (Module M11)

[![pipeline status](https://gitlab.com/essalhi-moussa-group/automatisation_des_tests_et_qualite_logicielle/badges/main/pipeline.svg)](https://gitlab.com/essalhi-moussa-group/automatisation_des_tests_et_qualite_logicielle/-/pipelines)

Projet de fin de module - Université Hassan II de Casablanca, Faculté des Sciences Aïn Chock, filière IIIA, année 2025-2026.
Réalisé par **ESSALHI Moussa**, encadré par **Ayoub Koddam**.

Ce dépôt contient l'automatisation des tests d'une application web de gestion d'étudiants, vue par l'équipe QA :

| Type de test | Cible | Outils |
|---|---|---|
| UI | Formy (https://formy-project.herokuapp.com) | Selenium 4, TestNG, Page Object Model, Allure |
| API | Reqres (https://reqres.in) | RestAssured + json-schema-validator, Postman + Newman |
| Performance | Reqres | Apache JMeter 5.6 (50 utilisateurs) |
| Sécurité | Formy | OWASP ZAP (baseline passif) |
| CI/CD | - | GitLab CI (`.gitlab-ci.yml`), Jenkinsfile en alternative |

Dépôts : [GitHub](https://github.com/essalhi-moussa/Automatisation_des_Tests_et_Qualite_Logicielle) (code) et [GitLab](https://gitlab.com/essalhi-moussa-group/automatisation_des_tests_et_qualite_logicielle) (pipeline CI/CD).

## Choix à connaître avant de lire les tests

- **Formy n'a pas de page de connexion ni d'iFrame.** La page `/form` sert de scénario d'inscription. L'exigence « iFrames » est couverte par une page locale autonome (test déterministe) et, séparément, par `the-internet.herokuapp.com/nested_frames` (groupe `external`, site tiers instable).
- **Reqres limite le débit** : 20 requêtes par minute et un quota journalier de 40 requêtes (en-têtes `Ratelimit-*` / `X-Ratelimit-*`). Au-delà : HTTP 429. Les tests rejouent après un 429 ; un **mock local** (`mock/reqres-mock.js`) permet de développer sans quota. Le test de charge sur l'API publique mesure donc surtout cette limitation, ce qui est analysé dans le rapport.
- Reqres ne persiste pas les écritures : POST/PUT/DELETE renvoient un écho, `GET /users/23` renvoie 404.

## Structure du dépôt

```
.
├── pom.xml                         Maven : dépendances, profils smoke / ui / api / external / all
├── .gitlab-ci.yml                  Pipeline GitLab CI
├── Jenkinsfile                     Pipeline Jenkins (alternative)
├── src/test/java/ma/fsac/qa/
│   ├── config/Config.java          Lecture de config.properties / -D / variables d'environnement
│   ├── base/                       BaseTest (ThreadLocal<WebDriver>), DriverFactory (Selenium Manager)
│   ├── listeners/TestListener.java Capture d'écran jointe à Allure en cas d'échec
│   ├── pages/                      Page Objects (Formy + frames)
│   ├── tests/ui/                   Tests Selenium
│   ├── tests/api/                  Tests RestAssured
│   └── utils/                      Data providers, gestionnaire de 429, relance
├── src/test/resources/
│   ├── config.properties           URL, navigateur, délais, clé API
│   ├── schemas/                    Schémas JSON des réponses
│   └── testng/                     smoke.xml, ui.xml, api.xml, external.xml, all.xml
├── postman/                        Collection v2.1 + environnements (public, mock)
├── jmeter/                         reqres-load-test.jmx + data/users.csv
├── mock/reqres-mock.js             Mock local de Reqres (Node.js, sans dépendance)
├── scripts/                        zap-scan.sh, run-jmeter.sh, run-newman.sh, run-suite.sh, notify-webhook.sh, génération des documents
├── reports/                        ui/ api/ perf/ security/ + summary.json
└── docs/                           Plan_de_tests et Rapport_final (.docx et .pdf), énoncé, figures
```

## Prérequis

- JDK 17 ou plus (le code est compilé pour Java 17), Maven 3.9
- Google Chrome (le driver est téléchargé par Selenium Manager : aucun chemin de driver n'est codé en dur)
- Node.js 18+ pour Newman, le mock et le CLI Allure : `npm i -g newman newman-reporter-htmlextra allure-commandline`
- Apache JMeter 5.6 (pour le test de charge) ; Docker (pour ZAP en CI) ou ZAP installé localement
- Python 3 avec `python-docx`, `matplotlib`, `pypdf` (uniquement pour régénérer les documents)

## Lancer les tests

Toutes les suites passent par un profil Maven. Les paramètres se surchargent avec `-D` : `-Dbrowser=chrome|firefox|edge`, `-Dheadless=true|false`, `-Dapi.base.url=...`, `-Dremote.url=...` (Selenium Grid).

```bash
mvn -P smoke test       # parcours critiques UI + API (suite par défaut)
mvn -P ui test          # 21 tests UI (Chrome headless, 3 classes en parallèle)
mvn -P api test         # 9 tests API contre https://reqres.in
mvn -P external test    # frames du site tiers the-internet (instable, séparé)
mvn -P all test         # api + ui
```

La clé API Reqres est lue dans `REQRES_API_KEY` si la variable existe, sinon dans `config.properties` (`api.key`).

**Sans consommer le quota Reqres**, lancer le mock puis cibler son URL :

```bash
node mock/reqres-mock.js                       # écoute sur http://localhost:3999
mvn -P api test -Dapi.base.url=http://localhost:3999
RATE_LIMIT=5 RATE_WINDOW_S=10 node mock/reqres-mock.js 3998   # variante avec limitation de débit
```

### Postman et Newman

```bash
bash scripts/run-newman.sh public      # API publique
bash scripts/run-newman.sh mock        # mock local
python scripts/build_postman.py        # régénère collection et environnements
```

La collection `postman/Reqres.postman_collection.json` (v2.1) utilise les variables d'environnement `baseUrl`, `apiKey`, `maxResponseTime`, un script de pré-requête (jeu de données aléatoire) et des `pm.test` sur le statut, le corps, le schéma et le temps.

### Performance (JMeter)

```bash
bash scripts/run-jmeter.sh reqres                                  # 50 utilisateurs, montée en charge 10 s, 10 boucles
PROTOCOL=http HOST=localhost PORT=3999 bash scripts/run-jmeter.sh mock
USERS=50 RAMPUP=10 LOOPS=10 JMETER_BIN=/chemin/jmeter bash scripts/run-jmeter.sh mon-run
```

Le tableau de bord HTML est produit dans `reports/perf/<run>/dashboard/index.html`.

### Sécurité (OWASP ZAP)

```bash
bash scripts/zap-scan.sh                       # Docker : zap-baseline.py (analyse passive)
ZAP_MODE=full bash scripts/zap-scan.sh         # zap-full-scan.py : attaques actives, uniquement sur une cible dont vous êtes propriétaire
ZAP_HOME=/chemin/ZAP_2.17.0 bash scripts/zap-scan.sh   # sans Docker, avec un ZAP installé
```

Rapports : `reports/security/zap-*.html` et `zap-*.json`.

## Consulter les rapports

| Rapport | Fichier |
|---|---|
| Allure UI | `reports/ui/allure-local/index.html` (fichier unique, s'ouvre hors ligne) |
| Allure API | `reports/api/allure-*/index.html` |
| Newman (htmlextra) | `reports/api/newman/rapport-newman-*.html` |
| JMeter | `reports/perf/*/dashboard/index.html` |
| ZAP | `reports/security/zap-baseline.html` |
| Synthèse chiffrée | `reports/summary.json` (générée par `scripts/summarize_results.py`) |

Générer un rapport Allure : `bash scripts/run-suite.sh ui local` (ou `api mock -Dapi.base.url=...`), ou à la main :
`allure generate target/allure-results --clean --single-file -o reports/ui/allure-local`.

## Pipeline CI/CD

`.gitlab-ci.yml` enchaîne `build`, `api-tests` (RestAssured, Newman), `ui-tests` (Selenium sur le service `selenium/standalone-chrome`), `performance` (manuel ou planifié), `security` (ZAP, `allow_failure`) et `report` (Allure publié avec GitLab Pages). Les artefacts sont conservés 30 jours, les rapports JUnit sont exposés à GitLab et le dépôt Maven est mis en cache.

Variables CI (Settings > CI/CD > Variables) : `REQRES_API_KEY`, `API_BASE_URL`, `API_MODE`, `SLACK_WEBHOOK_URL`, `DISCORD_WEBHOOK_URL` (les deux dernières masquées, facultatives).

`API_MODE` vaut `auto` par défaut : une requête de contrôle mesure le quota Reqres restant et, s'il est insuffisant, les jobs API utilisent le mock local (`scripts/ci-select-api.sh`). La cible retenue est écrite dans `reports/api/cible-api.txt` (artefact du job). `real` force Reqres, `mock` force le mock.

Notifications :

- **E-mail** : Settings > Integrations > « Pipeline status emails » (destinataires, envoi sur échec seulement ou toujours).
- **Webhook** : si `SLACK_WEBHOOK_URL` ou `DISCORD_WEBHOOK_URL` est définie, `scripts/notify-webhook.sh` envoie un message en fin de pipeline.

**Exécution réelle** : pipeline [#2924651734](https://gitlab.com/essalhi-moussa-group/automatisation_des_tests_et_qualite_logicielle/-/pipelines/2924651734) réussi (RestAssured 9/9 et Newman 37/37 sur Reqres, Selenium 21/21, ZAP, Allure). Rapport Allure publié : https://automatisation-des-tests-et-qualite-logicielle-5d7828.gitlab.io/ . Résumé et artefacts : `reports/ci/` (`python scripts/fetch_ci_results.py`).

`Jenkinsfile` fournit l'équivalent (étapes parallèles, plugin Allure, JUnit, `emailext`). Outils Jenkins attendus : `Maven-3.9`, `JDK-17`.

## Documents

- `docs/Plan_de_tests.docx` / `.pdf` : objectifs, périmètre, stratégie, environnements, critères, risques, scénarios, matrice de traçabilité.
- `docs/Rapport_final.docx` / `.pdf` : architecture, scénarios, résultats (UI, API, performance, sécurité), CI/CD, difficultés, recommandations.
- Régénération : `python scripts/summarize_results.py && python scripts/build_figures.py && python scripts/build_docs.py all`. Les noms peuvent être surchargés avec `QA_AUTEURS`, `QA_ENCADRANT` et `QA_FILIERE`.

## Rendu

**Captures du pipeline.** Après une exécution réussie du pipeline, déposer les captures dans `docs/img/ci/` sous ces noms (une partie suffit, elles sont insérées automatiquement au chapitre 6 du rapport) :

| Fichier | Contenu |
|---|---|
| `1-pipeline.png` | Pipeline réussi : graphe des stages (GitLab > Build > Pipelines, ou Stage View Jenkins) |
| `2-tests-junit.png` | Onglet « Tests » du pipeline (rapport JUnit) |
| `3-allure.png` | Rapport Allure publié (GitLab Pages ou page Allure de Jenkins) |
| `4-notification.png` | E-mail de statut du pipeline ou message Slack/Discord |

Puis : `python scripts/build_docs.py rapport`.

**Archive ZIP** (fichiers suivis par Git uniquement : ni `target/`, ni `.git`) :

```bash
git archive --format=zip --prefix=M11_QAOps_ESSALHI_Moussa/ -o ../M11_QAOps_ESSALHI_Moussa_IIIA.zip HEAD -- . ':(exclude)docs/enonce'
```
