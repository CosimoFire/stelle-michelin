# Stelle Michelin in Italia: grafici da incorporare

| File | Che cosa contiene |
|---|---|
| `serie.html` | Le stelle Michelin in Italia per area geografica: serie 2014–2027 per Nord, Centro e Mezzogiorno (numero o quota) |
| `mappa.html` | I ristoranti stellati Michelin nelle province italiane: capoluogo e resto della provincia, filtro per stelle e tabella |
| `index.html` | Pagina di prova che incorpora i due grafici come farebbe il sito |
| `verifica/` | Pacchetto per la verifica: dati (382 stellati 2027, province, serie per regione), codice e metodo in `verifica/VERIFICA.md` |
| `dati.json` | I dati usati (serie per macroarea e indicatori per provincia; i grafici hanno gli stessi dati già al loro interno) |

Le pagine non usano librerie esterne. L'unica risorsa esterna è il font Source Serif 4 di Google Fonts.

## 1. Pubblicazione

La pagina è pubblicata con GitHub Pages (branch **main**, cartella **/ (root)**):

- `https://cosimofire.github.io/stelle-michelin/serie.html`
- `https://cosimofire.github.io/stelle-michelin/mappa.html`
- `https://cosimofire.github.io/stelle-michelin/` (pagina di prova)

Per aggiornare un grafico basta ricaricare il file su GitHub: la versione online si aggiorna in circa un minuto, anche negli articoli dove è già incorporato. I file si rigenerano dal progetto `michelin-dashboard` con `make build`: `output/serie_macroaree.html` diventa `serie.html`, `output/mappa_province.html` diventa `mappa.html`.

## 2. Incorporare nell'articolo

Nel CMS inserisci un blocco HTML per ciascun grafico:

```html
<iframe src="https://cosimofire.github.io/stelle-michelin/serie.html"
        title="Le stelle Michelin in Italia per area geografica"
        style="width:100%;border:0;height:850px" scrolling="no"></iframe>
```

```html
<iframe src="https://cosimofire.github.io/stelle-michelin/mappa.html"
        title="I ristoranti stellati Michelin nelle province italiane"
        style="width:100%;border:0;height:1350px" scrolling="no"></iframe>
```

### Altezza automatica

I grafici comunicano la propria altezza alla pagina che la ospita. Per usarla aggiungi **una sola volta** nella pagina questo script (è lo stesso di golden power e sirene: se è già nel template del sito non serve ripeterlo):

```html
<script>
window.addEventListener('message', function (e) {
  if (e.origin !== 'https://cosimofire.github.io') return;
  if (!e.data || !e.data.gpEmbed || !e.data.height) return;
  document.querySelectorAll('iframe').forEach(function (f) {
    if (f.contentWindow === e.source) f.style.height = e.data.height + 'px';
  });
});
</script>
```

Se il CMS non permette script, l'iframe funziona con l'altezza fissa indicata sopra; in quel caso conviene `scrolling="auto"`, perché aprendo la tabella delle province la pagina si allunga.

## 3. Note

- **Fonti:** mappa e anno 2027 della serie dal sito ufficiale della Guida MICHELIN Italia 2027 (382 stellati: 13 tre stelle, 40 due stelle, 329 una stella; regioni e prime cinque province coincidono con il lancio askanews del 12 novembre 2026); serie 2014–2026 dagli elenchi annuali Scatti di Gusto / Dissapore; residenti ANPR.
- **Limiti:** il dato 2016 della serie va verificato su una seconda fonte. I comuni sono assegnati dalle coordinate del sito Michelin (5 ristoranti cadono appena fuori dal confine comunale e sono assegnati al comune più vicino, a meno di 2 km).
- **Privacy:** il font viene caricato dai server di Google. Se la policy del giornale lo vieta, si possono caricare i file del font nel repository e togliere il link a `fonts.googleapis.com`.
