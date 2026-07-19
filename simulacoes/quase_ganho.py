"""Por que "faltou pouco" acontece tanto?

O quase-ganho (near miss) é a única derrota que o cérebro processa como
progresso. Estudos de neuroimagem mostram que ele ativa as mesmas áreas de
recompensa que a vitória, e que aumenta a vontade de continuar jogando.

Este script separa três coisas que costumam ser confundidas:

  1. Quanto o "quase" já aconteceria por puro acaso.
  2. Quanto ele acontece com os rolos ponderados da página.
  3. Quanto de fato se ganha, nos dois casos.

O ponto não é que a ponderação multiplique muito o quase-ganho. É que o
quase-ganho é ABUNDANTE de qualquer jeito, e a vitória, não. O contraste
entre "quase sempre quase" e "quase nunca" é o motor.
"""

import argparse
import random
from typing import List, Tuple

from .config import formatar_numero, formatar_pct

SIMBOLOS = ("7", "4", "9")


def classificar(res: Tuple[str, str, str]) -> str:
    """Quase-ganho é QUALQUER par igual, em qualquer posição."""
    if res[0] == res[1] == res[2]:
        return "vitoria"
    if res[0] == res[1] or res[0] == res[2] or res[1] == res[2]:
        return "quase"
    return "nada"


def girar_justo(rng: random.Random) -> Tuple[str, str, str]:
    return tuple(rng.choice(SIMBOLOS) for _ in range(3))       # type: ignore


def girar_ponderado(rng: random.Random) -> Tuple[str, str, str]:
    """Como a página gira: o "7" domina as duas primeiras casas e a
    terceira quase nunca fecha."""
    a = "7" if rng.random() < 0.72 else SIMBOLOS[1 + (0 if rng.random() < .5 else 1)]
    b = "7" if rng.random() < 0.72 else SIMBOLOS[1 + (0 if rng.random() < .5 else 1)]
    if a == b:
        c = a if rng.random() < 0.08 else SIMBOLOS[(SIMBOLOS.index(a) + 1) % 3]
    else:
        c = rng.choice(SIMBOLOS)
    return (a, b, c)


def medir(girar, n: int, rng: random.Random) -> dict:
    contagem = {"vitoria": 0, "quase": 0, "nada": 0}
    for _ in range(n):
        contagem[classificar(girar(rng))] += 1
    return {k: v / n for k, v in contagem.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--giros", type=int, default=1_000_000)
    ap.add_argument("--semente", type=int, default=None)
    args = ap.parse_args()
    rng = random.Random(args.semente)

    print("=" * 64)
    print("O QUASE-GANHO")
    print("=" * 64)
    print(f"{formatar_numero(args.giros)} giros de cada tipo, "
          f"três símbolos por rolo.\n")

    justo = medir(girar_justo, args.giros, rng)
    pond = medir(girar_ponderado, args.giros, rng)

    print(f"  {'':<22} {'rolos honestos':>16} {'rolos da página':>17}")
    print("  " + "-" * 57)
    for chave, rot in (("vitoria", "ganhou de verdade"),
                       ("quase", "quase ganhou"),
                       ("nada", "nem chegou perto")):
        print(f"  {rot:<22} {formatar_pct(justo[chave], 2):>16} "
              f"{formatar_pct(pond[chave], 2):>17}")
    print()
    print(f"  Com rolos honestos, 'dois iguais' já sai em "
          f"{formatar_pct(justo['quase'], 1)} dos giros: é o acaso,")
    print("  não a máquina. A ponderação leva isso para "
          f"{formatar_pct(pond['quase'], 1)}, e ao mesmo tempo")
    print(f"  derruba a vitória de {formatar_pct(justo['vitoria'], 2)} para "
          f"{formatar_pct(pond['vitoria'], 2)}.")
    print()
    razao_justa = justo["quase"] / max(justo["vitoria"], 1e-12)
    razao_pond = pond["quase"] / max(pond["vitoria"], 1e-12)
    print(f"  quase por vitória, honesto : {formatar_numero(razao_justa, 1)} para 1")
    print(f"  quase por vitória, página  : {formatar_numero(razao_pond, 1)} para 1")
    print()
    print(f"É essa razão que importa: nos rolos da página, a sensação de estar")
    print(f"perto chega {formatar_numero(razao_pond, 0)} vezes mais do que o prêmio, "
          "e o cérebro não guarda")
    print("essa diferença.")
    print("Uma derrota que parece progresso é a melhor derrota que existe")
    print("para quem cobra pela próxima tentativa.")
    print()


if __name__ == "__main__":
    main()
