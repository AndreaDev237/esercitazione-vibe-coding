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
> Crea src/store.py con una funzione che crea lo schema SQLite (una tabella denormalizzata: contatore, edificio, tipo, unità, data, valore) e una che inserisce le letture usando l'anagrafica. Aggiungi un vincolo che impedisca due letture per la stessa coppia contatore e data. Poi src/cli.py con argparse che esegue tutta la pipeline e stampa quante righe sono state lette, scartate, quante correzioni, quante inserite. Solo standard library.

**Cosa ho accettato e cosa no:**
Schema, vincolo e CLI vanno bene. Dentro `inserisci` però catturava `sqlite3.IntegrityError` e faceva `continue`, contando a parte le righe saltate. L'ho tolto: se arriva un doppione l'eccezione sale e basta.

Poi, siccome SQL lo mastico poco, gli ho fatto spiegare `UNIQUE (id_contatore, data)` riga per riga. Il dubbio che avevo era se il vincolo fosse su ogni colonna separatamente o sulla coppia. È sulla coppia: due contatori diversi lo stesso giorno vanno benissimo.

**Perché:**
Se il database rifiuta una riga, il problema è a monte, la deduplica ha lasciato passare qualcosa. Con il `continue` il riepilogo a schermo tornerebbe comunque e non me ne accorgerei mai. Preferisco che la pipeline si fermi.

---

## Una cosa che ho rifiutato

Finita la fase 5, coi test verdi, ho chiesto: "Le liste hanno circa 3500 elementi. Rendi queste funzioni più efficienti, evitando copie inutili." Mi ha proposto due cose: trasformare il ciclo di `tieni_ultima` in una dict comprehension, e in `ordina_per_data` usare `letture.sort(key=...)` al posto di `sorted(...)`, per non copiare la lista.

Le ho applicate tutte e due, senza pensarci troppo. Pytest: `1 failed`, ed era `test_ordina_per_data_non_muta_l_input`. Il `.sort()` ordina la lista che gli passa il chiamante, che poi se la ritrova cambiata. Su quello che avevo chiesto (meno copie) aveva ragione, il costo era da un'altra parte. Ho tolto il `.sort()` e tenuto la comprehension. Il commit rosso è `sol-06-refactor-rosso`, quello dopo `sol-07-store`.

La cosa che mi ha fatto un po' arrabbiare: sotto il blocco di codice c'era scritto "nota: `.sort()` modifica la lista in place". L'avvertimento c'era. Io avevo copiato il blocco e basta.

## Una riga che non so spiegare

`cursore.rowcount` dopo `executemany`. Non ero sicuro se contasse solo l'ultima esecuzione o tutte. Ho chiesto e ho controllato la documentazione: per gli INSERT è il totale delle righe inserite da tutte le esecuzioni. Prima non lo sapevo e l'avrei committato uguale, il test passava. Adesso lo so.

## Autovalutazione

| # | Domanda | Sì/No |
|---|---|---|
| 1 | Piano prima del codice, e corretto | Sì |
| 2 | Tre edge case proposti dall'AI e gestiti | Sì |
| 3 | Un traceback risolto con un prompt | Sì, due |
| 4 | Attese dei test dal manifest | Sì |
| 5 | Test "non modifica l'input" | Sì, tre |
| 6 | Un suggerimento rifiutato, con motivo | Sì |
| 7 | "Vale l'ultima" come dice il Comune | Sì |
| 8 | Il database rifiuta un doppione, con test | Sì |
| 9 | Diff letto prima di ogni commit | Sì |
| 10 | So spiegare ogni funzione | Sì, dopo aver chiesto di `rowcount` |
