#!/usr/bin/env python3
"""Consolide les resultats reels de reports/ dans reports/summary.json.

Les documents (plan de tests, rapport final) lisent uniquement ce fichier :
aucun chiffre n'est saisi a la main.
"""
import glob
import json
import os
import re
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS = os.path.join(ROOT, "reports")


def testng(path):
    root = ET.parse(path).getroot()
    suite = root.find("suite")
    methods = []
    for m in root.iter("test-method"):
        if m.get("is-config") == "true":
            continue
        methods.append({
            "name": m.get("name"),
            "description": m.get("description") or "",
            "status": m.get("status"),
            "duration_ms": int(m.get("duration-ms", "0")),
        })
    return {
        "total": int(root.get("total")), "passed": int(root.get("passed")),
        "failed": int(root.get("failed")), "skipped": int(root.get("skipped")),
        "duration_s": round(int(suite.get("duration-ms", "0")) / 1000, 1),
        "started": suite.get("started-at"),
        "methods": methods,
    }


def run_name(path, prefix):
    return re.sub(r"\.xml$", "", os.path.basename(path)[len(prefix):])


def newman(path):
    d = json.load(open(path, encoding="utf-8"))
    st = d["run"]["stats"]
    ex = d["run"]["executions"]
    times = [e["response"]["responseTime"] for e in ex if "response" in e]
    codes = [e["response"]["code"] for e in ex if "response" in e]
    return {
        "requests": st["requests"]["total"], "requests_failed": st["requests"]["failed"],
        "assertions": st["assertions"]["total"], "assertions_failed": st["assertions"]["failed"],
        "avg_response_ms": round(sum(times) / len(times), 1) if times else None,
        "max_response_ms": max(times) if times else None,
        "status_codes": codes,
        "duration_ms": d["run"]["timings"]["completed"] - d["run"]["timings"]["started"],
    }


def jmeter(run_dir):
    stats = json.load(open(os.path.join(run_dir, "dashboard", "statistics.json"), encoding="utf-8"))
    out = {}
    for label, s in stats.items():
        out[label] = {
            "samples": s["sampleCount"], "error_pct": round(s["errorPct"], 2),
            "avg_ms": round(s["meanResTime"], 1), "median_ms": round(s["medianResTime"], 1),
            "min_ms": s["minResTime"], "max_ms": s["maxResTime"],
            "p90_ms": s["pct1ResTime"], "p95_ms": s["pct2ResTime"], "p99_ms": s["pct3ResTime"],
            "throughput_rps": round(s["throughput"], 2),
        }
    # repartition des codes de reponse a partir du JTL (CSV)
    codes = {}
    jtl = os.path.join(run_dir, "resultats.jtl")
    if os.path.exists(jtl):
        import csv
        start, first429 = None, None
        with open(jtl, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = "%s %s" % (row["label"], row["responseCode"])
                codes[key] = codes.get(key, 0) + 1
                ts = int(row["timeStamp"])
                start = ts if start is None else min(start, ts)
                if row["responseCode"] == "429":
                    first429 = ts if first429 is None else min(first429, ts)
        if first429 is not None:
            out["_first_429_s"] = round((first429 - start) / 1000, 1)
    out["_codes"] = codes
    return out


def zap(path):
    d = json.load(open(path, encoding="utf-8"))
    alerts = []
    for site in d["site"]:
        for a in site["alerts"]:
            risk = a["riskdesc"].split(" ")[0]
            alerts.append({
                "name": a["name"], "risk": risk, "riskdesc": a["riskdesc"],
                "cwe": a.get("cweid"), "count": int(a["count"]), "pluginid": a["pluginid"],
                "uris": sorted({i["uri"] for i in a["instances"]})[:3],
            })
    order = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}
    alerts.sort(key=lambda a: (order.get(a["risk"], 9), a["name"]))
    by_risk = {}
    for a in alerts:
        by_risk[a["risk"]] = by_risk.get(a["risk"], 0) + 1
    return {"version": d.get("@version"), "generated": d.get("@generated"), "alerts": alerts, "by_risk": by_risk}


summary = {"ui": {}, "api": {}, "newman": {}, "perf": {}, "security": None}

for p in glob.glob(os.path.join(REPORTS, "ui", "testng-results-*.xml")):
    summary["ui"][run_name(p, "testng-results-")] = testng(p)
for p in glob.glob(os.path.join(REPORTS, "api", "testng-results-*.xml")):
    summary["api"][run_name(p, "testng-results-")] = testng(p)
for p in glob.glob(os.path.join(REPORTS, "api", "newman", "newman-*.json")):
    summary["newman"][re.sub(r"^newman-|\.json$", "", os.path.basename(p))] = newman(p)
for d in glob.glob(os.path.join(REPORTS, "perf", "*")):
    if os.path.exists(os.path.join(d, "dashboard", "statistics.json")):
        summary["perf"][os.path.basename(d)] = jmeter(d)
zp = os.path.join(REPORTS, "security", "zap-baseline.json")
if os.path.exists(zp):
    summary["security"] = zap(zp)

with open(os.path.join(REPORTS, "summary.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("reports/summary.json :", {k: list(v) if isinstance(v, dict) else bool(v) for k, v in summary.items()})
