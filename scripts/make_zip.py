#!/usr/bin/env python3
"""Construit l'archive de rendu a partir du dernier commit (git archive) puis verifie son contenu.

Usage : python scripts/make_zip.py [dossier_de_sortie]
Sortie : <dossier>/M11_QAOps_ESSALHI_Moussa_IIIA.zip (par defaut : dossier parent du depot)
Seuls les fichiers commites sont archives : commiter avant de lancer le script.
"""
import io
import os
import subprocess
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NAME = "M11_QAOps_ESSALHI_Moussa_IIIA"
OUT_DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(ROOT)
OUT = os.path.join(OUT_DIR, NAME + ".zip")

dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
if dirty:
    print("ATTENTION : modifications non commitees (absentes de l'archive) :\n" + dirty)

subprocess.run(["git", "archive", "--format=zip", "--prefix=%s/" % NAME, "-o", OUT, "HEAD", "--", ".",
                ":(exclude)docs/enonce"], cwd=ROOT, check=True)

z = zipfile.ZipFile(OUT)
names = set(z.namelist())
P = NAME + "/"


def has(path):
    return (P + path) in names


def has_prefix(prefix):
    return any(n.startswith(P + prefix) and not n.endswith("/") for n in names)


def pdf_pages(path):
    from pypdf import PdfReader
    return len(PdfReader(io.BytesIO(z.read(P + path))).pages)


def pdf_text(path):
    from pypdf import PdfReader
    return " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(z.read(P + path))).pages[:1])


checks = [
    ("Livrable 1 - scripts UI sur depot Git", has_prefix("src/test/java/ma/fsac/qa/tests/ui/") and has_prefix("src/test/java/ma/fsac/qa/pages/")),
    ("Livrable 1 - scripts API sur depot Git", has("src/test/java/ma/fsac/qa/tests/api/UsersApiTests.java") and has_prefix("src/test/resources/schemas/")),
    ("Projet Maven et suites TestNG", has("pom.xml") and has_prefix("src/test/resources/testng/")),
    ("Livrable 2 - collection Postman exportee", has("postman/Reqres.postman_collection.json")),
    ("Livrable 3 - plan de tests PDF", has("docs/Plan_de_tests.pdf")),
    ("Livrable 3 - plan de tests Word", has("docs/Plan_de_tests.docx")),
    ("Livrable 4 - rapport d'execution UI (Allure)", has("reports/ui/allure-local/index.html")),
    ("Livrable 4 - rapports d'execution API (Allure + Newman)", has_prefix("reports/api/allure-") and has_prefix("reports/api/newman/rapport-newman-")),
    ("Livrable 4 - rapport de performance (JMeter)", has("reports/perf/reqres/dashboard/index.html")),
    ("Livrable 4 - rapport de securite (ZAP)", has("reports/security/zap-baseline.html") and has("reports/security/zap-baseline.json")),
    ("Livrable 5 - rapport final PDF", has("docs/Rapport_final.pdf")),
    ("Livrable 5 - rapport final Word", has("docs/Rapport_final.docx")),
    ("Plan JMeter (.jmx) et donnees CSV", has("jmeter/reqres-load-test.jmx") and has("jmeter/data/users.csv")),
    ("Scan ZAP (script)", has("scripts/zap-scan.sh")),
    ("Pipeline GitLab CI", has(".gitlab-ci.yml")),
    ("Pipeline Jenkins (alternative)", has("Jenkinsfile")),
    ("README", has("README.md")),
    ("Pas de target/ ni de .git", not any("/target/" in n or "/.git/" in n for n in names)),
]
if has("docs/Rapport_final.pdf"):
    n = pdf_pages("docs/Rapport_final.pdf")
    checks.append(("Rapport final de 5 a 10 pages (%d pages)" % n, 5 <= n <= 10))
    t = pdf_text("docs/Rapport_final.pdf")
    checks.append(("Page de garde : ESSALHI Moussa / Ayoub Koddam", "ESSALHI Moussa" in t and "Ayoub Koddam" in t))
ci = sorted(n[len(P):] for n in names if n.startswith(P + "docs/img/ci/") and n.endswith(".png"))
checks.append(("Captures du pipeline (%d/4 : %s)" % (len(ci), ", ".join(os.path.basename(c) for c in ci) or "aucune"), len(ci) >= 3))

print("\nArchive :", OUT)
print("Taille  : %.1f Mo, %d fichiers\n" % (os.path.getsize(OUT) / 1e6, sum(1 for n in names if not n.endswith("/"))))
ok_all = True
for label, ok in checks:
    ok_all &= ok
    print("[%s] %s" % ("OK" if ok else "MANQUE", label))
print("\nResultat :", "conforme" if ok_all else "incomplet (voir MANQUE)")
