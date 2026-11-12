#!/usr/bin/env bash
# Scarica (o aggiorna) i dati grezzi in data/raw. Tutte le fonti sono su GitHub.
set -euo pipefail
RAW="${1:-data/raw}"
mkdir -p "$RAW/geo" "$RAW/pop"

clone_or_pull () {  # $1 repo, $2 dir
  if [ -d "$2/.git" ]; then git -C "$2" pull --depth 1 -q; else git clone -q --depth 1 "https://github.com/$1.git" "$2"; fi
}

echo "1/4 Michelin (michelin-my-maps, CSV aggiornato circa una volta al mese)"
clone_or_pull ngshiheng/michelin-my-maps "$RAW/mym"
git -C "$RAW/mym" log -1 --format='    ultimo aggiornamento CSV: %cd'

echo "2/4 ANPR, popolazione residente per comune (aggiornata ogni giorno)"
clone_or_pull italia/anpr-opendata "$RAW/anpr"

echo "3/4 Confini comunali (openpolis)"
curl -sSL -o "$RAW/geo/comuni.geojson" https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_municipalities.geojson

echo "4/4 Popolazione per paese (Banca Mondiale, via datasets/population)"
curl -sSL -o "$RAW/pop/population.csv" https://raw.githubusercontent.com/datasets/population/main/data/population.csv

echo "Fatto."
