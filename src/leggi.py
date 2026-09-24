"""Lettura del file delle letture.

Il file arriva da un gestionale Windows: cp1252, separatore punto e virgola.
UTF-8 era l'ipotesi di partenza ed e' caduta al primo nome con l'accento.
"""

import csv
from pathlib import Path

ENCODING = "cp1252"
SEPARATORE = ";"


def leggi_csv(percorso: Path) -> list[list[str]]:
    """Restituisce le righe del file senza l'intestazione, come liste di stringhe.

    Non valida niente: una riga corta resta corta. Se ne occupa `valida`.
    """
    with open(percorso, encoding=ENCODING, newline="") as f:
        righe = list(csv.reader(f, delimiter=SEPARATORE))
    return righe[1:]
