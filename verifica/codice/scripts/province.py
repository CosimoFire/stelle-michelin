"""Aggregate per province, capoluogo vs resto provincia."""
import sys
import pandas as pd

OUT = sys.argv[1]
j = pd.read_csv(f"{OUT}/michelin_italia_comuni.csv", dtype={"COD_ISTAT_COMUNE": str})
a = pd.read_csv(f"{OUT}/anpr_residenti_capoluoghi.csv", dtype={"COD_ISTAT_COMUNE": str})

a["area"] = a.capoluogo.map({True: "capoluogo", False: "resto"})
j["area"] = j.capoluogo.map({True: "capoluogo", False: "resto"})
j["bib"] = j.Award.eq("Bib Gourmand")

pop = a.groupby(["PROVINCIA", "area"]).RESIDENTI.sum().unstack(fill_value=0)
r = j.groupby(["PROVINCIA", "area"]).agg(stellati=("starred", "sum"), stelle=("stars", "sum"),
                                         bib=("bib", "sum"), selezione=("Name", "size")).unstack(fill_value=0)
r.columns = [f"{m}_{area}" for m, area in r.columns]
t = pop.add_prefix("residenti_").join(r).fillna(0)
for m in ["stellati", "stelle", "bib", "selezione"]:
    for area in ["capoluogo", "resto"]:
        t[f"{m}_{area}"] = t[f"{m}_{area}"].astype(int)
        t[f"{m}_{area}_x100k"] = (t[f"{m}_{area}"] / t[f"residenti_{area}"] * 1e5).round(2)
    t[f"{m}_tot"] = t[f"{m}_capoluogo"] + t[f"{m}_resto"]
t["residenti_tot"] = t.residenti_capoluogo + t.residenti_resto
t["stellati_tot_x100k"] = (t.stellati_tot / t.residenti_tot * 1e5).round(2)
t["quota_stellati_capoluogo"] = (t.stellati_capoluogo / t.stellati_tot.where(t.stellati_tot > 0)).round(3)
t["quota_residenti_capoluogo"] = (t.residenti_capoluogo / t.residenti_tot).round(3)
t = t.reset_index().rename(columns={"PROVINCIA": "provincia"})
t.to_csv(f"{OUT}/province_capoluogo_resto.csv", index=False)

# --- national summary ---
nat = j.groupby("area").agg(stellati=("starred", "sum"), stelle=("stars", "sum"), bib=("bib", "sum"), selezione=("Name", "size"))
nat["residenti"] = a.groupby("area").RESIDENTI.sum()
nat["stellati_x100k"] = nat.stellati / nat.residenti * 1e5
print(nat, "\n")
print("Comuni con almeno uno stellato:", j[j.starred].COD_ISTAT_COMUNE.nunique())
# size class of comuni hosting starred restaurants
j2 = j[j.starred].copy()
j2["classe"] = pd.cut(j2.RESIDENTI, [0, 2000, 5000, 20000, 100000, 1e8],
                      labels=["<2k", "2-5k", "5-20k", "20-100k", ">100k"])
a["classe"] = pd.cut(a.RESIDENTI, [0, 2000, 5000, 20000, 100000, 1e8], labels=["<2k", "2-5k", "5-20k", "20-100k", ">100k"])
cl = pd.DataFrame({"stellati": j2.classe.value_counts(), "residenti": a.groupby("classe").RESIDENTI.sum()}).sort_index()
cl["quota_stellati"] = (cl.stellati / cl.stellati.sum()).round(3)
cl["quota_residenti"] = (cl.residenti / cl.residenti.sum()).round(3)
print(cl, "\n")
print("Top comuni per stellati:\n", j[j.starred].groupby("COMUNE").size().sort_values(ascending=False).head(12))
cols = ["provincia", "stellati_tot", "stellati_capoluogo", "stellati_resto", "stellati_tot_x100k",
        "stellati_capoluogo_x100k", "stellati_resto_x100k", "quota_stellati_capoluogo", "quota_residenti_capoluogo"]
print("\nTop 15 province per stellati x100k:\n", t.sort_values("stellati_tot_x100k", ascending=False)[cols].head(15).to_string(index=False))
print("\nProvince senza stellati:", t[t.stellati_tot == 0].provincia.tolist())
print("\nProvince dove il resto supera il capoluogo per densità (stellati>=3):",
      (t[(t.stellati_tot >= 3)].stellati_resto_x100k > t[(t.stellati_tot >= 3)].stellati_capoluogo_x100k).sum(), "su", (t.stellati_tot >= 3).sum())
