"""Validazione delle letture: valide da una parte, scarti con motivo dall'altra."""

from datetime import date

STATI_VALIDI = {"OK", "STIMA"}
CAMPI_ATTESI = 5


def numero_italiano(testo: str) -> float:
    """'1.234,5' -> 1234.5. Il punto separa le migliaia, la virgola i decimali."""
    return float(testo.replace(".", "").replace(",", "."))


def valida(righe: list[list[str]]) -> tuple[list[dict], list[str]]:
    """Separa le righe valide dagli scarti.

    Restituisce una nuova lista di letture (dizionari) e una lista di motivi,
    uno per riga scartata. Non modifica `righe`.
    """
    valide = []
    scarti = []
    for numero_riga, riga in enumerate(righe, start=2):  # la 1 e' l'intestazione
        if len(riga) != CAMPI_ATTESI:
            scarti.append(f"riga {numero_riga}: campi mancanti")
            continue
        id_contatore, edificio, data, valore, stato = riga
        if stato not in STATI_VALIDI:
            scarti.append(f"riga {numero_riga}: stato {stato}")
            continue
        if valore == "":
            scarti.append(f"riga {numero_riga}: valore vuoto")
            continue
        try:
            valore_num = numero_italiano(valore)
        except ValueError:
            scarti.append(f"riga {numero_riga}: valore non numerico {valore!r}")
            continue
        valide.append({
            "id_contatore": id_contatore,
            "edificio": edificio,
            "data": date.fromisoformat(data),
            "valore": valore_num,
            "stato": stato,
        })
    return valide, scarti
