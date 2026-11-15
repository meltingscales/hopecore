#!/usr/bin/env python3
"""Ledger tools for hopecore.html (standard library only).

The ledger lives inside hopecore.html in
<script type="application/json" id="hopecore-data">. The page's renderer
(CSS + JS) also lives in that file, so hopecore.html is the only source of
truth: these tools pull the ledger out, put it back, and check it.

Usage:
  python3 tools/hopecore.py extract [-o ledger.json]   # write ledger JSON (default: stdout)
  python3 tools/hopecore.py embed ledger.json          # replace the ledger inside hopecore.html
  python3 tools/hopecore.py check [--against REF]      # validate; compare with git REF (default HEAD)
  python3 tools/hopecore.py stats                      # print scorecard counts

All commands take --html PATH (default: hopecore.html next to tools/).
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HTML = ROOT / "hopecore.html"
BLOCK_RE = re.compile(
    r'(<script type="application/json" id="hopecore-data">)(.*?)(</script>)', re.S
)

STATUSES = {"confirmed", "early", "on-track", "pending", "slipping", "missed", "superseded"}
KINDS = {"capability", "deployment", "impact"}
SIGNIFICANCE = {"first-ever", "major", "notable"}
SEVERITY = {"high", "medium", "low"}
TRENDS = {"worsening", "stable", "easing"}
CONFIDENCE = {"high", "medium", "low"}
SOURCE_TYPES = {"primary", "secondary"}
TOP_KEYS = ["meta", "metrics", "predictions", "milestones", "roadblocks", "sources", "changelog"]
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def parse_ledger(html):
    m = BLOCK_RE.search(html)
    if not m:
        raise SystemExit('error: no <script type="application/json" id="hopecore-data"> block found')
    if len(BLOCK_RE.findall(html)) != 1:
        raise SystemExit("error: ledger block must appear exactly once")
    return json.loads(m.group(2))


def load(path):
    return parse_ledger(Path(path).read_text(encoding="utf-8"))


def dump_for_html(ledger):
    # Escape "</" so nothing inside a string can close the <script> tag.
    return json.dumps(ledger, ensure_ascii=False, indent=1).replace("</", "<\\/")


def cmd_extract(args):
    text = json.dumps(load(args.html), ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def cmd_embed(args):
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    html_path = Path(args.html)
    html = html_path.read_text(encoding="utf-8")
    parse_ledger(html)  # make sure exactly one block exists
    new = BLOCK_RE.sub(lambda m: m.group(1) + "\n" + dump_for_html(ledger) + "\n" + m.group(3), html)
    if parse_ledger(new) != ledger:
        raise SystemExit("error: round-trip mismatch after embedding")
    html_path.write_text(new, encoding="utf-8")
    print(f"embedded {args.ledger} into {html_path}")


def scorecard(ledger):
    preds = ledger["predictions"]
    counts = Counter(p["status"] for p in preds)
    hits = counts["confirmed"] + counts["early"]
    hit_rate = f"{round(100 * hits / (hits + counts['missed']))}%" if hits + counts["missed"] else "n/a"
    new_ms = sum(1 for m in ledger["milestones"] if m.get("added") == ledger["meta"]["last_run"])
    per_domain = {}
    for p in preds:
        per_domain.setdefault(p["domain"], Counter())[p["status"]] += 1
    return counts, hit_rate, new_ms, per_domain


def cmd_stats(args):
    ledger = load(args.html)
    counts, hit_rate, new_ms, per_domain = scorecard(ledger)
    print(f"last_run {ledger['meta']['last_run']}  run #{ledger['meta']['run_count']}")
    print("  ".join(f"{s}={counts[s]}" for s in sorted(STATUSES)))
    print(f"hit rate {hit_rate}   new milestones this run {new_ms}")
    for dom, c in sorted(per_domain.items()):
        print(f"  {dom:14} " + " ".join(f"{s}={n}" for s, n in sorted(c.items())))


def git_show(ref, html_path):
    try:
        rel = Path(html_path).resolve().relative_to(ROOT)
    except ValueError:  # file outside the repo: compare with the tracked hopecore.html
        rel = DEFAULT_HTML.relative_to(ROOT)
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{ref}:{rel.as_posix()}"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out.stdout


def cmd_check(args):
    errors, warnings = [], []
    err = errors.append
    warn = warnings.append

    try:
        L = load(args.html)
    except json.JSONDecodeError as e:
        raise SystemExit(f"FAIL: ledger JSON does not parse: {e}")

    for k in TOP_KEYS:
        if k not in L:
            err(f"missing top-level key '{k}'")
    if errors:
        return report(errors, warnings)

    meta = L["meta"]
    for k in ("version", "created", "last_run", "run_count"):
        if k not in meta:
            err(f"meta.{k} missing")

    src_ids = [s["id"] for s in L["sources"]]
    src_set = set(src_ids)

    def unique(kind, items):
        c = Counter(x["id"] for x in items)
        for i, n in c.items():
            if n > 1:
                err(f"duplicate {kind} id '{i}'")

    for kind in ("metrics", "predictions", "milestones", "roadblocks", "sources"):
        unique(kind, L[kind])

    domains = {d["id"] for d in L.get("domains", [])}

    def refs(where, ids):
        for i in ids or []:
            if i not in src_set:
                err(f"{where}: unknown source '{i}'")

    def date_ok(where, d):
        if not isinstance(d, str) or not DATE_RE.match(d):
            err(f"{where}: bad date '{d}' (want YYYY, YYYY-MM or YYYY-MM-DD)")

    def domain_ok(where, d):
        if domains and d not in domains:
            err(f"{where}: unknown domain '{d}'")

    for s in L["sources"]:
        for k in ("title", "publisher", "url", "published", "accessed", "type"):
            if not s.get(k):
                err(f"source {s['id']}: missing {k}")
        if s.get("type") not in SOURCE_TYPES:
            err(f"source {s['id']}: type must be primary|secondary")
        if not str(s.get("url", "")).startswith("http"):
            err(f"source {s['id']}: url must be http(s)")

    for m in L["metrics"]:
        domain_ok(f"metric {m['id']}", m.get("domain"))
        if not m.get("series"):
            err(f"metric {m['id']}: empty series")
        for p in m.get("series", []):
            date_ok(f"metric {m['id']}", p.get("date"))
            if not isinstance(p.get("value"), (int, float)):
                err(f"metric {m['id']}: non-numeric value {p.get('value')!r}")
            if not p.get("source_ids"):
                err(f"metric {m['id']} @ {p.get('date')}: no source")
            refs(f"metric {m['id']}", p.get("source_ids"))
            if m.get("log") and isinstance(p.get("value"), (int, float)) and p["value"] <= 0:
                err(f"metric {m['id']}: log scale needs values > 0")

    pred_ids = set()
    for p in L["predictions"]:
        w = f"prediction {p['id']}"
        pred_ids.add(p["id"])
        domain_ok(w, p.get("domain"))
        if p.get("status") not in STATUSES:
            err(f"{w}: bad status '{p.get('status')}'")
        if p.get("kind") not in KINDS:
            err(f"{w}: bad kind '{p.get('kind')}'")
        if p.get("confidence") not in CONFIDENCE:
            err(f"{w}: bad confidence '{p.get('confidence')}'")
        if not isinstance(p.get("year"), int):
            err(f"{w}: year must be an integer")
        hist = p.get("history") or []
        if not hist:
            err(f"{w}: empty history")
            continue
        if hist[-1].get("status") != p.get("status"):
            err(f"{w}: status '{p.get('status')}' != last history status '{hist[-1].get('status')}'")
        for h in hist:
            date_ok(w, h.get("date"))
            refs(w, h.get("source_ids"))
            if h.get("status") not in STATUSES:
                err(f"{w}: bad history status '{h.get('status')}'")
        for prev, cur in zip(hist, hist[1:]):
            if prev["status"] != cur["status"] and not cur.get("source_ids"):
                err(f"{w}: status change on {cur.get('date')} has no source")
            if prev["status"] != cur["status"] and not cur.get("reason"):
                err(f"{w}: status change on {cur.get('date')} has no reason")
        last = hist[-1]
        if p.get("status") != "pending" and not last.get("source_ids"):
            err(f"{w}: non-pending status needs a source")
        if p.get("status") in ("confirmed", "missed", "early"):
            types = [next((s["type"] for s in L["sources"] if s["id"] == i), None) for i in last.get("source_ids", [])]
            if "primary" not in types and types.count("secondary") < 2:
                err(f"{w}: {p['status']} needs one primary or two secondary sources")
        if p.get("status") == "early" and not p.get("years_early"):
            warn(f"{w}: early without years_early")
        if p.get("status") == "missed" and isinstance(p.get("year"), int) and p["year"] >= int(meta["last_run"][:4]):
            err(f"{w}: missed before its target year has passed")

    for m in L["milestones"]:
        w = f"milestone {m['id']}"
        domain_ok(w, m.get("domain"))
        date_ok(w, m.get("date"))
        if m.get("kind") not in KINDS:
            err(f"{w}: bad kind '{m.get('kind')}'")
        if m.get("significance") not in SIGNIFICANCE:
            err(f"{w}: bad significance '{m.get('significance')}'")
        if not m.get("source_ids"):
            err(f"{w}: no source")
        refs(w, m.get("source_ids"))
        for pid in m.get("confirms_prediction_ids", []):
            if pid not in pred_ids:
                err(f"{w}: confirms unknown prediction '{pid}'")

    for r in L["roadblocks"]:
        w = f"roadblock {r['id']}"
        domain_ok(w, r.get("domain"))
        if r.get("severity") not in SEVERITY:
            err(f"{w}: bad severity")
        if r.get("trend") not in TRENDS:
            err(f"{w}: bad trend")
        if not r.get("source_ids"):
            err(f"{w}: no source")
        refs(w, r.get("source_ids"))

    refs("meta.summary", meta.get("summary_source_ids"))
    for d in L.get("domains", []):
        if not d.get("read"):
            err(f"domain {d['id']}: missing realistic read")
        if not any(r["domain"] == d["id"] for r in L["roadblocks"]):
            err(f"domain {d['id']}: no roadblocks (every domain card needs a Roadblocks panel)")

    if not any(c.get("date") == meta.get("last_run") for c in L["changelog"]):
        err(f"no changelog entry dated meta.last_run ({meta.get('last_run')})")

    used = set()
    for k in ("metrics", "predictions", "milestones", "roadblocks"):
        for x in L[k]:
            used.update(x.get("source_ids", []))
            for p in x.get("series", []):
                used.update(p.get("source_ids", []))
            for h in x.get("history", []):
                used.update(h.get("source_ids", []))
    used.update(meta.get("summary_source_ids", []))
    for s in src_set - used:
        warn(f"source {s} is never cited")

    # History rules: compare with the committed version.
    old_html = git_show(args.against, args.html)
    if old_html is None:
        warn(f"could not read hopecore.html at git ref '{args.against}'; skipped history comparison")
    else:
        old = parse_ledger(old_html)
        new_preds = {p["id"]: p for p in L["predictions"]}
        for op in old["predictions"]:
            np_ = new_preds.get(op["id"])
            w = f"prediction {op['id']}"
            if np_ is None:
                err(f"{w}: deleted (predictions must never be removed)")
                continue
            for k in ("text", "year", "domain", "origin"):
                if np_.get(k) != op.get(k):
                    err(f"{w}: '{k}' changed from {op.get(k)!r} to {np_.get(k)!r} (add a revised prediction instead)")
            oh, nh = op.get("history", []), np_.get("history", [])
            if nh[: len(oh)] != oh:
                err(f"{w}: earlier history entries were edited or removed")
        new_ms = {m["id"] for m in L["milestones"]}
        for m in old["milestones"]:
            if m["id"] not in new_ms:
                err(f"milestone {m['id']}: deleted")
        new_rb = {r["id"] for r in L["roadblocks"]}
        for r in old["roadblocks"]:
            if r["id"] not in new_rb:
                err(f"roadblock {r['id']}: deleted")
        if len(L["changelog"]) < len(old["changelog"]) or L["changelog"][: len(old["changelog"])] != old["changelog"]:
            err("changelog: earlier entries were edited or removed")
        if L != old:
            if meta["run_count"] <= old["meta"]["run_count"]:
                err(f"meta.run_count not incremented (was {old['meta']['run_count']}, now {meta['run_count']})")
            if meta["last_run"] <= old["meta"]["last_run"] and meta["run_count"] != old["meta"]["run_count"]:
                warn(f"meta.last_run not advanced (was {old['meta']['last_run']})")

    counts, hit_rate, new_ms_count, _ = scorecard(L)
    print("scorecard: " + "  ".join(f"{s}={counts[s]}" for s in ("confirmed", "early", "on-track", "slipping", "missed", "pending", "superseded"))
          + f"  hit_rate={hit_rate}  new_milestones={new_ms_count}")
    return report(errors, warnings)


def report(errors, warnings):
    for w in warnings:
        print(f"warn: {w}")
    for e in errors:
        print(f"FAIL: {e}")
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html", default=str(DEFAULT_HTML), help="path to hopecore.html")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract", help="print or save the ledger JSON")
    e.add_argument("-o", "--out")
    b = sub.add_parser("embed", help="write a ledger JSON file back into hopecore.html")
    b.add_argument("ledger")
    c = sub.add_parser("check", help="validate the ledger (section 8 self-check)")
    c.add_argument("--against", default="HEAD", help="git ref to compare history against (default HEAD)")
    sub.add_parser("stats", help="print scorecard counts")
    args = ap.parse_args()
    rc = {"extract": cmd_extract, "embed": cmd_embed, "check": cmd_check, "stats": cmd_stats}[args.cmd](args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
