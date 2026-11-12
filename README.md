# Stelle Michelin in Italia: grafico da incorporare

| File | Che cosa contiene |
|---|---|
| `dashboard.html` | La dashboard: serie 2014–2026 per Nord, Centro e Mezzogiorno e mappa delle province (capoluogo e resto della provincia), con filtro per stelle e tabella |
| `index.html` | Pagina di prova che incorpora la dashboard come farebbe il sito |
| `dati.json` | I dati usati (serie per macroarea e indicatori per provincia; la dashboard ha gli stessi dati già al suo interno) |

La pagina non usa librerie esterne. L'unica risorsa esterna è il font Source Serif 4 di Google Fonts.

## 1. Pubblicazione

La pagina è pubblicata con GitHub Pages (branch **main**, cartella **/ (root)**):

- `https://cosimofire.github.io/stelle-michelin/dashboard.html`
- `https://cosimofire.github.io/stelle-michelin/` (pagina di prova)

Per aggiornare il grafico basta ricaricare `dashboard.html` su GitHub: la versione online si aggiorna in circa un minuto, anche negli articoli dove è già incorporato. Il file si rigenera dal progetto `michelin-dashboard` con `make build` (template `templates/dashboard.html`).

## 2. Incorporare nell'articolo

Nel CMS inserisci un blocco HTML con questo codice:

```html
<iframe src="https://cosimofire.github.io/stelle-michelin/dashboard.html"
        title="Stelle Michelin in Italia: dove sono e come si spostano"
        style="width:100%;border:0;height:2100px" scrolling="no"></iframe>
```

### Altezza automatica

La dashboard comunica la propria altezza alla pagina che la ospita. Per usarla aggiungi **una sola volta** nella pagina questo script (è lo stesso di golden power e sirene: se è già nel template del sito non serve ripeterlo):

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

- **Fonti:** Guida Michelin (selezione online via michelin-my-maps, estrazione del 3 novembre 2026), elenchi annuali Scatti di Gusto / Dissapore per la serie 2014–2026, ANPR per i residenti.
- **Limiti:** la mappa conta 377 stellati, la serie 394 per il 2026 (fonti diverse). Il dato 2016 della serie va verificato su una seconda fonte.
- **Privacy:** il font viene caricato dai server di Google. Se la policy del giornale lo vieta, si possono caricare i file del font nel repository e togliere il link a `fonts.googleapis.com`.
