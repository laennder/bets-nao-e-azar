"""A Lei dos Grandes Números contra o apostador.

Em 10 apostas quase tudo pode acontecer. Em 10.000, só uma coisa acontece.

A perda esperada cresce LINEARMENTE com o número de apostas, enquanto a
oscilação cresce com a RAIZ desse número. A sorte é diluída; a margem não.
"""

import argparse
import random

from .aposta import sessao
from .config import (APOSTA, DEPOSITO, BANCA_INICIAL, formatar_numero,
                     formatar_reais)
from .dados import jogos, perda_por_real


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--semente", type=int, default=None)
    ap.add_argument("--ao-vivo", action="store_true")
    args = ap.parse_args()
    rng = random.Random(args.semente)
    js = jogos(args.ao_vivo)
    p = perda_por_real(js)

    print("=" * 64)
    print("O LONGO PRAZO")
    print("=" * 64)
    print(f"Começa com {formatar_reais(BANCA_INICIAL)}, aposta "
          f"{formatar_reais(APOSTA)} por vez. Zerou, deposita "
          f"{formatar_reais(DEPOSITO)}.\n")

    print(f"{'apostas':>9} {'saldo':>12} {'depositado':>13} "
          f"{'resultado':>13} {'depósitos':>10} {'esperado':>13}")
    print("-" * 74)
    for n in (10, 100, 1_000, 10_000):
        r = sessao(js, n, BANCA_INICIAL, APOSTA, DEPOSITO, rng)
        print(f"{formatar_numero(n):>9} {formatar_reais(r['banca']):>12} "
              f"{formatar_reais(r['depositado']):>13} "
              f"{formatar_reais(r['resultado']):>13} "
              f"{r['aportes']:>10} {formatar_reais(-p * APOSTA * n):>13}")

    print()
    print("Repare nas duas colunas do meio. O saldo na conta sobe e desce e")
    print("quase sempre parece administrável: é o que o aplicativo te mostra.")
    print("Quem só cresce é o total que saiu do seu bolso.")
    print()
    print("A sorte é volátil. A margem é constante.")
    print("No longo prazo, o constante vence o volátil.")
    print()
    print("Você não perdeu por azar. Perdeu porque a conta foi feita para isso.")
    print()


if __name__ == "__main__":
    main()
