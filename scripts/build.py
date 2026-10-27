"""Build the static site in docs/ from docs/data/latest.json + desk_estimates.json."""
import json, csv, os, sys, html, urllib.parse, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from products import PRODUCTS, HS_DESC

D = os.path.join(os.path.dirname(__file__), "..", "docs")
BASE = "https://nidhi-bhai.github.io/india-agri-export-prices/"
EMAIL = "nidhi69n@gmail.com"
S = json.load(open(os.path.join(D, "data", "latest.json")))
DESK = json.load(open(os.path.join(D, "data", "desk_estimates.json")))
FX = (S.get("fx") or {}).get("usd_inr")
CT_URL = "https://comtradeplus.un.org/TradeFlow?Frequency=M&Flows=X&CommodityCodes={h}&Partners=0&Reporters=699&AggregateBy=none&BreakdownMode=plus"
AGM_URL = "https://agmarknet.gov.in/"
e = html.escape

def per(p):  # 202607 -> Jul 2026
    p = str(p)
    if len(p) == 6: return dt.date(int(p[:4]), int(p[4:]), 1).strftime("%b %Y")
    return p

def num(x, d=2):
    return "" if x is None else f"{x:,.{d}f}"

def mailto(name):
    q = urllib.parse.urlencode({"subject": f"Quote request: {name}",
        "body": f"Product: {name}\nQuantity (kg or MT): \nDestination port: \nPacking / spec: \nSample needed (yes/no): \n"}, quote_via=urllib.parse.quote)
    return f"mailto:{EMAIL}?{q}"

CSS = """body{font:16px/1.55 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1c2a1f;margin:0;background:#fbfaf6}
.w{max-width:960px;margin:0 auto;padding:18px}header{background:#1f4d2b;color:#fff}header a{color:#fff;text-decoration:none}
header .w{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}nav a{margin-left:14px;font-size:14px;opacity:.9}
h1{font-size:28px;line-height:1.25;margin:18px 0 6px}h2{font-size:20px;margin-top:30px}.sub{color:#5b6b5e;margin:0 0 14px}
table{border-collapse:collapse;width:100%;font-size:14px;background:#fff}th,td{border-bottom:1px solid #e6e3d8;padding:7px 8px;text-align:left;vertical-align:top}
th{background:#f1efe6;font-weight:600}td.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}.tag{font-size:11px;padding:1px 6px;border-radius:8px;white-space:nowrap}
.off{background:#e3f1e6;color:#1f4d2b}.est{background:#fff1d6;color:#7a4b00}.cta{background:#1f4d2b;color:#fff;border-radius:10px;padding:16px 18px;margin:22px 0}
.cta a.b{display:inline-block;background:#f2b33d;color:#1c2a1f;font-weight:700;padding:9px 16px;border-radius:8px;text-decoration:none;margin-top:8px}
.note{font-size:13px;color:#5b6b5e}.warn{background:#fff7e6;border-left:4px solid #f2b33d;padding:8px 12px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:10px}.card{background:#fff;border:1px solid #e6e3d8;border-radius:8px;padding:12px}
.card a{font-weight:600;color:#1f4d2b}footer{border-top:1px solid #e6e3d8;margin-top:40px;font-size:13px;color:#5b6b5e}a{color:#1f6b3a}"""

def page(title, desc, path, body, ld=None):
    canon = BASE + path
    ldj = f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website">
<style>{CSS}</style>{ldj}</head><body>
<header><div class="w"><a href="{BASE}"><b>India Agri Export Price Index</b></a><nav><a href="{BASE}">Products</a><a href="{BASE}methodology.html">Methodology</a><a href="{BASE}data/latest.csv">CSV</a><a href="{BASE}data/latest.json">JSON</a></nav></div></header>
<main class="w">{body}</main>
<footer><div class="w">Free, open data. Published by <b>Nidhi Farms</b>, a sourcing firm (trader, not a grower) in Andhra Pradesh, India. Conventional grade only; we do not sell certified organic.
Data snapshot {S['snapshot_date']}; refreshed weekly. Official statistics belong to their publishers (UN Comtrade, Agmarknet/Govt. of India, ECB); our own figures are labelled <i>estimate</i>.
Licence: data CC BY 4.0, code MIT. <a href="https://github.com/Nidhi-bhai/india-agri-export-prices">Source on GitHub</a>.
More open datasets by the same author: <a href="https://nidhi-bhai.github.io/pdufa-calendar/">PDUFA / FDA catalyst calendar</a>.</div></footer></body></html>"""

def cta(name):
    return f"""<div class="cta"><b>Need a firm quote or a sample of {e(name.lower())}?</b><br>
Email <b>{EMAIL}</b> with product, quantity and destination port. We reply with a per-kg FOB/CIF price that includes everything.
<br><a class="b" href="{e(mailto(name))}">Request a quote: {e(name)}</a>
<div class="note" style="color:#d9e8dc;margin-top:6px">Nidhi Farms, sourcing firm, Andhra Pradesh, India. Trader, conventional grade. Prices on this page are reference data, not offers.</div></div>"""

def spark(vals):
    v = [x for x in vals if x is not None]
    if len(v) < 2: return ""
    lo, hi = min(v), max(v); rng = (hi - lo) or 1; W, H = 220, 40
    pts = " ".join(f"{i*W/(len(vals)-1):.1f},{H-(x-lo)/rng*(H-4)-2:.1f}" for i, x in enumerate(vals) if x is not None)
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="trend"><polyline fill="none" stroke="#1f6b3a" stroke-width="2" points="{pts}"/></svg>'

def agm_latest(a):
    for k in ("price_rs_q", "prev1_rs_q", "prev2_rs_q"):
        if a.get(k): return a[k], {"price_rs_q": 0, "prev1_rs_q": 1, "prev2_rs_q": 2}[k]
    return None, None

def product_rows(p):
    """Return list of flat metric rows (also used for CSV)."""
    rows = []
    for h in p["hs"]:
        m = S["comtrade_monthly"].get(h) or []
        if m:
            r = m[0]
            rows.append(dict(product=p["name"], slug=p["slug"], metric=f"India export unit value, HS {h}" + (" (pooled category)" if p["pooled"] else ""),
                value=r["usd_per_kg"], unit="USD/kg", period=per(r["period"]), source="UN Comtrade (monthly, India reporter, FOB value / net weight)",
                source_url=CT_URL.format(h=h), type="official statistic"))
            vals = [x["usd_per_kg"] for x in m if x["usd_per_kg"] is not None]
            if len(vals) >= 3:
                rows.append(dict(product=p["name"], slug=p["slug"], metric=f"12-month range of monthly unit value, HS {h}",
                    value=f"{min(vals):.2f}–{max(vals):.2f}", unit="USD/kg", period=f"{per(m[-1]['period'])} – {per(m[0]['period'])}",
                    source="UN Comtrade", source_url=CT_URL.format(h=h), type="official statistic"))
    for cid, label in p["agm"]:
        a = S["agmarknet"].get(str(cid))
        if not a: continue
        v, lag = agm_latest(a)
        if v is None: continue
        d = a["reported_date"]
        try:
            d0 = dt.datetime.strptime(d, "%d-%m-%Y").date() - dt.timedelta(days=lag); d = d0.isoformat()
        except Exception: pass
        rows.append(dict(product=p["name"], slug=p["slug"], metric=f"Mandi price, all-India average: {label}", value=v, unit="INR/quintal",
            period=d, source="Agmarknet, Govt. of India (marketwise price dashboard)", source_url=AGM_URL, type="official statistic",
            note=f"arrivals that day: {a.get(['arrival_t','prev1_arrival_t','prev2_arrival_t'][lag])} t"))
        if FX:
            rows.append(dict(product=p["name"], slug=p["slug"], metric=f"Same mandi price in USD/kg: {label}", value=round(v / 100 / FX, 3), unit="USD/kg",
                period=d, source=f"Calculated: Agmarknet price ÷ 100 ÷ USD/INR {FX} ({S['fx']['date']}, ECB)", source_url=AGM_URL,
                type="calculated (raw farm-gate commodity, not export-ready)"))
    if p["desk"] and p["desk"] in DESK["items"]:
        k = DESK["items"][p["desk"]]
        val = f"{k['low']:.2f}" if k["low"] == k["high"] else f"{k['low']:.2f}–{k['high']:.2f}"
        rows.append(dict(product=p["name"], slug=p["slug"], metric="Indicative export FOB range seen in public offers", value=val, unit="USD/kg",
            period=f"compiled {DESK['compiled']}", source="Nidhi Farms desk research: " + k["basis"], source_url=k["sources"][0], type="ESTIMATE"))
    return rows

def table(rows):
    if not rows:
        return '<p class="warn">No public price series we trust is available for this product yet. We leave it empty rather than guess. Email us for a live quote.</p>'
    t = ["<table><tr><th>Metric</th><th>Value</th><th>Unit</th><th>Period / date</th><th>Source</th></tr>"]
    for r in rows:
        cls = "est" if "ESTIMATE" in r["type"] or "calculated" in r["type"] else "off"
        v = r["value"] if isinstance(r["value"], str) else num(r["value"], 3 if r["unit"] == "USD/kg" else 2)
        t.append(f'<tr><td>{e(r["metric"])} <span class="tag {cls}">{e(r["type"])}</span>{("<br><span class=note>"+e(r["note"])+"</span>") if r.get("note") else ""}</td>'
                 f'<td class="n"><b>{e(str(v))}</b></td><td>{e(r["unit"])}</td><td>{e(str(r["period"]))}</td><td><a href="{e(r["source_url"])}" rel="nofollow">{e(r["source"])}</a></td></tr>')
    t.append("</table>")
    return "".join(t)

def trend(h):
    m = S["comtrade_monthly"].get(h) or []
    if not m: return ""
    m = list(reversed(m))
    rows = "".join(f'<tr><td>{per(x["period"])}</td><td class="n">{num(x["usd_per_kg"],3)}</td><td class="n">{num((x["net_kg"] or 0)/1000,0)}</td><td class="n">{num((x["value_usd"] or 0)/1e6,2)}</td></tr>' for x in m)
    return (f'<h3>HS {h}: India monthly exports, last {len(m)} months available {spark([x["usd_per_kg"] for x in m])}</h3>'
            f'<p class="note">{e(HS_DESC.get(h,""))}. Source: <a href="{CT_URL.format(h=h)}" rel="nofollow">UN Comtrade</a>. Comtrade publishes with a lag of a few months.</p>'
            f'<table><tr><th>Month</th><th>Unit value USD/kg</th><th>Net weight, tonnes</th><th>Value, USD million</th></tr>{rows}</table>')

def dests(h):
    d = S["comtrade_destinations"].get(h)
    if not d: return ""
    rows = "".join(f'<tr><td>{e(str(x["country"]))}</td><td class="n">{num(x["value_usd"]/1e6,2)}</td><td class="n">{num((x["net_kg"] or 0)/1000,0)}</td><td class="n">{num(x["usd_per_kg"],3)}</td></tr>' for x in d["top"])
    return (f'<h3>Top destinations for India HS {h}, {d["year"]}</h3><table><tr><th>Importing country</th><th>USD million</th><th>Tonnes</th><th>Unit value USD/kg</th></tr>{rows}</table>'
            f'<p class="note">Source: UN Comtrade annual data, India as reporter.</p>')

def faq(p, rows):
    ct = next((r for r in rows if r["unit"] == "USD/kg" and r["type"] == "official statistic" and "12-month" not in r["metric"]), None)
    est = next((r for r in rows if r["type"] == "ESTIMATE"), None)
    qa = []
    a = []
    if est: a.append(f"Public export offers we have seen range {est['value']} USD/kg FOB (estimate, {est['period']}).")
    if ct: a.append(f"India's official export unit value for {ct['metric'].split(', ')[-1]} was {num(ct['value'],2)} USD/kg in {ct['period']} (UN Comtrade){' — a pooled customs category, so treat it as context, not a product price' if p['pooled'] else ''}.")
    if not a: a.append("There is no reliable public price series for this product yet, so we publish none. Ask for a live quote instead.")
    a.append("Firm prices depend on grade, quantity, packing and destination; email for a quote.")
    qa.append((f"What is the export price of {p['name'].lower()} from India?", " ".join(a)))
    qa.append(("How often is this page updated?", "Every week, automatically. Each weekly snapshot is appended to a public history file, so the series grows over time."))
    qa.append(("Is Nidhi Farms a grower or certified organic?", "Neither. Nidhi Farms is a sourcing firm (trader) in Andhra Pradesh, India, supplying conventional-grade product with lab testing arranged on request."))
    body = "".join(f"<h3>{e(q)}</h3><p>{e(t)}</p>" for q, t in qa)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in qa]}
    return body, ld

def build():
    all_rows = []
    cards = []
    for p in PRODUCTS:
        rows = product_rows(p); all_rows += rows
        title = f"{p['name']} export price from India (USD/kg), updated weekly"
        head = next((r for r in rows if r["type"] == "ESTIMATE"), None) or next((r for r in rows if r["unit"] == "USD/kg"), None)
        desc = (f"{p['name']} export price from India: " + (f"{head['value']} USD/kg ({head['type']}, {head['period']}). " if head else "")
                + "Official UN Comtrade and Agmarknet data with sources, weekly history, free CSV/JSON.")
        fq, ld = faq(p, rows)
        others = " · ".join(f'<a href="{q["slug"]}.html">{e(q["name"])}</a>' for q in PRODUCTS if q is not p)
        pooled = (f'<p class="warn">HS code {", ".join(p["hs"])} is a pooled customs category: it mixes {e(p["name"].lower())} with other goods. '
                  'Its unit value is context for the market, not the price of this exact product.</p>') if p["pooled"] and p["hs"] else ""
        body = (f'<h1>{e(title)}</h1><p class="sub">Snapshot {S["snapshot_date"]}. Every number shows its source and date. Green = official statistic; amber = estimate or our calculation.</p>'
                + cta(p["name"]) + "<h2>Latest prices</h2>" + pooled + table(rows)
                + "".join(trend(h) + dests(h) for h in p["hs"])
                + "<h2>Questions</h2>" + fq + cta(p["name"])
                + f'<h2>Other products</h2><p>{others}</p><p class="note">Download: <a href="data/latest.csv">latest.csv</a> · <a href="data/latest.json">latest.json</a> · <a href="data/history.csv">history.csv</a> · <a href="methodology.html">methodology</a></p>')
        dl = {"@context": "https://schema.org", "@type": "Dataset", "name": title, "description": desc, "url": BASE + f"p/{p['slug']}.html",
              "license": "https://creativecommons.org/licenses/by/4.0/", "creator": {"@type": "Organization", "name": "Nidhi Farms"},
              "dateModified": S["snapshot_date"], "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": BASE + "data/latest.csv"}]}
        open(os.path.join(D, "p", p["slug"] + ".html"), "w").write(page(title, desc, f"p/{p['slug']}.html", body.replace('href="data/', 'href="../data/').replace('href="methodology', 'href="../methodology'), [dl, ld]))
        n_off = sum(1 for r in rows if r["type"] == "official statistic")
        cards.append(f'<div class="card"><a href="p/{p["slug"]}.html">{e(p["name"])}</a><br><span class="note">'
                     + (f'{e(str(head["value"]))} {head["unit"]} <span class="tag {"est" if head["type"]!="official statistic" else "off"}">{e(head["type"])}{" · pooled HS code" if (p["pooled"] and head["type"]=="official statistic") else ""}</span>' if head else "no reliable public price yet")
                     + f'<br>{n_off} official series</span></div>')
    # CSV / JSON downloads
    cols = ["product", "slug", "metric", "value", "unit", "period", "source", "source_url", "type", "note"]
    with open(os.path.join(D, "data", "latest.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for r in all_rows: w.writerow({k: r.get(k, "") for k in cols})
    json.dump({"snapshot_date": S["snapshot_date"], "fx": S.get("fx"), "rows": all_rows}, open(os.path.join(D, "data", "index.json"), "w"), indent=1)
    # index
    body = (f'<h1>India Agri Export Price Index</h1><p class="sub">Free weekly reference prices for {len(PRODUCTS)} Indian agri exports — herbs, spices, jaggery, millets, cold-pressed oils and roots. '
            f'Official data from UN Comtrade and Agmarknet, plus clearly-labelled estimates. Snapshot {S["snapshot_date"]}.</p>'
            + f'<div class="grid">{"".join(cards)}</div>' + cta("Indian agri products")
            + '<h2>What this is</h2><p>Buyers and importers ask the same question every week: "what does this cost from India right now?" Public data exists but is scattered across UN Comtrade, government mandi dashboards and seller listings. '
              'This index pulls it together once a week, shows the source and date beside every number, and never fills a gap with a guess. Each weekly snapshot is appended to <a href="data/history.csv">history.csv</a>, so the record gets longer every week.</p>'
            + '<h2>Downloads</h2><ul><li><a href="data/latest.csv">latest.csv</a> — every metric on this site, flat</li><li><a href="data/latest.json">latest.json</a> — raw weekly snapshot</li><li><a href="data/index.json">index.json</a> — the rows behind the pages</li><li><a href="data/history.csv">history.csv</a> — append-only weekly history</li></ul>'
            + '<p><a href="methodology.html">Read the methodology</a> (plain English).</p>')
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "India Agri Export Price Index", "url": BASE, "license": "https://creativecommons.org/licenses/by/4.0/",
          "description": "Weekly reference export prices (USD/kg) and mandi prices (INR/quintal) for Indian agri products, from UN Comtrade and Agmarknet.",
          "creator": {"@type": "Organization", "name": "Nidhi Farms"}, "dateModified": S["snapshot_date"],
          "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": BASE + "data/latest.csv"}, {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": BASE + "data/history.csv"}]}
    open(os.path.join(D, "index.html"), "w").write(page("India Agri Export Price Index: moringa, turmeric, millets, jaggery, oils (USD/kg, weekly)",
        "Free weekly export prices from India for moringa, ashwagandha, turmeric, jaggery, millets, cold-pressed oils and vetiver. Sourced from UN Comtrade and Agmarknet. CSV/JSON.", "", body, ld))
    meth = f"""<h1>Methodology</h1><p class="sub">How every number on this site is produced, in plain English.</p>
<h2>1. Official export statistics (UN Comtrade)</h2><p>India reports its exports to the UN every month by customs code (HS code). We take the value (USD, FOB) and the net weight (kg) and divide one by the other. That gives a <b>unit value</b> in USD/kg: the average price of everything India shipped under that code that month. Comtrade publishes with a lag of a few months, so the latest month is usually 2–4 months old. Many of our products share a code with other goods (e.g. HS 121190 covers moringa, ashwagandha, neem, vetiver and hundreds of other herbs). We mark those as <b>pooled</b>: useful as market context, not as the price of the exact product. We use the free public Comtrade preview API.</p>
<h2>2. Indian wholesale mandi prices (Agmarknet)</h2><p>The Government of India's Agmarknet portal publishes daily all-India average prices (INR per quintal = 100 kg) and arrivals for commodities traded in regulated markets (APMCs). These are <b>raw, farm-gate commodity prices</b> (e.g. turmeric fingers, jaggery blocks, millet grain) before cleaning, grading, grinding, packing, testing and port costs, so they sit well below export prices. We show the latest day reported and the arrivals that day; low arrivals mean a thin, noisy price. The USD/kg conversion uses the European Central Bank USD/INR reference rate (via frankfurter.dev).</p>
<h2>3. Estimates (labelled ESTIMATE)</h2><p>For powders and niche items there is no official price series. Our desk compiles ranges from public seller offers, rate cards and trade reports, with links. These are asks, not transaction prices. We only publish ranges for products where the export economics are positive; we do not publish a figure where we have no source.</p>
<h2>4. Empty cells</h2><p>If a source has no data for a product this week, the cell stays empty. We never interpolate or invent.</p>
<h2>5. Weekly refresh and history</h2><p>A scheduled job runs once a week, fetches every source again, rebuilds the pages and <b>appends</b> the new snapshot to <a href="data/history.csv">history.csv</a>. Old rows are never rewritten. If a source is down, the previous values are kept and marked stale in latest.json.</p>
<h2>6. Who publishes this</h2><p>Nidhi Farms, a sourcing firm (trader) in Andhra Pradesh, India. We are not a grower and we do not sell certified organic product. Correspondence: c/o GITAM Post Office, Back Gate, Visakhapatnam 530045, India. Questions or corrections: <a href="mailto:{EMAIL}?subject=Price%20index%20correction">{EMAIL}</a>.</p>"""
    open(os.path.join(D, "methodology.html"), "w").write(page("Methodology: India Agri Export Price Index", "How the India Agri Export Price Index is built: UN Comtrade unit values, Agmarknet mandi prices, labelled estimates, weekly history.", "methodology.html", meth))
    urls = [BASE, BASE + "methodology.html"] + [BASE + f"p/{p['slug']}.html" for p in PRODUCTS]
    open(os.path.join(D, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{u}</loc><lastmod>{S['snapshot_date']}</lastmod><changefreq>weekly</changefreq></url>" for u in urls) + "</urlset>\n")
    open(os.path.join(D, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    open(os.path.join(D, ".nojekyll"), "w").write("")
    print("built", len(PRODUCTS), "product pages,", len(all_rows), "rows")

if __name__ == "__main__":
    build()
