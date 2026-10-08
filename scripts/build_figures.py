#!/usr/bin/env python3
"""Genere les figures des documents (docs/img/*.png) : schemas et graphiques issus de reports/summary.json."""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG = os.path.join(ROOT, "docs", "img")
os.makedirs(IMG, exist_ok=True)
SUMMARY = json.load(open(os.path.join(ROOT, "reports", "summary.json"), encoding="utf-8"))

BLUE, GREEN, ORANGE, RED, GREY, DARK = "#1f4e79", "#2e7d32", "#ef8f1c", "#c62828", "#6b7280", "#1b1f24"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})


def box(ax, x, y, w, h, text, color=BLUE, fs=8.5, tc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=color, ec="none"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs, linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, color=GREY):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, color=color, lw=1.2))


def save(fig, name):
    fig.savefig(os.path.join(IMG, name), dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def architecture():
    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.6)
    ax.axis("off")
    box(ax, 0.2, 4.5, 9.6, 0.75, "Dépôt Git (GitLab / GitHub)  -  code, collection Postman, plan JMeter, scripts, pipeline", DARK)
    arrow(ax, 5, 4.5, 5, 4.05)
    box(ax, 0.2, 3.2, 9.6, 0.8, "Pipeline CI/CD  (.gitlab-ci.yml  /  Jenkinsfile)\nbuild  >  api-tests  >  ui-tests  >  performance  >  security  >  report", BLUE)
    cols = [
        (0.2, "Tests UI\nSelenium 4, TestNG\nPage Object Model", "Formy\n+ page locale (iFrame)"),
        (2.7, "Tests API\nRestAssured, schémas\nPostman, Newman", "Reqres.in\n(ou mock local)"),
        (5.2, "Performance\nJMeter 5.6\n50 utilisateurs", "Reqres.in\n(ou mock local)"),
        (7.7, "Sécurité\nOWASP ZAP\nbaseline (passif)", "Formy"),
    ]
    for x, top, target in cols:
        arrow(ax, x + 1.05, 3.2, x + 1.05, 2.75)
        box(ax, x, 1.75, 2.1, 1.0, top, "#2f6f9f", fs=7.4)
        arrow(ax, x + 1.05, 1.75, x + 1.05, 1.35)
        box(ax, x, 0.55, 2.1, 0.8, target, "#e5e7eb", fs=8, tc=DARK)
    box(ax, 0.2, 0.0, 9.6, 0.38, "Rapports : Allure (UI/API)  -  Newman htmlextra  -  dashboard JMeter  -  ZAP HTML/JSON  -  JUnit", GREEN, fs=8)
    save(fig, "architecture.png")


def pyramide():
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    levels = [
        (0.0, 10.0, "API (RestAssured, Postman)  -  base large, rapide, stable", "#2f6f9f"),
        (1.5, 7.0, "UI (Selenium)  -  parcours essentiels", "#1f4e79"),
        (3.0, 4.0, "Performance / sécurité", "#14304d"),
    ]
    for i, (x, w, label, c) in enumerate(levels):
        y = 0.4 + i * 1.5
        ax.add_patch(plt.Polygon([(x + 0.0 + i * 0.0, y), (10 - x, y), (10 - x - 0.7, y + 1.4), (x + 0.7, y + 1.4)],
                                 fc=c, ec="white"))
        ax.text(5, y + 0.7, label, ha="center", va="center", color="white", fontsize=7.8)
    ax.text(5, 5.35, "Pyramide de tests adaptée au projet", ha="center", fontsize=9.5, fontweight="bold", color=DARK)
    save(fig, "pyramide.png")


def pipeline():
    fig, ax = plt.subplots(figsize=(7.6, 1.9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 2.4)
    ax.axis("off")
    stages = [("build", "compile"), ("api-tests", "RestAssured\nNewman"), ("ui-tests", "Selenium\nChrome headless"),
              ("performance", "JMeter\n(manuel / planifié)"), ("security", "OWASP ZAP\n(allow_failure)"),
              ("report", "Allure\nGitLab Pages")]
    w = 1.7
    for i, (name, detail) in enumerate(stages):
        x = 0.1 + i * 1.95
        box(ax, x, 1.15, w, 0.7, name, BLUE if i not in (3, 4) else ORANGE, fs=8.5)
        ax.text(x + w / 2, 0.62, detail, ha="center", va="center", fontsize=7.4, color=DARK)
        if i < len(stages) - 1:
            arrow(ax, x + w, 1.5, x + 1.95, 1.5)
    ax.text(0.1, 2.2, "Notifications : e-mail GitLab (pipeline status) + webhook Slack/Discord en fin de pipeline",
            fontsize=7.8, color=GREY)
    save(fig, "pipeline.png")


def resultats():
    ui = SUMMARY["ui"].get("local")
    api = SUMMARY["api"].get("real") or SUMMARY["api"].get("mock")
    api_label = "API RestAssured"
    nm = SUMMARY["newman"].get("public") or SUMMARY["newman"].get("mock")
    labels, passed, failed = [], [], []
    if ui:
        labels.append("UI Selenium")
        passed.append(ui["passed"])
        failed.append(ui["failed"] + ui["skipped"])
    if api:
        labels.append(api_label)
        passed.append(api["passed"])
        failed.append(api["failed"] + api["skipped"])
    if nm:
        labels.append("Postman (assertions)")
        passed.append(nm["assertions"] - nm["assertions_failed"])
        failed.append(nm["assertions_failed"])
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    y = range(len(labels))
    ax.barh(list(y), passed, color=GREEN, label="Réussis")
    ax.barh(list(y), failed, left=passed, color=RED, label="En échec")
    for i, (p, f) in enumerate(zip(passed, failed)):
        ax.text(p + f + 0.6, i, "%d / %d" % (p, p + f), va="center", fontsize=8.5)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Nombre de tests / assertions")
    ax.set_xlim(0, max(p + f for p, f in zip(passed, failed)) * 1.2)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.22), ncol=2, fontsize=8, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "resultats.png")


def perf():
    runs = SUMMARY["perf"]
    fig, axes = plt.subplots(1, len(runs), figsize=(7.4, 2.7), squeeze=False)
    titles = {"mock": "Mock local (validation du plan)", "reqres": "Reqres.in (API réelle)"}
    for ax, (name, data) in zip(axes[0], sorted(runs.items(), key=lambda kv: kv[0] != "reqres")):
        labels = sorted(k for k in data if not k.startswith("_") and k != "Total")
        keys = [("avg_ms", "Moyenne", "#2f6f9f"), ("p90_ms", "P90", ORANGE), ("p95_ms", "P95", RED)]
        width = 0.26
        for j, (k, lab, c) in enumerate(keys):
            vals = [data[l][k] for l in labels]
            xs = [i + (j - 1) * width for i in range(len(labels))]
            ax.bar(xs, vals, width, label=lab, color=c)
            for x, v in zip(xs, vals):
                ax.text(x, v, "%d" % round(v), ha="center", va="bottom", fontsize=7)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels([l.replace(" /api/users", "\n/api/users") for l in labels], fontsize=7.5)
        ax.set_ylabel("ms")
        ax.set_title(titles.get(name, name), fontsize=8.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0][0].legend(fontsize=7.5, frameon=False)
    fig.tight_layout()
    save(fig, "performance.png")


def zap():
    sec = SUMMARY.get("security")
    if not sec:
        return
    order = ["High", "Medium", "Low", "Informational"]
    colors = [RED, ORANGE, "#d9b300", GREY]
    vals = [sec["by_risk"].get(o, 0) for o in order]
    labels = ["Élevé", "Moyen", "Faible", "Informatif"]
    fig, ax = plt.subplots(figsize=(4.2, 2.4))
    ax.bar(labels, vals, color=colors)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.1, str(v), ha="center", fontsize=9)
    ax.set_ylabel("Types d'alertes")
    ax.set_ylim(0, max(vals) + 1.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "zap-risques.png")


def captures():
    """Planche de trois captures reelles : Newman, JMeter, ZAP (fichiers docs/img/shot-*.png)."""
    from PIL import Image
    items = [("shot-newman.png", "Newman (htmlextra)", (70, 0, 1180, 830)),
             ("shot-jmeter.png", "JMeter (tableau de bord)", (250, 60, 1300, 850)),
             ("shot-zap.png", "OWASP ZAP (rapport HTML)", (0, 0, 1050, 790))]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.1))
    for ax, (f, title, box_) in zip(axes, items):
        p = os.path.join(IMG, f)
        if os.path.exists(p):
            ax.imshow(Image.open(p).crop(box_))
        ax.set_title(title, fontsize=8)
        ax.axis("off")
    fig.tight_layout(pad=0.4)
    save(fig, "captures.png")


for fn in (architecture, pyramide, pipeline, resultats, perf, zap, captures):
    fn()
print("Figures generees dans", IMG)
