# Piano

Chiesto all'AI prima di scrivere una riga, con il pattern "Pianificazione prima
del codice". Sotto, la sua risposta con le mie correzioni in grassetto.

## I cinque step

1. **Lettura** — `src/leggi.py`. Apre `letture_2025.csv`, restituisce le righe.
   L'AI proponeva `csv.DictReader` con encoding UTF-8. **Corretto:** il separatore
   è `;`, non l'ha visto perché non ha aperto il file. L'encoding lo scopro
   provando: UTF-8 è un'ipotesi, non un fatto.
2. **Validazione** — `src/valida.py`. Separa valide e scarti, ogni scarto con un
   motivo. L'AI proponeva di scartare i valori negativi. **Tolto:** non è nelle
   regole del Comune e nel file non ce ne sono. Aggiunto invece: zero è valido.
3. **Deduplica e ordinamento** — `src/aggrega.py`. L'AI proponeva "rimuovi i
   duplicati tenendo la prima occorrenza". **Corretto:** vale l'ultima. È la
   regola scritta nella consegna, e l'AI non l'ha letta.
4. **Aggregazione** — stesso file. Consumo mensile per edificio, tipo, unità.
   L'AI proponeva di raggruppare per edificio e mese. **Aggiunto:** il tipo, o si
   sommano kWh con m³.
5. **Salvataggio e CLI** — `src/store.py`, `src/cli.py`. Tabella unica,
   `UNIQUE (id_contatore, data)`, riepilogo a schermo.

## Dipendenze

Solo standard library: `csv`, `datetime`, `sqlite3`, `argparse`. `pytest` per i test.

## Punti di fallimento previsti dall'AI

- Encoding del file (ha detto "potrebbe non essere UTF-8": giusto, e infatti)
- Formato dei numeri (ha detto "virgola decimale": giusto, ma ha mancato le migliaia)
- Righe incomplete
- Contatori non presenti nell'anagrafica (**non nel dato, ma il codice non deve nasconderlo:** se manca, errore, non "sconosciuto")

## Cosa ha mancato

- Le migliaia con il punto: `1.234,5`. L'ho scoperto al primo traceback.
- La regola "vale l'ultima". Non poteva saperla: non gliel'avevo detta nel prompt.
  Il piano si corregge, non si ributta.
