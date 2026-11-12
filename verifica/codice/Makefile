PY  ?= python3
RAW := data/raw
OUT := output
# elenco stellati dal sito Michelin (vuoto = usa michelin-my-maps)
MICHELIN ?= data/michelin_sito_2027.tsv

.PHONY: all fetch analisi serie build clean

all: analisi serie build

fetch:
	bash scripts/fetch_data.sh $(RAW)

analisi:
	$(PY) scripts/prep.py $(RAW) $(OUT) $(MICHELIN)
	$(PY) scripts/province.py $(OUT)
	$(PY) scripts/mappa.py $(RAW) $(OUT)
	$(PY) scripts/paesi.py $(RAW) $(OUT)

serie:
	$(PY) scripts/serie.py $(RAW) data/serie $(OUT)

build:
	$(PY) scripts/build.py templates $(OUT)

clean:
	rm -f $(OUT)/*
