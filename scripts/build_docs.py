#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere docs/Plan_de_tests.(docx|pdf) et docs/Rapport_final.(docx|pdf) a partir de reports/summary.json.

Usage : python scripts/build_docs.py [plan|rapport|all]
Variables d'environnement facultatives : QA_AUTEURS, QA_ENCADRANT, QA_FILIERE
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from docgen import Doc  # noqa: E402
import scenarios as sc  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "docs", "img")
S = json.load(open(os.path.join(ROOT, "reports", "summary.json"), encoding="utf-8"))

AUTEURS = os.environ.get("QA_AUTEURS", "[NOM PRÉNOM / MEMBRES]")
ENCADRANT = os.environ.get("QA_ENCADRANT", "[NOM DU PROF]")
FILIERE = os.environ.get("QA_FILIERE", "IIIA")
ANNEE = "2025-2026"
REPO = "github.com/essalhi-moussa/Automatisation_des_Tests_et_Qualite_Logicielle"


SEP = chr(10) * 2  # ligne vide entre deux extraits


def fr(x, nd=0):
    """Nombre au format francais."""
    if x is None:
        return "n/d"
    s = ("%." + str(nd) + "f") % x
    return s.replace(".", ",")


def cover(doc_type, title, subtitle):
    return dict(
        university="Université Hassan II de Casablanca",
        faculty="Faculté des Sciences Aïn Chock",
        program="Module M11 - Automatisation des tests et qualité logicielle",
        doc_type=doc_type, title=title, subtitle=subtitle,
        fields=[("Réalisé par", AUTEURS), ("Filière", FILIERE), ("Encadrant", ENCADRANT),
                ("Année universitaire", ANNEE), ("Dépôt Git", REPO)],
    )


def counts(run):
    """Compte reussis/echecs/relances a partir des methodes TestNG (les relances apparaissent en SKIP)."""
    m = run["methods"]
    return (sum(1 for x in m if x["status"] == "PASS"), sum(1 for x in m if x["status"] == "FAIL"),
            sum(1 for x in m if x["status"] == "SKIP"))


def pick(d, *names):
    for n in names:
        if n in d:
            return n, d[n]
    return None, None


UI_NAME, UI = pick(S["ui"], "local")
EXT_NAME, EXT = pick(S["ui"], "thetinternet")
API_REAL_NAME, API_REAL = pick(S["api"], "reqres")
API_MOCK_NAME, API_MOCK = pick(S["api"], "mock")
NM_REAL_NAME, NM_REAL = pick(S["newman"], "public")
NM_MOCK_NAME, NM_MOCK = pick(S["newman"], "mock")
PERF_REAL = S["perf"].get("reqres")
PERF_MOCK = S["perf"].get("mock")
ZAP = S["security"]


# =============================================================================== PLAN DE TESTS
def build_plan():
    d = Doc("Plan de tests - Projet M11", "Plan de tests - Module M11 - FS Aïn Chock")
    d.cover(**cover("Plan de tests", "Plan de tests",
                    "Automatisation des tests UI, API, performance et sécurité d'une application web de gestion d'étudiants"))
    d.toc()

    d.h1("1. Introduction et objectifs")
    d.p("Ce document décrit la stratégie, le périmètre et les scénarios de test retenus par l'équipe QA pour l'application "
        "web de gestion d'étudiants du projet QAOps. Il sert de référence pour les scripts livrés dans le dépôt Git et pour "
        "les rapports d'exécution produits par le pipeline CI/CD.", "justify")
    d.bullets([
        "Vérifier automatiquement les parcours d'interface essentiels (formulaire, pop-ups, alertes, frames, listes, boutons).",
        "Valider le contrat des API REST : codes HTTP, contenu JSON, structure (schéma) et temps de réponse.",
        "Mesurer le comportement sous charge (50 utilisateurs simultanés) : temps de réponse, débit, taux d'erreur.",
        "Repérer les vulnérabilités simples (en-têtes manquants, cookies, composants obsolètes, XSS) et formuler des recommandations.",
        "Exécuter l'ensemble dans un pipeline reproductible qui produit des rapports et notifie l'équipe.",
    ])

    d.h1("2. Périmètre")
    d.table(["Dans le périmètre", "Hors périmètre"], [[
        "UI : application de démonstration Formy (formulaire, modal, switch-window, dropdown, radio, checkbox, boutons, champs désactivés).\n"
        "API : Reqres.in (/api/users, /api/login).\n"
        "Performance : GET et POST sur Reqres.\n"
        "Sécurité : analyse passive de Formy avec OWASP ZAP.",
        "Tests unitaires du code applicatif (non fourni).\n"
        "Tests d'accessibilité et de compatibilité multi-navigateurs (Chrome uniquement exécuté ; Firefox et Edge sont prévus dans la fabrique de drivers).\n"
        "Analyse active (attaques) d'un site dont nous ne sommes pas propriétaires.\n"
        "Tests de charge au-delà de 50 utilisateurs."]], widths=[1, 1], font=9)
    d.note("**Choix documentés.** (1) Formy n'a ni page de connexion ni formulaire d'inscription dédié : la page `/form` "
           "(« Complete Web Form ») est utilisée comme scénario d'inscription. (2) Formy n'a aucune page contenant un iFrame : l'exigence "
           "« frames/iFrames » est couverte par une page locale autonome (déterministe) et par `the-internet.herokuapp.com/nested_frames` "
           "(site de démonstration public, exécuté à part car instable).")

    d.h1("3. Stratégie de test")
    d.p("La stratégie suit la pyramide des tests : le plus grand nombre de contrôles se fait à la couche API (rapide et stable), "
        "l'interface est limitée aux parcours essentiels, et la performance et la sécurité complètent le dispositif.", "justify")
    d.image(os.path.join(IMG, "pyramide.png"), 9.5, "Figure 1 - Pyramide de tests adaptée au projet")
    d.table(["Niveau", "Objectif", "Outils", "Déclenchement"], [
        ["API", "Contrat, statuts, schémas JSON, temps de réponse, cas négatifs", "RestAssured, TestNG, Postman + Newman", "À chaque push (CI)"],
        ["UI", "Parcours utilisateur, pop-ups, alertes, frames, listes", "Selenium 4, TestNG, Allure", "À chaque push (CI)"],
        ["Performance", "50 utilisateurs, temps, débit, erreurs", "JMeter 5.6 (mode CLI, dashboard HTML)", "Manuel ou planifié"],
        ["Sécurité", "En-têtes, cookies, composants, XSS", "OWASP ZAP (baseline passif)", "Planifié, non bloquant"],
    ], widths=[1.1, 3, 2.7, 1.7], font=9, caption="Tableau 1 - Niveaux de test")
    d.p("Principes appliqués dans le code : Page Object Model, WebDriver stocké dans un ThreadLocal, attentes explicites uniquement "
        "(aucun `Thread.sleep` dans les pages), données de test fournies par des data providers TestNG, capture d'écran jointe à "
        "Allure en cas d'échec, URL et clé API centralisées dans `config.properties`.", "justify")

    d.h1("4. Environnements et outils")
    d.table(["Élément", "Valeur"], [
        ["Poste d'exécution", "Windows 11, Java 21 (compilation en cible Java 17), Maven 3.9, Chrome (version courante) via Selenium Manager"],
        ["Applications cibles", "Formy (formy-project.herokuapp.com) ; Reqres (reqres.in) ; the-internet.herokuapp.com (frames)"],
        ["Mock local", "mock/reqres-mock.js (Node.js) : reproduit le contrat observé de Reqres, sert à développer sans consommer le quota"],
        ["Tests UI / API", "Selenium 4.35, TestNG 7.10, RestAssured 5.5 + json-schema-validator, AssertJ, Allure TestNG 2.29"],
        ["API (Postman)", "Collection v2.1 + environnements ; Newman avec reporter htmlextra"],
        ["Performance", "Apache JMeter 5.6.3, plan jmeter/reqres-load-test.jmx"],
        ["Sécurité", "OWASP ZAP 2.17.0 (plan Automation Framework équivalent à zap-baseline.py ; image Docker en CI)"],
        ["CI/CD", "GitLab CI (.gitlab-ci.yml) ; Jenkinsfile déclaratif en alternative"],
    ], widths=[1.3, 4.5], font=9, caption="Tableau 2 - Environnement de test")

    d.h1("5. Critères d'entrée et de sortie")
    d.table(["Critères d'entrée", "Critères de sortie"], [[
        "Dépôt Git à jour et compilable (`mvn test-compile`).\nApplications cibles joignables (HTTP 200).\n"
        "Quota Reqres disponible, sinon utilisation du mock local.\nOutils installés (Chrome, JMeter, Newman, ZAP).",
        "100 % des tests de la suite `ui` et de la suite `api` réussis.\nCollection Newman : 0 assertion en échec.\n"
        "Test de charge exécuté avec 50 utilisateurs ; taux d'erreur et percentiles rapportés (les 429 sont analysés, pas masqués).\n"
        "Rapport ZAP produit ; aucune alerte de risque élevé non traitée.\nRapports archivés dans `reports/`."]],
        widths=[1, 1], font=9, caption="Tableau 3 - Critères")

    d.h1("6. Risques et parades")
    d.table(["Risque", "Impact", "Parade"], [
        ["Limite de débit de Reqres : 20 requêtes/minute et quota journalier de 40 requêtes (en-têtes Ratelimit-*, X-Ratelimit-*)",
         "Réponses 429, tests API et test de charge faussés", "Gestionnaire de 429 dans les tests (attente puis relance), mock local, analyse du 429 comme résultat"],
        ["Sites de démonstration instables (the-internet : chargements > 30 s)", "Tests UI intermittents",
         "Page locale déterministe pour la couverture iFrame ; tests du site tiers isolés dans le groupe `external` avec relance limitée"],
        ["Reqres ne persiste pas les écritures (POST/PUT/DELETE)", "Impossible de relire une ressource créée", "Assertions sur l'écho de la réponse, pas sur l'état"],
        ["Pas de Docker sur le poste d'exécution", "Scan ZAP par l'image officielle impossible localement", "ZAP installé localement avec un plan équivalent ; script Docker utilisé en CI"],
        ["Évolution des sites tiers (identifiants, contenus)", "Échecs non liés à nos scripts", "Locators sur identifiants stables, constat documenté dans le rapport"],
    ], widths=[2.6, 1.9, 3.1], font=8.5, caption="Tableau 4 - Registre des risques")

    d.landscape(True)
    d.h1("7. Scénarios de test")
    d.p("Chaque scénario précise ses préconditions, ses étapes, son jeu de données, le résultat attendu et le critère de validation. "
        "La colonne « Script » renvoie au code automatisé.", small=True)
    header = ["ID", "Titre", "Préconditions", "Étapes", "Jeu de données", "Résultat attendu", "Critère de validation", "Prio.", "Script"]
    widths = [0.55, 1.5, 1.2, 2.5, 1.5, 1.7, 2.0, 0.55, 1.5]
    d.h2("7.1 Interface utilisateur (Selenium)")
    d.table(header, [list(r) for r in sc.UI], widths=widths, font=7, caption="Tableau 5 - Scénarios UI")
    d.h2("7.2 API (RestAssured et Postman)")
    d.table(header, [list(r) for r in sc.API], widths=widths, font=7, caption="Tableau 6 - Scénarios API")
    d.h2("7.3 Performance et sécurité")
    d.table(header, [list(r) for r in sc.PERF + sc.SEC], widths=widths, font=7, caption="Tableau 7 - Scénarios de performance et de sécurité")
    d.landscape(False)

    d.h1("8. Matrice de traçabilité")
    d.table(["Exigence", "Description (sujet)", "Scénarios / livrables"],
            [list(r) for r in sc.REQUIREMENTS], widths=[0.7, 3.5, 2.3], font=9,
            caption="Tableau 8 - Exigence vers test")

    d.h1("9. Organisation et livrables")
    d.table(["Livrable", "Emplacement"], [
        ["Scripts de test (UI, API), suites TestNG", "src/test/java, src/test/resources/testng"],
        ["Collection Postman exportée et environnements", "postman/"],
        ["Plan de charge JMeter et jeu de données", "jmeter/"],
        ["Scripts ZAP, Newman, JMeter, mock", "scripts/, mock/"],
        ["Pipeline CI/CD", ".gitlab-ci.yml, Jenkinsfile"],
        ["Rapports d'exécution (UI, API, performance, sécurité)", "reports/"],
        ["Plan de tests et rapport final (Word et PDF)", "docs/"],
    ], widths=[3.4, 2.6], font=9, caption="Tableau 9 - Livrables")

    out = os.path.join(ROOT, "docs")
    nums, pages = d.save_pdf(os.path.join(out, "Plan_de_tests.pdf"))
    d.save_docx(os.path.join(out, "Plan_de_tests.docx"), nums)
    print("Plan de tests : %d pages" % pages)


# =============================================================================== RAPPORT FINAL
def excerpt(rel, start, nlines, end=None):
    """Extrait un bloc du code reel : nlines lignes, ou jusqu'a la ligne `end` (incluse) si elle est fournie."""
    lines = open(os.path.join(ROOT, rel), encoding="utf-8").read().split("\n")
    for i, ln in enumerate(lines):
        if start in ln:
            if end:
                for j in range(i, len(lines)):
                    if lines[j].rstrip() == end:
                        return "\n".join(lines[i:j + 1])
            return "\n".join(lines[i:i + nlines])
    raise ValueError("Extrait introuvable : %s dans %s" % (start, rel))


def build_report():
    d = Doc("Rapport final - Projet M11", "Rapport final - Module M11 - FS Aïn Chock")
    d.cover(**cover("Rapport final", "Rapport final",
                    "Automatisation des tests UI, API, performance et sécurité - intégration CI/CD"))
    d.toc()

    ui_p, ui_f, ui_s = counts(UI)
    api = API_REAL or API_MOCK
    api_env = "API publique Reqres" if API_REAL else "mock local"
    nm = NM_REAL or NM_MOCK

    # ---------------------------------------------------------------- 1
    d.h1("1. Introduction")
    d.p("L'équipe QA de l'application web de gestion d'étudiants a automatisé les tests d'interface, d'API, de performance et de "
        "sécurité, puis les a intégrés dans un pipeline CI/CD. Ce rapport présente l'architecture retenue, les scénarios, les "
        "extraits de code significatifs, les résultats réels des exécutions, les difficultés rencontrées et les pistes d'amélioration.", "justify")
    d.p("Les plateformes imposées sont utilisées telles quelles : Formy pour l'interface, Reqres pour l'API, JMeter pour la charge, "
        "OWASP ZAP pour la sécurité et GitLab CI pour l'intégration continue (Jenkinsfile en alternative). Tous les chiffres "
        "ci-dessous proviennent des rapports archivés dans `reports/` (fichier de synthèse `reports/summary.json`).", "justify")

    # ---------------------------------------------------------------- 2
    d.h1("2. Architecture du projet")
    d.image(os.path.join(IMG, "architecture.png"), 13.6, "Figure 1 - Architecture de la solution de test")
    d.table(["Dossier", "Contenu"], [
        ["src/test/java/.../base, listeners, config", "BaseTest (WebDriver en ThreadLocal), DriverFactory (Selenium Manager), TestListener (capture Allure), Config"],
        ["src/test/java/.../pages", "Page Objects : FormPage, ModalPage, SwitchWindowPage, DropdownPage, RadioButtonPage, ButtonsPage, CheckboxPage, EnabledPage, FramesPage"],
        ["src/test/java/.../tests/ui et api", "Tests Selenium (21 dans la suite ui) et tests RestAssured (9 dans la suite api)"],
        ["src/test/resources", "config.properties, schémas JSON, suites TestNG (smoke, ui, api, external, all)"],
        ["postman/, jmeter/, mock/, scripts/", "Collection v2.1, plan de charge et CSV, mock Reqres, scripts ZAP / JMeter / Newman"],
        [".gitlab-ci.yml, Jenkinsfile, reports/, docs/", "Pipelines, rapports d'exécution, plan de tests et rapport"],
    ], widths=[2.4, 4.4], font=8.5, caption="Tableau 1 - Structure du dépôt")

    # ---------------------------------------------------------------- 3
    d.h1("3. Scénarios de test")
    nui, napi = len(sc.UI), len(sc.API)
    d.p("%d scénarios UI, %d scénarios API, 2 de performance et 2 de sécurité sont décrits en détail (préconditions, étapes, données, "
        "résultat attendu, critère, priorité) dans le plan de tests. Le tableau suivant en donne la vue d'ensemble." % (nui, napi), "justify")
    rows = []
    for r in sc.UI:
        rows.append([r[0], r[1], r[7]])
    short = [[r[0], r[1], r[7]] for r in sc.UI + sc.API + sc.PERF + sc.SEC]
    half = (len(short) + 1) // 2
    left, right = short[:half], short[half:]
    while len(right) < len(left):
        right.append(["", "", ""])
    d.table(["ID", "Scénario", "Prio.", "ID", "Scénario", "Prio."],
            [l + r for l, r in zip(left, right)], widths=[0.55, 2.6, 0.6, 0.55, 2.6, 0.6], font=7.5,
            caption="Tableau 2 - Vue d'ensemble des scénarios")
    d.note("**Choix liés aux plateformes.** Formy n'a pas de page de connexion : la page /form joue le rôle du formulaire d'inscription. "
           "Formy n'a pas d'iFrame : l'exigence est couverte par une page locale autonome (UI-15) et par le site the-internet.herokuapp.com "
           "(UI-13, UI-14), isolé dans le groupe `external` car ses chargements dépassent parfois 30 secondes.")

    # ---------------------------------------------------------------- 4
    d.h1("4. Scripts : extraits significatifs")
    base = "src/test/java/ma/fsac/qa/base/BaseTest.java"
    d.code(SEP.join([excerpt(base, "private static final ThreadLocal", 0, end="    }"),
                         excerpt(base, "@BeforeMethod", 0, end="    }"),
                         excerpt(base, "@AfterMethod", 8)]),
           "Extrait 1 - BaseTest : un WebDriver par thread")
    d.code(excerpt("src/test/java/ma/fsac/qa/pages/FormPage.java", '@Step("Soumettre le formulaire")', 8),
           "Extrait 2 - Page Object : attente explicite du contenu de /thanks (et non de l'URL seule)")
    d.code(excerpt("src/test/java/ma/fsac/qa/tests/api/UsersApiTests.java", "public void listerLesUtilisateurs", 12),
           "Extrait 3 - Test RestAssured : statut, corps, schéma JSON et temps")
    d.code("pm.test('Statut HTTP 201', function () { pm.response.to.have.status(201); });\n"
           "pm.test('Temps de réponse < ' + pm.environment.get('maxResponseTime') + ' ms', function () {\n"
           "    pm.expect(pm.response.responseTime).to.be.below(Number(pm.environment.get('maxResponseTime')));\n"
           "});\n"
           "pm.test('Schéma JSON valide', function () { pm.response.to.have.jsonSchema(schema); });",
           "Extrait 4 - Assertions Postman (statut, temps, schéma), variables d'environnement baseUrl / apiKey / maxResponseTime")

    # ---------------------------------------------------------------- 5
    d.h1("5. Résultats")
    d.h2("5.1 Tests UI (Selenium, Allure)")
    d.p("La suite `ui` (profil Maven `ui`, Chrome headless, 3 classes en parallèle) donne **%d tests réussis sur %d** en %s s. "
        "Le rapport Allure complet est dans `reports/ui/allure-local/index.html`." % (ui_p, UI["total"], fr(UI["duration_s"], 1)), "justify")
    d.image(os.path.join(IMG, "shot-allure-ui.png"), 12.2, "Figure 2 - Rapport Allure de la suite UI (capture réelle)")
    if EXT:
        e_p, e_f, e_s = counts(EXT)
        d.p("Le groupe `external` (the-internet.herokuapp.com/nested_frames) a été exécuté séparément : **%d réussis, %d échec définitif, %d relances** "
            "(relance automatique limitée à 2). Ce site tiers répond de façon irrégulière ; ce résultat est rapporté tel quel et n'entre pas dans le "
            "critère de sortie de la suite `ui`." % (e_p, e_f, e_s), "justify")

    d.h2("5.2 Tests API (RestAssured et Postman / Newman)")
    rows = []
    if API_REAL:
        rows.append(["RestAssured - API publique", "%d / %d" % (API_REAL["passed"], API_REAL["total"]), fr(API_REAL["duration_s"], 1) + " s"])
    if API_MOCK:
        rows.append(["RestAssured - mock local", "%d / %d" % (API_MOCK["passed"], API_MOCK["total"]), fr(API_MOCK["duration_s"], 1) + " s"])
    if NM_REAL:
        rows.append(["Newman - API publique (%d requêtes)" % NM_REAL["requests"],
                     "%d / %d assertions" % (NM_REAL["assertions"] - NM_REAL["assertions_failed"], NM_REAL["assertions"]),
                     "%s ms (moy. réponse %s ms)" % (fr(NM_REAL["duration_ms"]), fr(NM_REAL["avg_response_ms"], 0))])
    if NM_MOCK:
        rows.append(["Newman - mock local (%d requêtes)" % NM_MOCK["requests"],
                     "%d / %d assertions" % (NM_MOCK["assertions"] - NM_MOCK["assertions_failed"], NM_MOCK["assertions"]),
                     "%s ms (moy. réponse %s ms)" % (fr(NM_MOCK["duration_ms"]), fr(NM_MOCK["avg_response_ms"], 0))])
    d.table(["Exécution", "Réussis", "Durée"], rows, widths=[3.2, 1.8, 2.2], font=8.5, caption="Tableau 3 - Résultats des tests API")
    d.p("Chaque test vérifie le code HTTP, le contenu JSON, le schéma (fichiers `src/test/resources/schemas`) et le temps de réponse "
        "(seuil de 3 s). Les cas négatifs couvrent GET /users/23 (404) et POST /login sans mot de passe (400). "
        "Comportements constatés : POST et PUT ne persistent rien, DELETE renvoie 204 sans corps, et l'identifiant renvoyé par POST est une chaîne.", "justify")
    d.note("**Constat important : Reqres limite fortement le débit.** Les réponses portent les en-têtes `Ratelimit-Limit: 20` (20 requêtes par "
           "minute) et `X-Ratelimit-Limit: 40` (quota journalier). Nous avons épuisé ce quota pendant la mise au point : l'API répond alors "
           "429 jusqu'à la réinitialisation à minuit UTC. Les tests rejouent donc les requêtes après un 429 (attente du délai `Ratelimit-Reset`) et un "
           "mock local fidèle au contrat permet de poursuivre sans quota.")
    d.image(os.path.join(IMG, "resultats.png"), 10.0, "Figure 3 - Synthèse des tests UI et API")

    d.h2("5.3 Performance (JMeter)")
    d.p("Plan : 50 utilisateurs, montée en charge de 10 s, 10 boucles par utilisateur, temps de réflexion aléatoire de 0,5 à 1,5 s, "
        "GET /api/users?page=2 puis POST /api/users alimenté par un CSV, avec assertions (code, JSONPath, durée < 3 s). "
        "Exécution en mode CLI avec génération du tableau de bord HTML.", "justify")
    prow = []
    for name, data, lab in (("reqres", PERF_REAL, "API publique Reqres"), ("mock", PERF_MOCK, "Mock local")):
        if not data:
            continue
        for label, v in data.items():
            if label.startswith("_"):
                continue
            prow.append([lab, label, v["samples"], fr(v["error_pct"], 2) + " %", fr(v["avg_ms"], 0), fr(v["p90_ms"], 0),
                         fr(v["p95_ms"], 0), fr(v["p99_ms"], 0), fr(v["throughput_rps"], 1)])
    d.table(["Cible", "Requête", "Échant.", "Erreurs", "Moy. (ms)", "P90", "P95", "P99", "Débit (req/s)"], prow,
            widths=[1.3, 1.9, 0.7, 0.8, 0.8, 0.5, 0.5, 0.5, 0.9], font=8, caption="Tableau 4 - Résultats JMeter")
    d.image(os.path.join(IMG, "performance.png"), 14.5, "Figure 4 - Temps de réponse (moyenne, P90, P95)")
    d.p(PERF_ANALYSIS(), "justify")

    d.h2("5.4 Sécurité (OWASP ZAP)")
    n_alerts = len(ZAP["alerts"])
    by = ZAP["by_risk"]
    d.p("Analyse baseline (spider puis analyse passive) de https://formy-project.herokuapp.com avec ZAP %s : **%d types d'alertes** "
        "(élevé %d, moyen %d, faible %d, informatif %d). Aucune attaque active n'a été lancée sur ce site tiers." % (
            ZAP["version"], n_alerts, by.get("High", 0), by.get("Medium", 0), by.get("Low", 0), by.get("Informational", 0)), "justify")
    d.table(["Alerte ZAP", "Risque", "OWASP Top 10 (2021)", "CWE", "Recommandation"], SEC_ROWS(), widths=[2.0, 0.8, 1.6, 0.6, 2.9],
            font=7.5, caption="Tableau 5 - Alertes principales, correspondance OWASP / CWE et correctifs")
    d.p("Contrôles complémentaires : une recherche de réflexion XSS (marqueur inoffensif dans les paramètres de /form et /thanks) n'a "
        "produit **aucune réflexion** ; le formulaire Formy n'envoie d'ailleurs pas ses champs au serveur (le bouton Submit est un lien vers /thanks). "
        "Points positifs relevés sur les en-têtes : `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff` sur les pages, cookie de session HttpOnly. "
        "Une clé d'API Google Maps est visible dans le code source de /autocomplete : elle doit être restreinte par référent HTTP.", "justify")

    # ---------------------------------------------------------------- 6
    d.h1("6. Pipeline CI/CD")
    d.image(os.path.join(IMG, "pipeline.png"), 15.5, "Figure 5 - Étapes du pipeline GitLab CI")
    d.bullets([
        "**build** : compilation Maven ; cache du dépôt Maven (clé = hash du pom.xml).",
        "**api-tests** : RestAssured (rapport JUnit exposé à GitLab) et Newman (HTML htmlextra + JUnit).",
        "**ui-tests** : Selenium sur le service `selenium/standalone-chrome` (navigateur distant via `remote.url`).",
        "**performance** : JMeter, déclenchement manuel ou planifié (pour ne pas épuiser le quota Reqres à chaque commit).",
        "**security** : ZAP baseline (image officielle), `allow_failure: true`.",
        "**report** : génération du rapport Allure, publié avec GitLab Pages ; artefacts conservés 30 jours.",
        "**Notifications** : e-mails de statut de pipeline (Settings > Integrations > Pipeline status emails) et webhook Slack/Discord via les variables CI `SLACK_WEBHOOK_URL` / `DISCORD_WEBHOOK_URL`.",
        "**Jenkinsfile** équivalent : étapes parallèles API, Allure Plugin, JUnit, `emailext`.",
    ])
    d.note("**Statut de vérification.** Les fichiers `.gitlab-ci.yml` et `Jenkinsfile` ont été validés syntaxiquement et chacune de leurs commandes a été exécutée "
           "localement (Maven, Newman, JMeter, ZAP, génération Allure). Le pipeline n'a pas encore tourné sur un runner GitLab : les captures ci-dessous sont à insérer après le premier push.")
    d.table(["Capture à insérer", "Où la prendre"], [
        ["[Capture 1 - Pipeline réussi : graphe des 6 stages]", "GitLab > CI/CD > Pipelines"],
        ["[Capture 2 - Rapport Allure publié sur GitLab Pages]", "Settings > Pages (URL du projet)"],
        ["[Capture 3 - Onglet Tests (rapport JUnit) d'un pipeline]", "Pipeline > Tests"],
        ["[Capture 4 - E-mail ou message Slack de fin de pipeline]", "Boîte de réception / canal"],
    ], widths=[3.4, 2.6], font=8.5, caption="Tableau 6 - Captures GitLab à ajouter")

    # ---------------------------------------------------------------- 7
    d.h1("7. Difficultés rencontrées et solutions")
    d.table(["Difficulté", "Solution"], [
        ["Formy n'a pas de page de connexion ni d'iFrame", "Page /form utilisée comme inscription ; page locale `data:` avec iFrames imbriqués, et nested_frames en complément"],
        ["Quota Reqres de 20 req/min et 40 req/jour : réponses 429", "Gestionnaire de 429 (attente de `Ratelimit-Reset`), mock local fidèle, 429 analysé comme résultat de performance"],
        ["Page /thanks : l'URL change avant le contenu (test intermittent)", "Attente explicite du titre « Thanks » au lieu de l'URL"],
        ["Bouton OK du modal sans effet", "Le test décrit le comportement réel et ferme le modal avec Close"],
        ["the-internet : chargement > 30 s, éditeur TinyMCE en lecture seule", "Abandon de /iframe, frames imbriqués avec stratégie de chargement NONE, groupe `external` isolé"],
        ["Pas de Docker sur le poste", "ZAP local avec plan Automation Framework équivalent ; image Docker conservée pour la CI"],
        ["Échappements JSON des schémas (shell Windows)", "Expressions régulières simplifiées ([0-9], [.]) et validation JSON de chaque schéma"],
    ], widths=[3.0, 3.8], font=8.5, caption="Tableau 7 - Problèmes et solutions")

    # ---------------------------------------------------------------- 8
    d.h1("8. Recommandations d'amélioration")
    d.bullets([
        "**Qualité des tests** : ajouter l'historique Allure (tendances), exécuter Firefox et Edge en matrice, paralléliser sur un Selenium Grid.",
        "**API** : tests de contrat (Pact), virtualisation de Reqres (WireMock) pour la CI afin de ne dépendre d'aucun quota, clé API personnelle stockée en variable CI masquée.",
        "**Performance** : définir des seuils bloquants (P95, taux d'erreur) dans le pipeline, tester sur un environnement dédié et non sur une API publique limitée.",
        "**Sécurité** : appliquer les en-têtes CSP, HSTS, cookies Secure et SameSite, mettre à jour jQuery, ajouter SRI ; ajouter un scan de dépendances et un scan ZAP authentifié sur l'application réelle.",
        "**Processus** : exécuter le pipeline à chaque merge request, notifier uniquement les échecs, tenir la matrice de traçabilité à jour.",
    ])

    # ---------------------------------------------------------------- 9
    d.h1("9. Conclusion")
    d.p(CONCLUSION(ui_p), "justify")

    out = os.path.join(ROOT, "docs")
    nums, pages = d.save_pdf(os.path.join(out, "Rapport_final.pdf"))
    d.save_docx(os.path.join(out, "Rapport_final.docx"), nums)
    print("Rapport final : %d pages" % pages)


def PERF_ANALYSIS():
    """Analyse textuelle construite a partir des chiffres reels."""
    parts = []
    if PERF_REAL:
        tot = PERF_REAL.get("Total")
        codes = PERF_REAL.get("_codes", {})
        n429 = sum(v for k, v in codes.items() if k.endswith(" 429"))
        ok = sum(v for k, v in codes.items() if k.endswith(" 200") or k.endswith(" 201"))
        total = sum(codes.values())
        if total:
            parts.append(
                "**API publique.** Sur %d échantillons, %d ont reçu un code de succès (200/201) et %d un **HTTP 429** (%s %%). "
                "Le taux d'erreur global JMeter est de %s %%. La limite de 20 requêtes par minute et le quota journalier "
                "sont atteints en quelques secondes avec 50 utilisateurs : l'API publique ne permet pas de mesurer une capacité "
                "réelle, elle mesure sa propre limitation. Les temps de réponse des seules requêtes réussies ne sont donc pas représentatifs "
                "d'une charge soutenue." % (total, ok, n429, fr(100.0 * n429 / total, 1), fr(tot["error_pct"], 2) if tot else "n/d"))
    if PERF_MOCK:
        tot = PERF_MOCK["Total"]
        parts.append(
            "**Mock local.** Le même plan, sans limitation de débit, valide le script : %d échantillons, %s %% d'erreurs, "
            "moyenne %s ms, P90 %s ms, P95 %s ms, débit %s req/s. Le débit est borné par les temps de réflexion (50 utilisateurs, "
            "environ 1 s de pause par requête), pas par le serveur. Ces valeurs valident l'outillage et ne préjugent pas des performances de Reqres."
            % (tot["samples"], fr(tot["error_pct"], 2), fr(tot["avg_ms"], 1), fr(tot["p90_ms"], 0), fr(tot["p95_ms"], 0),
               fr(tot["throughput_rps"], 1)))
    return " ".join(parts)


def SEC_ROWS():
    top10 = {
        "Content Security Policy (CSP) Header Not Set": ("A05 Mauvaise configuration", "Définir `Content-Security-Policy: default-src 'self'` avec les sources tierces strictement nécessaires."),
        "Sub Resource Integrity Attribute Missing": ("A08 Intégrité des logiciels et des données", "Ajouter `integrity=\"sha384-...\"` et `crossorigin` aux scripts et feuilles de style externes."),
        "Vulnerable JS Library": ("A06 Composants vulnérables ou obsolètes", "Mettre jQuery à jour (3.5.0 ou plus ; CVE-2020-11022/11023, CVE-2019-11358)."),
        "Absence of Anti-CSRF Tokens": ("A01 Contrôle d'accès défaillant", "Ajouter un jeton anti-CSRF aux formulaires POST (/fileupload)."),
        "Cookie Without Secure Flag": ("A05 Mauvaise configuration", "Positionner `Secure` sur le cookie de session."),
        "Cookie without SameSite Attribute": ("A01 Contrôle d'accès défaillant", "Positionner `SameSite=Lax` (ou Strict)."),
        "Strict-Transport-Security Header Not Set": ("A02 Défaillances cryptographiques", "Envoyer `Strict-Transport-Security: max-age=31536000; includeSubDomains`."),
        "X-Content-Type-Options Header Missing": ("A05 Mauvaise configuration", "Envoyer `X-Content-Type-Options: nosniff` sur toutes les ressources, y compris statiques."),
        "Cross-Domain JavaScript Source File Inclusion": ("A08 Intégrité des logiciels et des données", "Héberger localement les bibliothèques ou les verrouiller par SRI."),
        "Timestamp Disclosure - Unix": ("A05 Mauvaise configuration", "Pas d'action requise (faux positif probable : valeurs numériques)."),
    }
    rows = []
    for a in ZAP["alerts"]:
        if a["name"] in top10:
            o, rec = top10[a["name"]]
            rows.append([a["name"], a["riskdesc"].replace("Informational", "Info"), o, a["cwe"], rec])
    return rows


def CONCLUSION(ui_p):
    api = API_REAL or API_MOCK
    parts = ["Le projet livre une chaîne de tests automatisés complète et reproductible : %d tests UI Selenium réussis sur %d, "
             "%d tests API RestAssured réussis sur %d" % (ui_p, UI["total"], api["passed"], api["total"])]
    nm = NM_REAL or NM_MOCK
    if nm:
        parts.append(", %d assertions Postman validées sur %d" % (nm["assertions"] - nm["assertions_failed"], nm["assertions"]))
    parts.append(", un plan de charge JMeter de 50 utilisateurs et un scan ZAP assorti de recommandations chiffrées. ")
    parts.append("Le principal enseignement est que la qualité des résultats dépend autant de la cible que des scripts : les limites de Reqres "
                 "(429) et l'instabilité de certains sites de démonstration imposent de séparer les tests déterministes (mock, page locale) "
                 "des tests sur services tiers, et de rapporter honnêtement les écarts plutôt que de les masquer. "
                 "Il reste à exécuter le pipeline sur un runner GitLab, à y insérer les captures prévues et à enrichir le plan "
                 "selon les recommandations du chapitre 8.")
    return "".join(parts)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("plan", "all"):
        build_plan()
    if what in ("rapport", "all"):
        build_report()
