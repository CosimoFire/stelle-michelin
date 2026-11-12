"""Build SVG geometry + data JSON for the province map (ANPR 107 provinces)."""
import json, sys, unicodedata, re
import pandas as pd, geopandas as gpd

RAW, OUT = sys.argv[1], sys.argv[2]
a = pd.read_csv(f"{OUT}/anpr_residenti_capoluoghi.csv", dtype={"COD_ISTAT_COMUNE": str})
t = pd.read_csv(f"{OUT}/province_capoluogo_resto.csv")

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().split("/")[0]
    return re.sub(r"[^A-Z]", "", s)
REGMAP = {"VALLEDAOSTAVALLEEDAOSTE": "VALLEDAOSTA", "TRENTINOALTOADIGESUDTIROL": "TRENTINOALTOADIGE"}
g = gpd.read_file(f"{RAW}/geo/comuni.geojson")[["name", "com_istat_code", "reg_name", "geometry"]]
a["key"] = a.COMUNE.map(norm) + "|" + a.REGIONE.map(norm)
g["key"] = g.name.map(norm) + "|" + g.reg_name.map(norm).replace(REGMAP)
code = g.com_istat_code.where(g.com_istat_code.isin(a.COD_ISTAT_COMUNE), g.key.map(a.set_index("key").COD_ISTAT_COMUNE))
g["cod"] = code  # merged comuni (Castegnero, Nanto, Lirio) fall back to nearest province below
g = g.merge(a[["COD_ISTAT_COMUNE", "PROVINCIA", "COMUNE", "capoluogo"]], left_on="cod", right_on="COD_ISTAT_COMUNE", how="left")
miss = g.PROVINCIA.isna()
if miss.any():  # remaining few: nearest province by spatial neighbour
    print("unassigned polygons:", g[miss].name.tolist())
    nb = gpd.sjoin_nearest(g[miss][["geometry"]].to_crs(32632), g[~miss][["PROVINCIA", "geometry"]].to_crs(32632))
    g.loc[miss, "PROVINCIA"] = nb.PROVINCIA.groupby(level=0).first()
g = g.to_crs(32632)
g["geometry"] = g.buffer(0)
prov = g.dissolve("PROVINCIA").reset_index()[["PROVINCIA", "geometry"]]
prov["geometry"] = prov.simplify(900)
caps = g[g.capoluogo == True].copy()
caps["geometry"] = caps.representative_point()

# project to SVG coordinates
W = 640
minx, miny, maxx, maxy = prov.total_bounds
s = W / (maxx - minx); H = (maxy - miny) * s
def P(x, y): return round((x - minx) * s, 1), round((maxy - y) * s, 1)
def path(geom):
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            pts = [P(x, y) for x, y in ring.coords]
            if len(pts) < 4: continue
            out.append("M" + "L".join(f"{x},{y}" for x, y in pts) + "Z")
    return "".join(out)

td = t.set_index("provincia")
jj = pd.read_csv(f"{OUT}/michelin_italia_comuni.csv", dtype={"COD_ISTAT_COMUNE": str})
nstar = jj[jj.starred].groupby("COD_ISTAT_COMUNE").size()
lv = jj[jj.starred].groupby(["PROVINCIA", "capoluogo", "stars"]).size()
lvc = jj[jj.starred & jj.capoluogo].groupby(["COD_ISTAT_COMUNE", "stars"]).size()
feats = []
for _, r in prov.iterrows():
    d = td.loc[r.PROVINCIA]
    cp = caps[caps.PROVINCIA == r.PROVINCIA]
    pts = [{"nome": c.COMUNE.title(), "n": int(nstar.get(c.COD_ISTAT_COMUNE, 0)),
            "lv": [int(lvc.get((c.COD_ISTAT_COMUNE, k), 0)) for k in (1, 2, 3)],
            "xy": P(c.geometry.x, c.geometry.y)} for _, c in cp.iterrows()]
    lvl = {"cap": [int(lv.get((r.PROVINCIA, True, k), 0)) for k in (1, 2, 3)],
           "res": [int(lv.get((r.PROVINCIA, False, k), 0)) for k in (1, 2, 3)]}
    feats.append({"p": r.PROVINCIA, "d": path(r.geometry), "caps": pts, "lvl": lvl,
                  **{k: (None if pd.isna(d[k]) else (int(d[k]) if float(d[k]).is_integer() and "x100k" not in k and "quota" not in k else float(d[k])))
                     for k in ["residenti_capoluogo", "residenti_resto", "stellati_capoluogo", "stellati_resto",
                               "stelle_capoluogo", "stelle_resto", "bib_capoluogo", "bib_resto",
                               "stellati_capoluogo_x100k", "stellati_resto_x100k", "stellati_tot_x100k",
                               "quota_stellati_capoluogo", "quota_residenti_capoluogo"]}})
json.dump({"w": W, "h": round(H, 1), "f": feats}, open(f"{OUT}/mappa_data.json", "w"), ensure_ascii=False)
print("W,H", W, round(H), "provinces", len(feats), "size KB", round(len(json.dumps(feats)) / 1024))
print(t.stellati_resto_x100k.describe())
print(pd.cut(t.stellati_resto_x100k, [-0.01, 0, 0.5, 1, 2, 10]).value_counts().sort_index())
