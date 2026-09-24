# Diario dell'esercitazione

**Nome:** Andrea (la soluzione mostrata nella lezione 11)
**Strumento usato:** GitHub Copilot, chat in modalità Ask

Per ogni fase, tre righe. Il prompt lo copi così com'è. Se ne hai usati più
di uno, metti quello che ha contato di più.

## 1. Piano

**Prompt usato:**
> Voglio scrivere uno script che legge letture giornaliere di contatori da un CSV, le valida, le aggrega per edificio e mese usando un'anagrafica, e le salva su SQLite. Prima di generare codice, elenca i 5 step principali, le dipendenze, e i potenziali punti di fallimento.

**Cosa ho accettato e cosa no:**
I cinque step vanno bene così come sono, li ho tenuti tutti. Ho dovuto correggere tre dettagli che però non sono dettagli: dava per scontato che il separatore fosse la virgola (è il punto e virgola, bastava aprire il file), sui duplicati ha scritto "tieni la prima occorrenza" mentre il Comune dice l'ultima, e come chiave di aggregazione proponeva edificio + mese. Senza il tipo di contatore avrei sommato kWh e metri cubi nello stesso numero.

**Perché:**
Non è colpa sua, in un certo senso. Nel prompt non gli ho detto le regole del Comune e non gli ho fatto vedere il file, quindi ha risposto per un CSV qualunque. Il piano resta valido come scheletro, l'ho corretto a mano e l'ho messo in PIANO.md con le mie modifiche in grassetto. Non aveva senso ributtarlo tutto per tre righe sbagliate.

## 2. Lettura

**Prompt usato:**
> Questo codice `open(percorso, encoding="utf-8")` solleva `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x96 in position 174: invalid start byte`. Spiega la causa, suggerisci 2 fix alternativi, e indica il più robusto.

**Cosa ho accettato e cosa no:**
La spiegazione era giusta: 0x96 in cp1252 è il trattino lungo (quello di "Palazzo Comunale – Piazza Libertà", riga 4), e in UTF-8 quel byte da solo non vuol dire niente. I due fix proposti erano `errors="replace"` e `encoding="cp1252"`. Ha detto che il primo è più robusto perché "non fallisce mai". Ho preso il secondo.

**Perché:**
Con `replace` il file si legge sempre, vero, ma i nomi degli edifici escono con dentro il carattere di sostituzione e nessuno se ne accorge finché non li vede in un report. Il file arriva da un gestionale Windows, cp1252 non è un'ipotesi. E se un giorno cambiano gestionale e mi arriva un UTF-8 vero, preferisco che mi esploda in faccia al primo giro piuttosto che avere nomi sporchi in database per un anno.

## 3. Validazione

**Prompt usato:**
> Scrivi una funzione `valida(righe)` che riceve liste di 5 stringhe (id contatore, edificio, data ISO, valore, stato) e restituisce due liste: le letture valide come dizionari e gli scarti come stringhe con il motivo. Includi gestione edge case e docstring. Prima di scrivere il codice, elenca gli edge case che vedi.

**Cosa ho accettato e cosa no:**
Mi ha elencato sei casi: riga corta, valore vuoto, valore non numerico, data non in formato ISO, stato sconosciuto, valore negativo. Ho tenuto i primi tre e lo stato. La data non ISO l'ho tolta perché nel file non c'è e comunque `date.fromisoformat` alza già un'eccezione sensata da sola. Il negativo l'ho tolto, vedi sotto. Ho aggiunto io due cose che non aveva considerato: lo zero è un valore valido, e `STIMA` è uno stato valido esattamente come `OK` (lui teneva solo `OK`).

La prima versione del codice faceva `float(valore.replace(",", "."))`. Ha retto otto righe. Alla nona, `ValueError: could not convert string to float: '1.282.4'`: il punto delle migliaia. Ho incollato il traceback in chat e ha capito subito, da lì è nata `numero_italiano`, che toglie prima i punti e poi cambia la virgola.

**Perché:**
Sul negativo ci ho pensato un attimo. Nelle regole del Comune non c'è, nel file non ce n'è nemmeno uno. Se lo metto, fra sei mesi qualcuno legge quel controllo e pensa che i negativi siano una cosa che succede. Meglio niente. Sugli stati invece l'AI è stata prudente per eccesso, ma la regola è scritta nella consegna, non c'era da interpretare.

## 4. Test

**Prompt usato:**
> Per la funzione `valida` in src/valida.py, scrivi 5 test unitari con pytest che coprano caso base, edge case, input non validi, e un caso di regressione. Le attese sui conteggi devono venire da data/manifest.json, non da numeri scritti a mano.

**Cosa ho accettato e cosa no:**
La struttura sì. Tre assert li ho riscritti. Come caso base aveva messo `assert len(valide) > 0`, che passa con qualunque bug immaginabile. Poi aveva `assert len(scarti) == 131` col numero scritto a mano, nonostante nel prompt gli avessi detto di leggerlo dal manifest (ha letto il manifest per le valide e non per gli scarti, boh). L'ho fatto sommare le tre cause dal manifest. E ho aggiunto un test che non aveva proposto: `test_valida_non_muta_l_input`.

**Perché:**
Per ogni assert mi sono chiesto quale bug lo farebbe diventare rosso. Su `> 0` non ho trovato risposta. Sul 131 a mano la risposta c'è, ma il giorno che rigenero il dataset quel test diventa rosso senza che ci sia un bug, e so già che qualcuno "sistema" il numero nel test invece di guardare il codice. Il test sull'input che non cambia oggi non serve a niente, lo so. L'ho scritto perché nel corso, alla lezione 7, il suo gemello ha preso l'unico bug vero del progetto. E infatti, vedi fase 5.

## 5. Aggregazione

**Prompt usato:**
> In src/aggrega.py scrivi: una funzione che carica data/contatori.csv indicizzato per IdContatore; una che, date le letture, per ogni coppia contatore e data tiene l'ultima lettura nell'ordine del file e restituisce una nuova lista; una che ordina per data restituendo una nuova lista; una che somma i consumi per edificio, tipo, unità di misura e mese. Solo standard library. Poi i test in tests/test_aggrega.py, incluso uno che verifichi che le funzioni non modifichino la lista ricevuta.

**Cosa ho accettato e cosa no:**
Le quattro funzioni le ho tenute quasi tutte così com'erano. Stavolta nel prompt c'era scritto "l'ultima" e ha usato un dizionario che sovrascrive, giusto. Ho cambiato una cosa in `consumo_mensile`: faceva `anagrafica.get(id, {}).get("Edificio", "sconosciuto")`. L'ho ridotto a `anagrafica[id]` e ho aggiunto un test che si aspetta il `KeyError`.

Nei test ha usato `valide[:200]` come campione per il test di integrità su `ordina_per_data`. L'ho cambiato in `valide[-40:] + valide[:40]`.

**Perché:**
Un contatore che non sta in anagrafica non è un edificio che si chiama "sconosciuto", è un errore nei dati, e voglio saperlo subito. Sul campione: le prime 200 righe del file sono già in ordine di data, quindi se qualcuno mettesse un `.sort()` in place dentro la funzione, il test passerebbe lo stesso e non servirebbe a niente. Le correzioni sono in coda al file con date sparse, per questo prendo anche gli ultimi 40. Me ne sono accorto rileggendo il test con la solita domanda in testa, quale bug lo fa fallire. Così com'era, nessuno.

## 6. Salvataggio

**Prompt usato:**

**Cosa ho accettato e cosa no:**

**Perché:**

---

## Una cosa che ho rifiutato

## Una riga che non so spiegare

## Autovalutazione

| # | Domanda | Sì/No |
|---|---|---|
| 1 | Piano prima del codice, e corretto | |
| 2 | Tre edge case proposti dall'AI e gestiti | |
| 3 | Un traceback risolto con un prompt | |
| 4 | Attese dei test dal manifest | |
| 5 | Test "non modifica l'input" | |
| 6 | Un suggerimento rifiutato, con motivo | |
| 7 | "Vale l'ultima" come dice il Comune | |
| 8 | Il database rifiuta un doppione, con test | |
| 9 | Diff letto prima di ogni commit | |
| 10 | So spiegare ogni funzione | |
