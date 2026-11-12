"""Costruisce le pagine HTML autonome (dati incorporati).

Uso: python scripts/build.py templates output
Output: output/mappa_province.html, output/serie_macroaree.html, output/dashboard_michelin.html
(le prime due sono le pagine da incorporare; dashboard_michelin.html le unisce)
"""
import json, re, sys
import pandas as pd

TPL, OUT = sys.argv[1], sys.argv[2]

j = pd.read_csv(f"{OUT}/michelin_italia_comuni.csv", dtype={"COD_ISTAT_COMUNE": str})
a = pd.read_csv(f"{OUT}/anpr_residenti_capoluoghi.csv", dtype={"COD_ISTAT_COMUNE": str})
t = pd.read_csv(f"{OUT}/province_capoluogo_resto.csv")
s = j[j.starred]

nat = {"quota_fuori": float((~s.capoluogo).mean()),
       "quota_res_fuori": float(a[~a.capoluogo].RESIDENTI.sum() / a.RESIDENTI.sum()),
       "quota_sotto5k": float((s.RESIDENTI < 5000).mean()),
       "quota_res_sotto5k": float(a[a.RESIDENTI < 5000].RESIDENTI.sum() / a.RESIDENTI.sum())}
z = t[t.stellati_capoluogo == 0].sort_values("residenti_capoluogo", ascending=False)
nat["esempi_zero"] = ", ".join(x.title() for x in z.provincia.head(4))
print("Indicatori nazionali:", nat)

mappa = open(f"{OUT}/mappa_data.json", encoding="utf-8").read()

# nomi dei ristoranti per provincia: capoluogo / resto, per numero di stelle (per i tooltip della mappa)
SMALL = {"di", "del", "della", "dei", "degli", "delle", "da", "de", "in", "e", "sul", "sulla", "sui", "al", "alla", "a", "con"}
def tc(x):
    """Nome di comune ANPR (maiuscolo) in forma leggibile: Serralunga d'Alba, Sant'Agata sui Due Golfi."""
    t = re.sub(r"(^|[\s\-'/])(\w)", lambda m: m.group(1) + m.group(2).upper(), str(x).lower())
    t = re.sub(r"(?<=\s)(D|Dell|Nell|Sull|All|Dall)'", lambda m: m.group(1).lower() + "'", t)
    return " ".join(w if i == 0 or w.lower() not in SMALL else w.lower() for i, w in enumerate(t.split(" ")))
nomi = {}
for r in s.sort_values("Name").itertuples():
    d = nomi.setdefault(r.PROVINCIA, {"cap": {"1": [], "2": [], "3": []}, "res": {"1": [], "2": [], "3": []}})
    d["cap" if r.capoluogo else "res"][str(r.stars)].append([r.Name, tc(r.COMUNE)])

pct5k = f"che ospitano il {round(nat['quota_res_sotto5k'] * 100)}% dei residenti"

def fill(tpl, extra=None):
    h = open(tpl, encoding="utf-8").read().replace("__DATA__", mappa).replace("__NAT__", json.dumps(nat))
    h = h.replace("__NOMI__", json.dumps(nomi, ensure_ascii=False))
    h = h.replace("che ospitano il 16% dei residenti", pct5k)
    for k, v in (extra or {}).items():
        h = h.replace(k, v)
    return h

serie = {"__SERIE__": open(f"{OUT}/serie.json", encoding="utf-8").read()}
for tpl, out, extra in [("mappa.html", "mappa_province.html", None),
                        ("serie.html", "serie_macroaree.html", serie),
                        ("dashboard.html", "dashboard_michelin.html", serie)]:
    open(f"{OUT}/{out}", "w", encoding="utf-8").write(fill(f"{TPL}/{tpl}", extra))
print("Scritti: mappa_province.html, serie_macroaree.html, dashboard_michelin.html")
