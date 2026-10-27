"""Weekly fetch: UN Comtrade (India exports, monthly unit values + annual top destinations),
Agmarknet all-India average mandi prices, and the USD/INR reference rate.
Writes docs/data/latest.json and appends to docs/data/history.csv (never rewrites old rows).
Free, keyless public endpoints only."""
import json, csv, os, sys, time, datetime as dt, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
from products import PRODUCTS, HS_DESC

ROOT = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
TODAY = dt.date.today()
UA = {"User-Agent": "india-agri-export-prices/1.0 (+https://nidhi-bhai.github.io/india-agri-export-prices/)"}

def get(url, tries=4, wait=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            print("  retry", i + 1, url[:110], e, file=sys.stderr)
            time.sleep(wait * (i + 1))
    return None

HS = sorted({h for p in PRODUCTS for h in p["hs"]})
CT = "https://comtradeapi.un.org/public/v1/preview/C/{freq}/HS?reporterCode=699&period={per}&cmdCode={cmd}&flowCode=X&partnerCode={partner}&includeDesc=true"

def ct_rows(d):
    return [r for r in (d or {}).get("data", []) if r.get("motCode") == 0 and r.get("customsCode") == "C00" and str(r.get("partner2Code")) == "0"]

def uv(r):
    v, w = r.get("primaryValue"), r.get("netWgt")
    return round(v / w, 3) if v and w else None

def comtrade_monthly(n_months=12, lookback=24):
    out = {h: [] for h in HS}
    y, m = TODAY.year, TODAY.month
    got = 0
    for _ in range(lookback):
        m -= 1
        if m == 0: y, m = y - 1, 12
        per = f"{y}{m:02d}"
        d = get(CT.format(freq="M", per=per, cmd=",".join(HS), partner="0"))
        time.sleep(2)
        rows = ct_rows(d)
        if not rows:
            if got: break
            continue
        got += 1
        for r in rows:
            out[r["cmdCode"]].append(dict(period=per, value_usd=r.get("primaryValue"), net_kg=r.get("netWgt"), usd_per_kg=uv(r)))
        if got >= n_months: break
    return out

def comtrade_destinations():
    out = {}
    for h in HS:
        for yr in (TODAY.year - 1, TODAY.year - 2):
            d = get(CT.format(freq="A", per=yr, cmd=h, partner="").replace("&partnerCode=", ""))
            time.sleep(2)
            rows = [r for r in ct_rows(d) if r.get("partnerCode") not in (0, None)]
            if rows:
                rows.sort(key=lambda r: -(r.get("primaryValue") or 0))
                out[h] = dict(year=yr, top=[dict(country=r.get("partnerDesc"), value_usd=round(r.get("primaryValue") or 0),
                              net_kg=r.get("netWgt"), usd_per_kg=uv(r)) for r in rows[:8]])
                break
    return out

AGM = "https://api.agmarknet.gov.in/v1/dashboard-data/?dashboard=marketwise_price_arrival&date={date}&commodity=%5B{cid}%5D&limit=10&page=1"

def f(x):
    try: return float(x)
    except Exception: return None

def agmarknet():
    out = {}
    ids = sorted({cid for p in PRODUCTS for cid, _ in p["agm"]})
    for cid in ids:
        rec = None
        for back in range(0, 5):
            date = (TODAY - dt.timedelta(days=back)).isoformat()
            d = get(AGM.format(date=date, cid=cid), tries=3)
            time.sleep(1)
            recs = ((d or {}).get("data") or {}).get("records") if isinstance((d or {}).get("data"), dict) else None
            if recs:
                rec = recs[0]; rec["_query_date"] = date; break
        if not rec:
            continue
        prices = [f(rec.get(k)) for k in ("as_on_price", "one_day_ago_price", "two_day_ago_price")]
        arr = [f(rec.get(k)) for k in ("as_on_arrival", "one_day_ago_arrival", "two_day_ago_arrival")]
        pw = [(p, a) for p, a in zip(prices, arr) if p and a]
        wavg = round(sum(p * a for p, a in pw) / sum(a for _, a in pw), 2) if pw else None
        out[str(cid)] = dict(name=rec.get("cmdt_name"), reported_date=rec.get("reported_date"),
            price_rs_q=prices[0], prev1_rs_q=prices[1], prev2_rs_q=prices[2],
            arrival_t=arr[0], prev1_arrival_t=arr[1], prev2_arrival_t=arr[2],
            three_day_arrival_weighted_rs_q=wavg, msp_rs_q=f(rec.get("msp_price")), trend=rec.get("trend"))
    return out

def fx():
    d = get("https://api.frankfurter.dev/v1/latest?base=USD&symbols=INR")
    if d and d.get("rates", {}).get("INR"):
        return dict(usd_inr=d["rates"]["INR"], date=d.get("date"), source="Frankfurter (European Central Bank reference rate)", url="https://api.frankfurter.dev/v1/latest?base=USD&symbols=INR")
    return None

def main():
    snap = dict(snapshot_date=TODAY.isoformat(), generated_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                fx=fx(), comtrade_monthly=comtrade_monthly(), comtrade_destinations=comtrade_destinations(),
                agmarknet=agmarknet(), hs_desc=HS_DESC)
    prev = {}
    lp = os.path.join(ROOT, "latest.json")
    if os.path.exists(lp):
        prev = json.load(open(lp))
    # keep last good values if a source is down this week (marked stale by its own date)
    for k in ("comtrade_monthly", "comtrade_destinations", "agmarknet"):
        if not any(snap[k].values()) if isinstance(snap[k], dict) else not snap[k]:
            print("WARN: source empty this run, keeping previous:", k, file=sys.stderr)
            snap[k] = prev.get(k, snap[k]); snap.setdefault("stale", []).append(k)
    if not snap["fx"]: snap["fx"] = prev.get("fx")
    json.dump(snap, open(lp, "w"), indent=1)
    append_history(snap)
    print("ok", TODAY, "comtrade codes with data:", sum(1 for v in snap["comtrade_monthly"].values() if v),
          "agmarknet:", len(snap["agmarknet"]))

def append_history(s):
    hp = os.path.join(ROOT, "history.csv")
    cols = ["snapshot_date", "source", "series", "period", "value", "unit", "note"]
    seen = set()
    if os.path.exists(hp):
        for r in csv.DictReader(open(hp)):
            seen.add((r["snapshot_date"], r["source"], r["series"], r["period"]))
    new = []
    sd = s["snapshot_date"]
    stale = set(s.get("stale", []))
    if "comtrade_monthly" not in stale:
        for h, rows in s["comtrade_monthly"].items():
            for r in rows:
                if r["usd_per_kg"] is not None:
                    new.append([sd, "UN Comtrade", f"HS{h} India export unit value", r["period"], r["usd_per_kg"], "USD/kg", ""])
    if "agmarknet" not in stale:
        for cid, a in s["agmarknet"].items():
            if a["price_rs_q"] is not None:
                new.append([sd, "Agmarknet", f"{a['name']} all-India avg", a["reported_date"], a["price_rs_q"], "INR/quintal", f"arrival {a['arrival_t']} t"])
    if s.get("fx"):
        new.append([sd, "ECB via Frankfurter", "USD/INR", s["fx"]["date"], s["fx"]["usd_inr"], "INR per USD", ""])
    new = [r for r in new if (r[0], r[1], r[2], r[3]) not in seen]
    exists = os.path.exists(hp)
    with open(hp, "a", newline="") as fh:
        w = csv.writer(fh)
        if not exists: w.writerow(cols)
        w.writerows(new)
    print("history rows appended:", len(new))

if __name__ == "__main__":
    main()
