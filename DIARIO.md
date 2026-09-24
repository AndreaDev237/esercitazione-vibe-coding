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

**Cosa ho accettato e cosa no:**

**Perché:**

## 4. Test

**Prompt usato:**

**Cosa ho accettato e cosa no:**

**Perché:**

## 5. Aggregazione

**Prompt usato:**

**Cosa ho accettato e cosa no:**

**Perché:**

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
