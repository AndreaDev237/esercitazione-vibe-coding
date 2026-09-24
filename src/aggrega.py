"""Anagrafica, deduplica, ordinamento e aggregazione mensile.

Tutte le funzioni che ricevono una lista restituiscono una lista nuova.
"""

import csv
from pathlib import Path


def carica_anagrafica(percorso: Path) -> dict[str, dict]:
    """Restituisce l'anagrafica indicizzata per IdContatore."""
    with open(percorso, encoding="utf-8", newline="") as f:
        return {riga["IdContatore"]: riga for riga in csv.DictReader(f)}


def tieni_ultima(letture: list[dict]) -> list[dict]:
    """Stesso contatore e stesso giorno: vale l'ultima nel file.

    E' la regola del Comune: la seconda lettura e' una correzione. Restituisce
    una nuova lista, nell'ordine di prima apparizione di ogni coppia.
    """
    ultime = {}
    for lettura in letture:
        ultime[(lettura["id_contatore"], lettura["data"])] = lettura
    return list(ultime.values())


def ordina_per_data(letture: list[dict]) -> list[dict]:
    """Restituisce una nuova lista ordinata per data e contatore."""
    return sorted(letture, key=lambda l: (l["data"], l["id_contatore"]))


def consumo_mensile(letture: list[dict], anagrafica: dict[str, dict]) -> dict[tuple, float]:
    """Somma dei consumi per (edificio, tipo, unita', 'YYYY-MM').

    Un contatore assente dall'anagrafica e' un errore, non una categoria:
    KeyError, non 'sconosciuto'.
    """
    totali = {}
    for lettura in letture:
        contatore = anagrafica[lettura["id_contatore"]]
        chiave = (
            contatore["Edificio"],
            contatore["Tipo"],
            contatore["UnitaMisura"],
            lettura["data"].strftime("%Y-%m"),
        )
        totali[chiave] = totali.get(chiave, 0.0) + lettura["valore"]
    return totali
