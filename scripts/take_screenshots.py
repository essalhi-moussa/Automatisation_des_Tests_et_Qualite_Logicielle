#!/usr/bin/env python3
"""Capture les rapports HTML (Allure, Newman, JMeter, ZAP) avec Chrome headless pour le rapport final.

Usage : python scripts/take_screenshots.py [nom_run_api] [nom_run_perf]
        (par defaut : reqres si le rapport existe, sinon mock)
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from docgen import find_browser  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "docs", "img")
os.makedirs(IMG, exist_ok=True)


def url(rel):
    return "file:///" + os.path.join(ROOT, rel).replace("\\", "/")


def shoot(rel, out, width=1250, height=860, budget=15000):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        print("absent :", rel)
        return
    subprocess.run([find_browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--allow-file-access-from-files", "--window-size=%d,%d" % (width, height),
                    "--virtual-time-budget=%d" % budget, "--screenshot=" + os.path.join(IMG, out), url(rel)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    print("capture :", out)


def pick(*candidates):
    for c in candidates:
        if os.path.exists(os.path.join(ROOT, c)):
            return c
    return candidates[-1]


api = sys.argv[1] if len(sys.argv) > 1 else None
perf = sys.argv[2] if len(sys.argv) > 2 else None
newman = pick("reports/api/newman/rapport-newman-%s.html" % (api or "public"), "reports/api/newman/rapport-newman-mock.html")
jm = pick("reports/perf/%s/dashboard/index.html" % (perf or "reqres"), "reports/perf/mock/dashboard/index.html")

shoot("reports/ui/allure-local/index.html", "shot-allure-ui.png", 1400, 820)
shoot(newman, "shot-newman.png", 1250, 900)
shoot(jm, "shot-jmeter.png", 1300, 900)
shoot("reports/security/zap-baseline.html", "shot-zap.png", 1200, 900)
