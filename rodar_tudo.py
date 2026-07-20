#!/usr/bin/env python3
"""Roda todas as simulações, na ordem em que a página as apresenta.

    python3 rodar_tudo.py              # com o retrato do mercado em dados/
    python3 rodar_tudo.py --ao-vivo    # com as cotações da rodada de agora
    python3 rodar_tudo.py --semente 7  # resultado reproduzível
"""

import argparse
import runpy
import sys

MODULOS = [
    ("margem", ["--ao-vivo"]),
    ("longo_prazo", ["--ao-vivo", "--semente"]),
    ("monte_carlo", ["--ao-vivo", "--semente"]),
    ("martingale", ["--semente"]),
    ("meta_de_saque", ["--ao-vivo", "--semente"]),
    ("quase_ganho", ["--semente"]),
    ("caminho_do_dinheiro", []),
    ("calculadora", ["--ao-vivo"]),
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ao-vivo", action="store_true",
                    help="busca as cotações e a taxa do Tesouro que a página usa agora")
    ap.add_argument("--semente", type=int, default=None,
                    help="fixa o sorteio, para o resultado ser reproduzível")
    ap.add_argument("--rapido", action="store_true",
                    help="menos repetições, para uma passada rápida")
    args = ap.parse_args()

    for nome, aceita in MODULOS:
        argv = [f"simulacoes/{nome}.py"]
        if args.ao_vivo and "--ao-vivo" in aceita:
            argv.append("--ao-vivo")
        if args.semente is not None and "--semente" in aceita:
            argv += ["--semente", str(args.semente)]
        if args.rapido:
            if nome == "monte_carlo":
                argv += ["--pessoas", "1000"]
            elif nome == "quase_ganho":
                argv += ["--giros", "100000"]
            elif nome == "martingale":
                argv += ["--rodadas", "40"]
            elif nome == "meta_de_saque":
                argv += ["--pessoas", "2000", "--rapido"]

        sys.argv = argv
        print()
        runpy.run_module(f"simulacoes.{nome}", run_name="__main__")

    print("=" * 64)
    print("Nenhum número aqui depende de acreditar em ninguém.")
    print("Mude os parâmetros, refaça as contas, discorde com dados.")
    print("=" * 64)
    print()


if __name__ == "__main__":
    main()
