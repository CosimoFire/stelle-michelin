"""Join Michelin restaurants (Italy) to comuni (spatial) and ANPR residents; flag capoluoghi."""
import json, sys, unicodedata, re
import pandas as pd, geopandas as gpd

RAW = sys.argv[1]
OUT = sys.argv[2]

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    s = s.split("/")[0]
    return re.sub(r"[^A-Z]", "", s)

# --- ANPR residents (master list, 107 provinces) ---
anpr = pd.DataFrame(json.load(open(f"{RAW}/anpr/data/popolazione_residente_export.json", encoding="utf-8")))
anpr["key"] = anpr.COMUNE.map(norm) + "|" + anpr.REGIONE.map(norm)
assert not anpr.key.duplicated().any(), anpr[anpr.key.duplicated(keep=False)]

# --- comuni polygons (openpolis) ---
g = gpd.read_file(f"{RAW}/geo/comuni.geojson")[["name", "com_istat_code", "reg_name", "geometry"]]
REGMAP = {"VALLEDAOSTAVALLEEDAOSTE": "VALLEDAOSTA", "TRENTINOALTOADIGESUDTIROL": "TRENTINOALTOADIGE"}
g["regk"] = g.reg_name.map(norm).replace(REGMAP)
g["key"] = g.name.map(norm) + "|" + g.regk
by_code = anpr.set_index("COD_ISTAT_COMUNE")
by_key = anpr.set_index("key")
def link(r):
    if r.com_istat_code in by_code.index: return r.com_istat_code
    if r.key in by_key.index: return by_key.loc[r.key, "COD_ISTAT_COMUNE"]
    return None
g["anpr_code"] = g.apply(link, axis=1)
print("polygons not linked to ANPR:", g.anpr_code.isna().sum(), g[g.anpr_code.isna()].name.tolist()[:30])

# --- Michelin ---
# Terzo argomento facoltativo: elenco scaricato dal sito ufficiale (data/michelin_sito_2027.tsv),
# altrimenti il CSV di michelin-my-maps.
if len(sys.argv) > 3:
    t = pd.read_csv(sys.argv[3], sep="	")
    it = pd.DataFrame({"Name": t.nome, "Location": t.citta + ", Italy", "Longitude": t.lng, "Latitude": t.lat,
                       "Award": t.stelle.map({3: "3 Stars", 2: "2 Stars", 1: "1 Star"}), "MichelinId": t.id})
    print("Fonte Michelin: sito ufficiale,", len(it), "ristoranti")
else:
    m = pd.read_csv(f"{RAW}/mym/data/michelin_my_maps.csv")
    it = m[m.Location.str.endswith(", Italy", na=False) | (m.Location == "Italy")].copy()
pts = gpd.GeoDataFrame(it, geometry=gpd.points_from_xy(it.Longitude, it.Latitude), crs=4326)
gp = g.to_crs(32632); pp = pts.to_crs(32632)
j = gpd.sjoin_nearest(pp, gp[["anpr_code", "name", "geometry"]], how="left", distance_col="dist_m")
j = j[~j.index.duplicated()]
print("restaurants:", len(j), "| outside polygon (>0 m):", (j.dist_m > 0).sum(), "| >2km:", (j.dist_m > 2000).sum())
print(j[j.dist_m > 2000][["Name", "Location", "dist_m"]])
j = j.merge(anpr[["COD_ISTAT_COMUNE", "COMUNE", "PROVINCIA", "REGIONE", "RESIDENTI"]],
            left_on="anpr_code", right_on="COD_ISTAT_COMUNE", how="left")
print("unlinked restaurants:", j.PROVINCIA.isna().sum())

# --- capoluoghi (primary seat; co-capoluoghi included where by law there are several) ---
CAP = {"AOSTA": ["AOSTA"], "BOLZANO/BOZEN": ["BOLZANO"], "BARLETTA-ANDRIA-TRANI": ["BARLETTA", "ANDRIA", "TRANI"],
       "FORLI'-CESENA": ["FORLI'", "FORLI"], "MASSA E CARRARA": ["MASSA"], "MONZA E DELLA BRIANZA": ["MONZA"],
       "PESARO E URBINO": ["PESARO"], "REGGIO DI CALABRIA": ["REGGIO DI CALABRIA"],
       "REGGIO NELL'EMILIA": ["REGGIO NELL'EMILIA"], "SUD SARDEGNA": ["CARBONIA"],
       "VERBANO-CUSIO-OSSOLA": ["VERBANIA"]}
anpr["capoluogo"] = anpr.apply(lambda r: norm(r.COMUNE) in [norm(x) for x in CAP.get(r.PROVINCIA, [r.PROVINCIA])], axis=1)
caps = anpr[anpr.capoluogo]
print("capoluoghi found:", len(caps), "provinces w/o capoluogo:", set(anpr.PROVINCIA) - set(caps.PROVINCIA))
j["capoluogo"] = j.COD_ISTAT_COMUNE.isin(caps.COD_ISTAT_COMUNE)

STARS = {"3 Stars": 3, "2 Stars": 2, "1 Star": 1}
j["stars"] = j.Award.map(STARS).fillna(0).astype(int)
j["starred"] = j.stars > 0
j.drop(columns="geometry").to_csv(f"{OUT}/michelin_italia_comuni.csv", index=False)
anpr.to_csv(f"{OUT}/anpr_residenti_capoluoghi.csv", index=False)
