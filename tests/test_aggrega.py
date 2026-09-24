import copy
import json
from datetime import date
from pathlib import Path

import pytest

from src import aggrega
from src.leggi import leggi_csv
from src.valida import valida

MANIFEST = json.loads(Path("data/manifest.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def valide():
    return valida(leggi_csv(Path("data/letture_2025.csv")))[0]


@pytest.fixture(scope="module")
def anagrafica():
    return aggrega.carica_anagrafica(Path("data/contatori.csv"))


def lettura(cid, giorno, valore):
    return {"id_contatore": cid, "edificio": "x", "data": date.fromisoformat(giorno), "valore": valore, "stato": "OK"}


def test_anagrafica_indicizzata_per_contatore(anagrafica):
    assert len(anagrafica) == 10
    assert anagrafica["2008"]["Tipo"] == "elettrico"
    assert anagrafica["2009"]["UnitaMisura"] == "m³"


def test_tieni_ultima_vale_la_correzione():
    letture = [lettura("2001", "2025-01-01", 10.0), lettura("2001", "2025-01-02", 20.0), lettura("2001", "2025-01-01", 15.0)]
    risultato = aggrega.tieni_ultima(letture)
    assert [l["valore"] for l in risultato] == [15.0, 20.0]


def test_tieni_ultima_toglie_tutte_le_correzioni(valide):
    assert len(aggrega.tieni_ultima(valide)) == MANIFEST["letture_dopo_dedup"]


def test_tieni_ultima_non_muta_l_input(valide):
    prima = copy.deepcopy(valide)
    aggrega.tieni_ultima(valide)
    assert valide == prima


def test_ordina_per_data_non_muta_l_input(valide):
    # Le correzioni stanno in coda al file con date vecchie: il campione
    # non e' gia' ordinato, altrimenti un .sort() in place passerebbe inosservato.
    campione = valide[-40:] + valide[:40]
    prima = copy.deepcopy(campione)
    ordinato = aggrega.ordina_per_data(campione)
    assert campione == prima
    assert ordinato[0]["data"] <= ordinato[-1]["data"]


def test_consumo_mensile_non_mescola_le_unita(valide, anagrafica):
    mensili = aggrega.consumo_mensile(aggrega.tieni_ultima(valide), anagrafica)
    kwh = sum(v for (_, _, unita, _), v in mensili.items() if unita == "kWh")
    m3 = sum(v for (_, _, unita, _), v in mensili.items() if unita == "m³")
    assert round(kwh, 1) == MANIFEST["totale_kwh_2025"]
    assert round(m3, 1) == MANIFEST["totale_m3_2025"]


def test_consumo_mensile_piscina_gennaio(valide, anagrafica):
    mensili = aggrega.consumo_mensile(aggrega.tieni_ultima(valide), anagrafica)
    chiave = ("Piscina Comunale", "elettrico", "kWh", "2025-01")
    assert round(mensili[chiave], 1) == MANIFEST["piscina_elettrico_2025_01_kwh"]


def test_contatore_sconosciuto_e_un_errore(anagrafica):
    with pytest.raises(KeyError):
        aggrega.consumo_mensile([lettura("9999", "2025-01-01", 1.0)], anagrafica)
