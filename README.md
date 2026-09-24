# Esercitazione — Consumi energetici degli edifici comunali

Il Comune ti passa un anno di letture dei contatori dei suoi edifici e ti chiede
una pipeline che le legga, le pulisca, le aggreghi per edificio e mese, e le
salvi in un database. Stesso lavoro del corso, dati diversi.

**Non si valuta il numero che ottieni. Si valuta come ci arrivi.** Quello che
consegni è il codice *e* il diario di come l'hai scritto con l'AI.

## I file

| File | Cosa contiene |
|---|---|
| `data/letture_2025.csv` | una lettura al giorno per contatore, tutto il 2025 |
| `data/contatori.csv` | l'anagrafica: a quale edificio appartiene ogni contatore, cosa misura, in che unità |
| `data/manifest.json` | i conteggi attesi. Li ha scritti il generatore del dataset: sono la fonte per i tuoi test |
| `PROMPT-PATTERN.md` | i sette prompt pattern del corso, come template da riempire, e a quale fase servono |
| `tools/genera_dataset.py` | il generatore. Puoi leggerlo, ma **non è un modo per risolvere l'esercizio**: il codice che scrivi deve funzionare senza sapere come è nato il file |

Apri i CSV con un editor prima di scrivere codice. Guardali.

## Cosa deve fare la pipeline

Quattro fasi, come nel corso. Ognuna è un modulo in `src/` con i suoi test in `tests/`.

1. **Leggere** `letture_2025.csv` e restituire una lista di righe.
2. **Validare**: separare le righe valide dagli scarti, e per ogni scarto dire perché.
3. **Aggregare**: consumo mensile per edificio e tipo di contatore, usando l'anagrafica.
4. **Salvare** su SQLite, con una CLI che esegue tutto e stampa un riepilogo.

## Le regole del dato

Sono regole del Comune, non dell'AI. Se un suggerimento le contraddice, il suggerimento è sbagliato.

- Una lettura è **valida** se ha tutti i campi, un valore numerico, e stato `OK` oppure `STIMA`. Lo stato `ERR` si scarta.
- Un valore **zero è valido**. D'estate il gas non si consuma.
- Se lo stesso contatore ha **due letture nello stesso giorno**, la seconda è una correzione: **vale l'ultima nel file**, non la prima.
- Non si sommano mai kWh con m³. L'aggregazione tiene separati **edificio, tipo di contatore e mese**.
- Il database deve **rifiutare** una seconda lettura per la stessa coppia contatore e giorno.

## Cosa devi consegnare

Il repo, con un commit per fase, più il **`DIARIO.md` compilato**. Il diario ha sei sezioni, una per fase, e in ognuna tre righe obbligatorie: il prompt che hai usato, cosa hai accettato e cosa no, e perché.

In fondo al diario ci sono due righe che non si possono lasciare vuote:

- **una cosa che hai rifiutato** dall'AI, e il motivo;
- **una riga di codice che non sai spiegare**, se c'è. Se non c'è, scrivi che hai controllato.

## Come si lavora

Vale la regola del modulo: **nessuna risposta dell'AI entra nel repo senza che tu l'abbia letta.** Chiedi, leggi, giudica, poi scrivi. Non è vietato accettare quello che propone; è vietato accettarlo senza saperlo spiegare.

Le tecniche sono quelle del corso, e i prompt sono in `PROMPT-PATTERN.md`: pianificare prima di scrivere, far proporre gli edge case all'AI, chiedere la spiegazione di un traceback invece di provare a caso, derivare le attese dei test dai dati invece che a mano, scrivere il test di integrità prima che serva, rifiutare un refactor che ottimizza una cosa e ne rompe un'altra.

**I tuoi numeri finali possono essere diversi dai miei.** Se la tua validazione fa una scelta diversa, il totale cambia. Quelli che devono tornare sono nel manifest, e il diario deve dire perché gli altri sono diversi.

## Autovalutazione

Alla fine, dieci domande. Sì o no. Sono le stesse che uso io nella soluzione.

1. Hai chiesto un piano prima di scrivere codice, e lo hai corretto?
2. Almeno tre edge case li ha proposti l'AI, e li hai gestiti?
3. Almeno un traceback lo hai risolto con un prompt, non a tentativi?
4. Le attese dei test vengono dal manifest, non da numeri scritti a mano?
5. C'è un test che verifica che le funzioni non modifichino la lista che ricevono?
6. Hai rifiutato almeno un suggerimento, e il diario dice perché?
7. La regola "vale l'ultima" è quella del Comune, non quella che l'AI dà per scontata?
8. Il database rifiuta davvero un doppione, e c'è un test che lo prova?
9. Hai letto il diff prima di ogni commit?
10. Sai spiegare ogni funzione che hai committato?

Sette su dieci è un buon lavoro. Dieci su dieci, e il diario è onesto, è il modulo fatto bene.

## Tempo

Due o tre ore. Se stai andando molto oltre, probabilmente stai facendo scrivere all'AI cose che non hai capito, e poi le stai debuggando. Fermati, torna al piano.

## Setup

```bash
git clone https://github.com/AndreaDev237/esercitazione-vibe-coding.git
cd esercitazione-vibe-coding
python -m pytest -q
```

Nessuna dipendenza oltre a `pytest`. Solo standard library.
