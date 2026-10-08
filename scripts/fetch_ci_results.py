#!/usr/bin/env python3
"""Recupere le resultat reel d'un pipeline GitLab (projet public) dans reports/ci/.

Usage : python scripts/fetch_ci_results.py [id_pipeline]   (par defaut : dernier pipeline de main)
Produit reports/ci/pipeline-gitlab.json (statut, jobs, chiffres extraits des journaux)
et copie les artefacts ZAP et Newman du pipeline dans reports/ci/.
"""
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

PROJECT_PATH = "essalhi-moussa-group/automatisation_des_tests_et_qualite_logicielle"
WEB = "https://gitlab.com/" + PROJECT_PATH
API = "https://gitlab.com/api/v4/projects/" + PROJECT_PATH.replace("/", "%2F")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "reports", "ci")
os.makedirs(OUT, exist_ok=True)


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "m11-qa-report"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def log(job_id):
    text = get("%s/-/jobs/%d/raw" % (WEB, job_id))
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)


pid = int(sys.argv[1]) if len(sys.argv) > 1 else json.loads(get(API + "/pipelines?ref=main&per_page=1"))[0]["id"]
p = json.loads(get("%s/pipelines/%d" % (API, pid)))
jobs = json.loads(get("%s/pipelines/%d/jobs?per_page=50" % (API, pid)))

result = {
    "pipeline_id": pid, "status": p["status"], "sha": p["sha"][:7], "ref": p["ref"],
    "created_at": p["created_at"], "duration_s": p.get("duration"), "web_url": p["web_url"],
    "jobs": [{"name": j["name"], "stage": j["stage"], "status": j["status"],
              "duration_s": round(j["duration"] or 0)} for j in jobs],
}

for j in jobs:
    if j["status"] != "success":
        continue
    text = log(j["id"])
    if j["name"] == "api-restassured":
        m = re.search(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$", text, re.M)
        t = re.search(r"Cible API : (.+)", text)
        result["restassured"] = {"run": int(m.group(1)), "failures": int(m.group(2)), "errors": int(m.group(3)),
                                 "target": t.group(1).strip() if t else None}
    elif j["name"] == "api-newman":
        m = re.search(r"assertions\s*│\s*(\d+)\s*│\s*(\d+)", text)
        t = re.search(r"Cible API : (.+)", text)
        result["newman"] = {"assertions": int(m.group(1)), "failed": int(m.group(2)),
                            "target": t.group(1).strip() if t else None}
    elif j["name"] == "ui-selenium":
        m = re.search(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$", text, re.M)
        result["selenium"] = {"run": int(m.group(1)), "failures": int(m.group(2)), "errors": int(m.group(3))}
    elif j["name"] == "security-zap":
        m = re.search(r"FAIL-NEW: (\d+)\s+FAIL-INPROG: (\d+)\s+WARN-NEW: (\d+)\s+WARN-INPROG: (\d+)\s+INFO: (\d+)\s+IGNORE: (\d+)\s+PASS: (\d+)", text)
        if m:
            result["zap"] = dict(zip(["fail_new", "fail_inprog", "warn_new", "warn_inprog", "info", "ignore", "pass"],
                                     map(int, m.groups())))
    if j["name"] in ("security-zap", "api-newman"):
        try:
            z = zipfile.ZipFile(io.BytesIO(get("%s/-/jobs/%d/artifacts/download" % (WEB, j["id"]), binary=True)))
            for n in z.namelist():
                if re.search(r"(zap-baseline\.(html|json)|rapport-newman\.html)$", n):
                    with open(os.path.join(OUT, os.path.basename(n)), "wb") as f:
                        f.write(z.read(n))
        except Exception as e:  # artefacts expires ou inaccessibles : on garde le resume
            print("artefacts %s non recuperes : %s" % (j["name"], e))

try:
    pages = get("https://automatisation-des-tests-et-qualite-logicielle-5d7828.gitlab.io/")
    result["pages_url"] = "https://automatisation-des-tests-et-qualite-logicielle-5d7828.gitlab.io/" if "allure" in pages.lower() else None
except Exception:
    result["pages_url"] = None

with open(os.path.join(OUT, "pipeline-gitlab.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(json.dumps({k: v for k, v in result.items() if k != "jobs"}, indent=2, ensure_ascii=False))
print(os.listdir(OUT))
