import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from src import aggrega, store
from src.cli import main
from src.leggi import leggi_csv
from src.valida import valida

MANIFEST = json.loads(Path("data/manifest.json").read_text(encoding="utf-8"))


@pytest.fixture
def conn():
    with sqlite3.connect(":memory:") as c:
        store.crea_schema(c)
        yield c


@pytest.fixture(scope="module")
def anagrafica():
    return aggrega.carica_anagrafica(Path("data/contatori.csv"))


def lettura(cid, giorno, valore):
    return {"id_contatore": cid, "edificio": "x", "data": date.fromisoformat(giorno), "valore": valore, "stato": "OK"}


def test_inserisce_e_conta(conn, anagrafica):
    n = store.inserisci(conn, [lettura("2001", "2025-01-01", 1.0), lettura("2001", "2025-01-02", 2.0)], anagrafica)
    assert n == 2
    assert conn.execute("SELECT COUNT(*) FROM letture").fetchone()[0] == 2


def test_il_database_rifiuta_un_doppione(conn, anagrafica):
    store.inserisci(conn, [lettura("2001", "2025-01-01", 1.0)], anagrafica)
    with pytest.raises(sqlite3.IntegrityError):
        store.inserisci(conn, [lettura("2001", "2025-01-01", 99.0)], anagrafica)


def test_la_pipeline_intera_inserisce_le_letture_uniche(conn, anagrafica):
    valide, _ = valida(leggi_csv(Path("data/letture_2025.csv")))
    n = store.inserisci(conn, aggrega.tieni_ultima(valide), anagrafica)
    assert n == MANIFEST["letture_dopo_dedup"]


def test_la_cli_stampa_il_riepilogo(tmp_path, capsys):
    main(["--output", str(tmp_path / "consumi.db")])
    out = capsys.readouterr().out
    assert f"lette: {MANIFEST['righe_totali']}" in out
    assert f"correzioni: {MANIFEST['correzioni']}" in out
    assert f"inserite: {MANIFEST['letture_dopo_dedup']}" in out
