import copy
import json
from datetime import date
from pathlib import Path

import pytest

from src.leggi import leggi_csv
from src.valida import numero_italiano, valida

MANIFEST = json.loads(Path("data/manifest.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def righe():
    return leggi_csv(Path("data/letture_2025.csv"))


def test_numero_italiano_migliaia_e_decimali():
    assert numero_italiano("1.234,5") == 1234.5
    assert numero_italiano("99,8") == 99.8
    assert numero_italiano("0,0") == 0.0


def test_numero_italiano_rifiuta_testo():
    with pytest.raises(ValueError):
        numero_italiano("n/d")


def test_i_conteggi_tornano_col_manifest(righe):
    valide, scarti = valida(righe)
    assert len(valide) == MANIFEST["righe_valide_attese"]
    assert len(scarti) == (
        MANIFEST["righe_malformate"]
        + MANIFEST["righe_valore_vuoto"]
        + MANIFEST["righe_stato_err"]
    )


def test_ogni_scarto_ha_il_suo_motivo(righe):
    _, scarti = valida(righe)
    motivi = [s.split(": ", 1)[1] for s in scarti]
    assert sum(m == "campi mancanti" for m in motivi) == MANIFEST["righe_malformate"]
    assert sum(m == "valore vuoto" for m in motivi) == MANIFEST["righe_valore_vuoto"]
    assert sum(m == "stato ERR" for m in motivi) == MANIFEST["righe_stato_err"]


def test_zero_e_un_valore_valido():
    valide, scarti = valida([["2002", "Scuola", "2025-07-15", "0,0", "OK"]])
    assert scarti == []
    assert valide[0]["valore"] == 0.0


def test_stima_e_valida_err_no():
    valide, scarti = valida([
        ["2001", "Scuola", "2025-01-01", "10,0", "STIMA"],
        ["2001", "Scuola", "2025-01-02", "10,0", "ERR"],
    ])
    assert len(valide) == 1
    assert scarti == ["riga 3: stato ERR"]


def test_la_data_diventa_una_date():
    valide, _ = valida([["2001", "Scuola", "2025-03-09", "1,0", "OK"]])
    assert valide[0]["data"] == date(2025, 3, 9)


def test_valida_non_muta_l_input(righe):
    prima = copy.deepcopy(righe[:50])
    valida(righe[:50])
    assert righe[:50] == prima
