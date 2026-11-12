# Stelle Michelin in Italia: pacchetto per la verifica

Questa cartella contiene tutto ciò che serve per controllare i due grafici pubblicati:

- `serie.html` — ristoranti stellati per Nord, Centro e Mezzogiorno, edizioni 2014–2027
- `mappa.html` — ristoranti stellati per provincia (capoluogo e resto della provincia), edizione 2027

Pagine online: https://cosimofire.github.io/stelle-michelin/serie.html e https://cosimofire.github.io/stelle-michelin/mappa.html

## Che cosa verificare

1. Che i 382 ristoranti dell'edizione 2027 e il loro numero di stelle corrispondano al sito ufficiale della Guida MICHELIN.
2. Che l'assegnazione di ogni ristorante a comune, provincia e regione sia corretta.
3. Che i conteggi per regione e per anno della serie corrispondano alle fonti indicate.
4. Che i numeri citati nei grafici e nel testo derivino correttamente dai dati.

## File

| File | Contenuto |
|---|---|
| `dati/stellati_2027_sito_michelin.tsv` | I 382 ristoranti come letti dal sito Michelin il 12 novembre 2026: stelle, id Michelin, nome, località e regione indicate dal sito, coordinate |
| `dati/stellati_2027_per_comune.csv` | Gli stessi ristoranti assegnati al comune ANPR (per coordinate), con provincia, regione, flag capoluogo e distanza dal confine comunale |
| `dati/province_2027.csv` | 107 province: stellati per livello, capoluogo/resto, residenti, stellati ogni 100.000 residenti |
| `dati/serie_regioni_2014_2027.csv` | Stellati per regione ed edizione (tre; due; una stella), base della serie |
| `dati/fonti_serie.csv` | Fonte, URL, totale ufficiale e note di ogni edizione della serie |
| `dati/serie_macroaree.json` | Serie per macroarea come usata nel grafico (valori assoluti, quote, quota di residenti) |
| `codice/` | Script Python e template che producono i dati e le pagine (`make all`) |

## Fonti

- **Edizione 2027 (mappa e ultimo anno della serie):** sito ufficiale Guida MICHELIN Italia, pagine di selezione per livello di stelle:
  - https://guide.michelin.com/it/it/selection/italy/ristoranti/3-stelle-michelin
  - https://guide.michelin.com/it/it/selection/italy/ristoranti/2-stelle-michelin
  - https://guide.michelin.com/it/it/selection/italy/ristoranti/1-stella-michelin

  Conteggi per regione dalle pagine regionali, per esempio https://guide.michelin.com/it/it/lombardia/ristoranti/1-stella-michelin.
  Comunicato con i totali: https://guide.michelin.com/it/it/notizia/michelin-guide-ceremony/guida-michelin-italia-2027-tre-nuovi-ristoranti-conquistano-due-stelle-michelin
- **Edizioni 2014–2026 della serie:** elenchi annuali pubblicati da Scatti di Gusto (2014–2017, 2019–2026) e Dissapore (2018); URL di ogni anno in `dati/fonti_serie.csv`.
- **Residenti e comuni:** ANPR open data (https://github.com/italia/anpr-opendata), 107 province.
- **Confini comunali:** openpolis (https://github.com/openpolis/geojson-italy).

## Metodo

1. **Elenco 2027.** Dalle tre pagine di selezione del sito Michelin (Italia) sono stati letti nome, id, località, regione e coordinate di ogni ristorante. Sono state scartate le schede di ristoranti suggeriti che il sito mostra in fondo alle liste e che non hanno il livello di stelle della pagina.
2. **Comune e provincia.** Ogni ristorante è assegnato al comune il cui poligono contiene le coordinate (join spaziale). Cinque ristoranti cadono appena fuori dal confine comunale e sono assegnati al comune più vicino; nessuno è a più di 2 km.
3. **Capoluogo.** È il comune sede della provincia; per Barletta-Andria-Trani sono capoluoghi tutti e tre i comuni. Le province sono le 107 dell'ANPR: per la Sardegna resta il vecchio assetto (Sud Sardegna).
4. **Serie per macroarea.** Nord = Nord-ovest + Nord-est, Centro = Toscana, Umbria, Marche, Lazio, Mezzogiorno = Sud e Isole (ripartizioni Istat). San Marino è escluso.
5. **Tassi.** Stellati ogni 100.000 residenti ANPR; nella mappa il colore riguarda solo il resto della provincia, il cerchio il capoluogo.

## Controlli già fatti (da ripetere)

- Totale 2027: 382 = 13 tre stelle + 40 due stelle + 329 una stella, uguale al comunicato Michelin.
- Regioni 2027: Lombardia 59, Campania 48, Toscana 39, Piemonte 34, Lazio 33 — uguali al lancio askanews del 12 novembre 2026.
- Province 2027: Roma 28 (1/5/22), Napoli 26 (0/6/20), Bolzano 22 (1/2/19), Milano 21 (1/4/16), Salerno 17 (0/0/17) — uguali all'askanews.
- Serie: le somme regionali coincidono con i totali ufficiali tranne 2014 e 2019 (−1), 2021 (−1) e 2016 (−2).

## Numeri citati nel testo da controllare

- Totale 2027: 382, contro 394 nel 2026 (−12).
- Tre stelle: da 15 (2026) a 13 (2027). Uliassi (Senigallia) passa a due stelle; Quattro Passi (Nerano) non è più tra i tre stelle.
- Variazione 2026–2027: Nord −11 (a 198), Centro −3 (a 85), Mezzogiorno +2 (a 99).
- Quote: Nord dal 62,5% (2014) al 51,8% (2027); Mezzogiorno dal 19,8% al 25,9%, contro il 33,4% dei residenti.
- 278 stellati su 382 fuori dai capoluoghi (73%), dove vive il 70% dei residenti.
- 90 stellati su 382 (24%) in comuni sotto i 5.000 abitanti, che ospitano il 16% dei residenti.
- 75 capoluoghi su 107 senza stellati; 22 province senza alcuno stellato.
- Roma (comune) 22 stellati, Milano (comune) 19: insieme 41.

## Limiti noti

- Il dato 2016 della serie è il meno solido (somma regionale −2 rispetto al totale ufficiale): il salto 2016–2017 va verificato su una seconda fonte.
- 2012 e 2013 mancano: online le tabelle regionali sono solo immagini.
- Il 2014–2026 viene da elenchi di stampa, il 2027 dal sito Michelin: fonti diverse per anni diversi.
- Il comune indicato nei tooltip è quello amministrativo ANPR, non la località indicata dal sito (per esempio Don Alfonso 1890 risulta a Massa Lubrense, non a Sant'Agata sui Due Golfi).
- Le colonne su Bib Gourmand e selezione non sono incluse: l'elenco 2027 riguarda solo gli stellati.

## Rifare i calcoli

```bash
cd codice
pip install -r requirements.txt
bash scripts/fetch_data.sh data/raw          # ANPR e confini comunali (~300 MB)
mkdir -p data/serie output
cp ../dati/serie_regioni_2014_2027.csv data/serie/regioni_raw.csv
cp ../dati/fonti_serie.csv data/serie/fonti.csv
make all MICHELIN=../dati/stellati_2027_sito_michelin.tsv
```

Lo script `paesi.py` (confronto tra paesi) non è usato nei grafici pubblicati.
