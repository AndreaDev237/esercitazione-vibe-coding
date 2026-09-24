"""La pipeline intera, da riga di comando: leggi, valida, deduplica, ordina, salva."""

import argparse
import sqlite3
from pathlib import Path

from src import aggrega, store
from src.leggi import leggi_csv
from src.valida import valida


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Pipeline consumi degli edifici comunali")
    parser.add_argument("--letture", type=Path, default=Path("data/letture_2025.csv"))
    parser.add_argument("--contatori", type=Path, default=Path("data/contatori.csv"))
    parser.add_argument("--output", type=Path, default=Path("consumi.db"))
    args = parser.parse_args(argv)

    righe = leggi_csv(args.letture)
    valide, scarti = valida(righe)
    uniche = aggrega.ordina_per_data(aggrega.tieni_ultima(valide))
    anagrafica = aggrega.carica_anagrafica(args.contatori)

    with sqlite3.connect(args.output) as conn:
        store.crea_schema(conn)
        inserite = store.inserisci(conn, uniche, anagrafica)

    mensili = aggrega.consumo_mensile(uniche, anagrafica)
    print(
        f"lette: {len(righe)} | scartate: {len(scarti)} | "
        f"correzioni: {len(valide) - len(uniche)} | inserite: {inserite} | "
        f"aggregati mensili: {len(mensili)}"
    )


if __name__ == "__main__":
    main()
