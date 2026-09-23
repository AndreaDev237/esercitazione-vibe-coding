"""Genera il dataset dell'esercitazione del Modulo 4.

Deterministico: stesso seed, stesso file, stessi difetti nelle stesse righe.

Due file:
- data/contatori.csv   anagrafica, UTF-8, separatore virgola
- data/letture_2025.csv letture giornaliere, cp1252, separatore punto e virgola,
                        decimali con la virgola, migliaia col punto

Piu' data/manifest.json con i conteggi attesi, calcolati mentre si scrive.
"""

import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20250901

EDIFICI = {
    "E01": "Scuola Primaria Dante Alighieri",
    "E02": "Palazzo Comunale – Piazza Libertà",
    "E03": "Biblioteca Civica",
    "E04": "Asilo Nido Girotondo",
    "E05": "Piscina Comunale",
    "E06": "Centro Sportivo Città di Lodi",
}

# id, edificio, tipo, unita', (minimo, massimo) consumo giornaliero
CONTATORI = [
    ("2001", "E01", "elettrico", "kWh", (60.0, 220.0)),
    ("2002", "E01", "gas",       "m³", (0.0, 90.0)),
    ("2003", "E02", "elettrico", "kWh", (120.0, 380.0)),
    ("2004", "E02", "gas",       "m³", (0.0, 140.0)),
    ("2005", "E03", "elettrico", "kWh", (40.0, 160.0)),
    ("2006", "E04", "elettrico", "kWh", (30.0, 110.0)),
    ("2007", "E04", "gas",       "m³", (0.0, 60.0)),
    ("2008", "E05", "elettrico", "kWh", (800.0, 1600.0)),
    ("2009", "E05", "gas",       "m³", (40.0, 320.0)),
    ("2010", "E06", "elettrico", "kWh", (90.0, 340.0)),
]

PRIMO_GIORNO = date(2025, 1, 1)
ULTIMO_GIORNO = date(2025, 12, 31)

STATI_VALIDI = ("OK", "STIMA")
STATO_ERRORE = "ERR"

# Righe (1-based, intestazione esclusa) con soli 3 campi invece di 5.
RIGHE_MALFORMATE = [388, 1204, 2077, 2950, 3511]
# Righe con stato OK ma valore vuoto: valide di stato, non di valore.
RIGHE_VALORE_VUOTO = [151, 917, 1660, 2333, 2801, 3402]
# Coppie contatore+giorno che compaiono due volte: la seconda e' la correzione,
# accodata in fondo al file. Vale l'ultima.
N_CORREZIONI = 30
# Righe con stato ERR (valore presente ma non attendibile).
N_ERRORI = 120


def consumo(contatore, giorno, rng):
    """Consumo giornaliero plausibile: il gas segue la stagione, l'elettrico meno."""
    _, _, tipo, _, (minimo, massimo) = contatore
    # 1.0 a gennaio, 0.0 a luglio
    stagione = (math.cos((giorno.timetuple().tm_yday - 15) / 365 * 2 * math.pi) + 1) / 2
    if tipo == "gas":
        base = minimo + (massimo - minimo) * stagione
        rumore = rng.uniform(-0.15, 0.15) * (massimo - minimo)
        return max(0.0, base + rumore)
    base = minimo + (massimo - minimo) * (0.4 + 0.3 * stagione)
    if giorno.weekday() >= 5:
        base *= 0.55
    return base + rng.uniform(-0.1, 0.1) * (massimo - minimo)


def formatta(valore):
    """Formato italiano: virgola decimale, punto per le migliaia."""
    intero, decimale = f"{valore:.1f}".split(".")
    intero_it = f"{int(intero):,}".replace(",", ".")
    return f"{intero_it},{decimale}"


def genera(cartella: Path):
    rng = random.Random(SEED)
    cartella.mkdir(parents=True, exist_ok=True)

    with open(cartella / "contatori.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["IdContatore", "IdEdificio", "Edificio", "Tipo", "UnitaMisura"])
        for cid, eid, tipo, unita, _ in CONTATORI:
            w.writerow([cid, eid, EDIFICI[eid], tipo, unita])

    righe = []  # (contatore, giorno, valore_float | None, stato)
    giorno = PRIMO_GIORNO
    while giorno <= ULTIMO_GIORNO:
        for c in CONTATORI:
            righe.append([c, giorno, consumo(c, giorno, rng), "OK"])
        giorno += timedelta(days=1)

    # Le righe malformate e quelle col valore vuoto restano OK di stato, cosi'
    # ogni difetto del file ha una causa sola e i conteggi non si sovrappongono.
    speciali = {n - 1 for n in RIGHE_MALFORMATE + RIGHE_VALORE_VUOTO}
    normali = [i for i in range(len(righe)) if i not in speciali]
    for i in rng.sample(normali, N_ERRORI):
        righe[i][3] = STATO_ERRORE
    stime = rng.sample([i for i in normali if righe[i][3] == "OK"], 200)
    for i in stime:
        righe[i][3] = "STIMA"

    candidati = [i for i in normali if righe[i][3] in STATI_VALIDI]
    correzioni = []
    for i in rng.sample(candidati, N_CORREZIONI):
        c, g, v, s = righe[i]
        correzioni.append([c, g, v * rng.uniform(1.2, 1.6), "OK"])

    # Conteggi attesi, calcolati sulla stessa lista che finisce nel file
    valide = {}
    n_malformate = n_vuote = n_err = 0
    tutte = righe + correzioni
    for numero, (c, g, v, s) in enumerate(tutte, start=1):
        if numero in RIGHE_MALFORMATE:
            n_malformate += 1
            continue
        if numero in RIGHE_VALORE_VUOTO:
            n_vuote += 1
            continue
        if s == STATO_ERRORE:
            n_err += 1
            continue
        valide[(c[0], g)] = round(v, 1)  # l'ultima vince
    n_valide = len(tutte) - n_malformate - n_vuote - n_err

    unita_per_contatore = {c[0]: c[3] for c in CONTATORI}
    tot = {"kWh": 0.0, "m³": 0.0}
    piscina_gennaio = 0.0
    for (cid, g), v in valide.items():
        tot[unita_per_contatore[cid]] += v
        if cid == "2008" and g.month == 1:
            piscina_gennaio += v

    prima_non_ascii = None
    with open(cartella / "letture_2025.csv", "w", encoding="cp1252", newline="") as f:
        f.write("IdContatore;Edificio;Data;Valore;Stato\n")
        for numero, (c, g, v, s) in enumerate(tutte, start=1):
            nome = EDIFICI[c[1]]
            if prima_non_ascii is None and not nome.isascii():
                prima_non_ascii = numero + 1  # +1 per l'intestazione
            if numero in RIGHE_MALFORMATE:
                f.write(f"{c[0]};{nome};{g.isoformat()}\n")
                continue
            valore = "" if numero in RIGHE_VALORE_VUOTO else formatta(v)
            f.write(f"{c[0]};{nome};{g.isoformat()};{valore};{s}\n")

    manifest = {
        "righe_totali": len(tutte),
        "righe_malformate": n_malformate,
        "righe_valore_vuoto": n_vuote,
        "righe_stato_err": n_err,
        "righe_valide_attese": n_valide,
        "correzioni": N_CORREZIONI,
        "letture_dopo_dedup": len(valide),
        "totale_kwh_2025": round(tot["kWh"], 1),
        "totale_m3_2025": round(tot["m³"], 1),
        "piscina_elettrico_2025_01_kwh": round(piscina_gennaio, 1),
        "prima_riga_non_ascii": prima_non_ascii,
    }
    with open(cartella / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


if __name__ == "__main__":
    print(json.dumps(genera(Path("data")), indent=2, ensure_ascii=False))
