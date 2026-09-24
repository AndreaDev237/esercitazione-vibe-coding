# I prompt pattern del corso

Sette pattern, quelli del syllabus. Sono template: le parentesi quadre le riempi
tu, con il tuo file, il tuo traceback, la tua funzione. Il prompt che usi davvero
lo copi nel diario.

**Un pattern non è una formula magica.** È un modo di fare la domanda che
costringe l'AI a dirti cose che puoi verificare: uno step, un edge case, due fix
alternativi, un cambiamento per volta. Poi verifichi.

| Fase | Pattern che serve |
|---|---|
| 1. Piano | Pianificazione prima del codice |
| 2. Lettura | Scrittura funzione, poi Debug da traceback (arriverà) |
| 3. Validazione | Scrittura funzione con edge case, Debug da traceback |
| 4. Test | Test unitari |
| 5. Aggregazione | Scrittura funzione, Refactor Pythonic, Spiegazione codice altrui |
| 6. Salvataggio | Scrittura funzione, Spiegazione codice altrui (sullo SQL) |

---

## Pianificazione prima del codice

> Voglio scrivere uno script che [obiettivo]. Prima di generare codice, elenca i 5 step principali, le dipendenze, e i potenziali punti di fallimento.

**Quando:** prima di ogni riga di codice. Una volta.
**Cosa guardare nella risposta:** cosa ha dato per scontato. Il separatore? L'encoding? Una regola che non gli hai detto? Il piano si corregge a mano, e le correzioni vanno nel diario.

## Scrittura funzione

> Scrivi una funzione che [comportamento], con questi input [tipi] e questo output [tipo]. Includi gestione edge case [casi] e docstring.

**Variante utile:** aggiungi in fondo *"Prima di scrivere il codice, elenca gli edge case che vedi."* Così gli edge case li propone l'AI e tu decidi quali tenere. È la domanda 2 dell'autovalutazione.
**Cosa guardare:** ogni edge case che ha aggiunto e che non è nelle regole del Comune. Se non è nelle regole e non è nel dato, è una regola inventata.

## Debug da traceback

> Questo codice [snippet] solleva [traceback]. Spiega la causa, suggerisci 2 fix alternativi, e indica il più robusto.

**Quando:** al primo errore. Non prima di aver letto il traceback tu, non dopo tre tentativi a caso.
**Cosa guardare:** "più robusto" secondo chi? Un fix che non fallisce mai può essere un fix che nasconde l'errore. Dei due, scegli quello che sai spiegare.

## Test unitari

> Per questa funzione [funzione], scrivi 5 test unitari con pytest che coprano caso base, edge case, input non validi, e un caso di regressione.

**Variante che ti serve qui:** *"Le attese sui conteggi devono venire da data/manifest.json, non da numeri scritti a mano."*
**Cosa guardare:** di ogni assert, chiediti quale bug lo farebbe diventare rosso. Se non ti viene in mente nessuno, l'assert non verifica niente. Aggiungi tu il test che l'AI non propone: la funzione non modifica la lista che riceve.

## Spiegazione codice altrui

> Spiegami questo codice riga per riga [snippet], identificando convenzioni, possibili bug e parti che andrebbero migliorate.

**Quando:** su qualunque cosa stai per committare e non sapresti difendere. Lo SQL della fase 6, per esempio.
**Cosa guardare:** se dopo la spiegazione sai rispondere a "cosa succede se…". Se no, chiedi ancora. Non committare prima.

## Refactor Pythonic

> Riscrivi questo codice [snippet] in modo più Pythonic e leggibile, spiegando ogni cambiamento. Mantieni invariati input e output.

**Quando:** dopo che i test sono verdi. Mai prima.
**Cosa guardare:** "mantieni invariati input e output" lo rispetta? Un `.sort()` al posto di `sorted()` cambia l'input. Lancia i test dopo, e leggi anche la prosa sotto il codice: gli avvertimenti stanno lì.

## Conversione approccio

> Riscrivi questo codice imperativo [snippet] in stile funzionale (map/filter/comprehension), motivando i pro e contro.

**Quando:** se vuoi. Non è obbligatorio per l'esercizio.
**Cosa guardare:** i contro. Se non ne elenca nessuno, non ha fatto quello che hai chiesto.

---

Nel `DIARIO.md` della soluzione (tag `soluzione`) vedi come li ho riempiti io,
fase per fase, e cosa ho tenuto di quello che hanno prodotto. Guardalo dopo,
non prima.
