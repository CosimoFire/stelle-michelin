"""Serie storica stellati per regione e macroarea (edizioni 2014-2026).

Uso: python scripts/serie.py data/raw data/serie output
Input:  data/serie/regioni_raw.csv (edizione;regione;tre;due;una), ANPR residenti
Output: output/stellati_regioni.csv, output/serie.json (per la dashboard)
"""
import json, sys
import pandas as pd

RAW, SERIE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

r = pd.read_csv(f"{SERIE}/regioni_raw.csv", sep=";")
r["ristoranti"] = r.tre + r.due + r.una
r["stelle"] = 3 * r.tre + 2 * r.due + r.una

RIP = {"Valle d'Aosta": "Nord-ovest", "Piemonte": "Nord-ovest", "Liguria": "Nord-ovest", "Lombardia": "Nord-ovest",
       "Trentino-Alto Adige": "Nord-est", "Veneto": "Nord-est", "Friuli-Venezia Giulia": "Nord-est", "Emilia-Romagna": "Nord-est",
       "Toscana": "Centro", "Umbria": "Centro", "Marche": "Centro", "Lazio": "Centro",
       "Abruzzo": "Sud", "Molise": "Sud", "Campania": "Sud", "Puglia": "Sud", "Basilicata": "Sud", "Calabria": "Sud",
       "Sicilia": "Isole", "Sardegna": "Isole"}
unknown = set(r.regione) - set(RIP)
assert not unknown, f"Regioni non riconosciute: {unknown}"
r["ripartizione"] = r.regione.map(RIP)
r["macro"] = r.ripartizione.map({"Nord-ovest": "Nord", "Nord-est": "Nord", "Centro": "Centro",
                                 "Sud": "Mezzogiorno", "Isole": "Mezzogiorno"})

# controllo somme contro i totali ufficiali (fonti.csv)
f = pd.read_csv(f"{SERIE}/fonti.csv", sep=";").set_index("edizione")
chk = r.groupby("edizione").ristoranti.sum().to_frame("somma_regioni")
chk["ufficiale_italia"] = f.totale_ufficiale_italia
chk["diff"] = chk.somma_regioni - chk.ufficiale_italia
print("Controllo somme vs totali ufficiali (San Marino escluso):\n", chk, "\n")

a = r.groupby(["edizione", "macro"]).ristoranti.sum().unstack()
share = (a.div(a.sum(axis=1), axis=0) * 100).round(1)
print("Stellati per macroarea:\n", a, "\n\nQuota %:\n", share, "\n")

# quota residenti per macroarea (ANPR); se i dati grezzi non ci sono, riusa le quote dell'ultimo serie.json
import os
ANPR = f"{RAW}/anpr/data/popolazione_residente_export.json"
NORD = {"PIEMONTE", "VALLE D'AOSTA", "LOMBARDIA", "LIGURIA", "TRENTINO ALTO ADIGE", "VENETO",
        "FRIULI VENEZIA GIULIA", "EMILIA ROMAGNA"}
CENTRO = {"TOSCANA", "UMBRIA", "MARCHE", "LAZIO"}
if os.path.exists(ANPR):
    pa = pd.DataFrame(json.load(open(ANPR)))
    pa["macro"] = pa.REGIONE.map(lambda x: "Nord" if x in NORD else "Centro" if x in CENTRO else "Mezzogiorno")
    pop = (pa.groupby("macro").RESIDENTI.sum() / pa.RESIDENTI.sum() * 100).round(1)
else:
    print("ATTENZIONE: dati ANPR non trovati, uso le quote di residenti già in output/serie.json")
    pop = pd.Series(json.load(open(f"{OUT}/serie.json", encoding="utf-8"))["pop"])
print("Quota residenti ANPR:\n", pop)

KEYS = ["Nord", "Centro", "Mezzogiorno"]
out = {"anni": a.index.tolist(),
       "abs": {k: a[k].astype(int).tolist() for k in KEYS},
       "pct": {k: share[k].tolist() for k in KEYS},
       "tot": a.sum(axis=1).astype(int).tolist(),
       "pop": {k: float(pop[k]) for k in KEYS}}
json.dump(out, open(f"{OUT}/serie.json", "w", encoding="utf-8"), ensure_ascii=False)
r[["edizione", "regione", "ripartizione", "macro", "tre", "due", "una", "ristoranti", "stelle"]] \
    .to_csv(f"{OUT}/stellati_regioni.csv", index=False)
