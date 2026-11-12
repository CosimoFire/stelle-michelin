"""Country comparison: per-capita only for full-coverage guides; plus top-tier share."""
import sys
import pandas as pd

RAW, OUT = sys.argv[1], sys.argv[2]
d = pd.read_csv(f"{RAW}/mym/data/michelin_my_maps.csv")
d["paese"] = d.Location.str.split(", ").str[-1]
d["stars"] = d.Award.map({"3 Stars": 3, "2 Stars": 2, "1 Star": 1}).fillna(0)
g = d.groupby("paese").agg(stellati=("stars", lambda s: (s > 0).sum()),
                           bi_tri=("stars", lambda s: (s >= 2).sum()),
                           stelle=("stars", "sum"), selezione=("Name", "size"),
                           localita=("Location", "nunique"))

# ISO3 for population join (World Bank via datasets/population, 2024)
ISO = {"France": "FRA", "Italy": "ITA", "Germany": "DEU", "Spain": "ESP", "Portugal": "PRT", "United Kingdom": "GBR",
       "Ireland": "IRL", "Belgium": "BEL", "Netherlands": "NLD", "Luxembourg": "LUX", "Switzerland": "CHE",
       "Austria": "AUT", "Denmark": "DNK", "Sweden": "SWE", "Norway": "NOR", "Finland": "FIN", "Slovenia": "SVN",
       "Croatia": "HRV", "Malta": "MLT", "Japan": "JPN", "USA": "USA", "Chinese Mainland": "CHN"}
# Guides with (near-)national coverage — to be verified edition by edition
FULL = {"France", "Italy", "Germany", "Spain", "Portugal", "United Kingdom", "Ireland", "Belgium", "Netherlands",
        "Luxembourg", "Switzerland", "Austria", "Denmark", "Sweden", "Norway", "Finland", "Slovenia", "Croatia", "Malta"}
p = pd.read_csv(f"{RAW}/pop/population.csv")
p = p[p.Year == 2024].set_index("Country Code").Value
g = g.loc[[c for c in ISO if c in g.index]].copy()
g["popolazione_2024"] = [p.get(ISO[c]) for c in g.index]
g["copertura"] = ["nazionale" if c in FULL else "parziale (solo alcune città/aree)" for c in g.index]
g["stellati_x1M"] = (g.stellati / g.popolazione_2024 * 1e6).round(2)
g["stelle_x1M"] = (g.stelle / g.popolazione_2024 * 1e6).round(2)
g["quota_bi_tri"] = (g.bi_tri / g.stellati).round(3)
g["quota_stellati_su_selezione"] = (g.stellati / g.selezione).round(3)
g = g.sort_values("stellati_x1M", ascending=False)
g.to_csv(f"{OUT}/paesi_confronto.csv")
print(g.drop(columns=["stelle"]).to_string())
