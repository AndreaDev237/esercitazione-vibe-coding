"""Persistenza su SQLite. Una tabella, denormalizzata, con il vincolo del Comune."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS letture (
    id_contatore TEXT NOT NULL,
    edificio     TEXT NOT NULL,
    tipo         TEXT NOT NULL,
    unita        TEXT NOT NULL,
    data         TEXT NOT NULL,
    valore       REAL NOT NULL,
    UNIQUE (id_contatore, data)
)
"""


def crea_schema(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA)
    conn.commit()


def inserisci(conn: sqlite3.Connection, letture: list[dict], anagrafica: dict[str, dict]) -> int:
    """Inserisce le letture e restituisce quante ne ha scritte.

    Una seconda lettura per la stessa coppia contatore e giorno viola UNIQUE:
    sqlite3.IntegrityError. Non si cattura qui: chi chiama deve saperlo.
    """
    righe = []
    for lettura in letture:
        contatore = anagrafica[lettura["id_contatore"]]
        righe.append((
            lettura["id_contatore"],
            contatore["Edificio"],
            contatore["Tipo"],
            contatore["UnitaMisura"],
            lettura["data"].isoformat(),
            lettura["valore"],
        ))
    cursore = conn.executemany("INSERT INTO letture VALUES (?, ?, ?, ?, ?, ?)", righe)
    conn.commit()
    return cursore.rowcount
