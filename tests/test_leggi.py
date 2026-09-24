import json
from pathlib import Path

from src.leggi import leggi_csv

LETTURE = Path("data/letture_2025.csv")
MANIFEST = json.loads(Path("data/manifest.json").read_text(encoding="utf-8"))


def test_legge_tutte_le_righe_senza_intestazione():
    righe = leggi_csv(LETTURE)
    assert len(righe) == MANIFEST["righe_totali"]
    assert righe[0][0] != "IdContatore"


def test_il_separatore_e_il_punto_e_virgola():
    prima = leggi_csv(LETTURE)[0]
    assert len(prima) == 5
    assert ";" not in prima[0]


def test_gli_accenti_sopravvivono_alla_lettura():
    riga = leggi_csv(LETTURE)[MANIFEST["prima_riga_non_ascii"] - 2]
    assert "Libertà" in riga[1]


def test_una_riga_corta_resta_corta():
    righe = leggi_csv(LETTURE)
    corte = [r for r in righe if len(r) != 5]
    assert len(corte) == MANIFEST["righe_malformate"]
