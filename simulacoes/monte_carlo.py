"""De 10.000 apostadores, quantos terminam no lucro?

Cada pessoa simulada aposta 500 vezes com as cotações reais da rodada,
depositando de novo toda vez que zera. O que interessa não é a média (essa
já se sabe negativa), é a FORMA da distribuição: uma montanha inteira à
esquerda do zero e uma cauda fina de sortudos à direita.

É essa cauda que aparece nas redes sociais. A montanha, não.
"""

import argparse
import random
from typing import List

from .aposta import sessao
from .config import (DEPOSITO, APOSTA, APOSTADORES, APOSTAS_POR_PESSOA,
                     BANCA_INICIAL, formatar_numero, formatar_pct,
                     formatar_reais)
from .dados import jogos


def histograma(valores: List[float], faixas: int = 21) -> None:
    lo, hi = min(valores), max(valores)
    if hi <= lo:
        return
    largura = (hi - lo) / faixas
    baldes = [0] * faixas
    for v in valores:
        i = min(faixas - 1, int((v - lo) / largura))
        baldes[i] += 1
    pico = max(baldes)

    print(f"  {'resultado':>26}   {'':<42} {'pessoas':>7}")
    for i, n in enumerate(baldes):
        centro = lo + largura * (i + 0.5)
        barra = "█" * round(n / pico * 42)
        marca = " <- zero" if lo + largura * i <= 0 < lo + largura * (i + 1) else ""
        print(f"  {formatar_reais(centro):>26}   {barra:<42} {n:>7}{marca}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pessoas", type=int, default=APOSTADORES)
    ap.add_argument("--apostas", type=int, default=APOSTAS_POR_PESSOA)
    ap.add_argument("--semente", type=int, default=None)
    ap.add_argument("--ao-vivo", action="store_true")
    args = ap.parse_args()
    rng = random.Random(args.semente)
    js = jogos(args.ao_vivo)

    print("=" * 64)
    print(f"{formatar_numero(args.pessoas)} APOSTADORES")
    print("=" * 64)
    print(f"{formatar_numero(args.pessoas)} pessoas, {args.apostas} apostas cada, "
          f"{formatar_reais(APOSTA)} por aposta.")
    print(f"Começam com {formatar_reais(BANCA_INICIAL)} e depositam mais "
          f"{formatar_reais(DEPOSITO)} sempre que zeram.\n")

    resultados, aportes, no_lucro, quebraram = [], 0, 0, 0
    for _ in range(args.pessoas):
        r = sessao(js, args.apostas, BANCA_INICIAL, APOSTA, DEPOSITO, rng)
        resultados.append(r["resultado"])
        aportes += r["aportes"]
        if r["resultado"] > 0:
            no_lucro += 1
        if r["aportes"] > 1:        # zerou e precisou recarregar
            quebraram += 1

    resultados.sort()
    n = len(resultados)
    print(f"  terminaram no lucro     : {formatar_pct(no_lucro / n)}  "
          f"({formatar_numero(no_lucro)} pessoas)")
    print(f"  zeraram ao menos 1 vez  : {formatar_pct(quebraram / n)}  "
          f"({formatar_numero(quebraram)} pessoas)")
    print(f"  resultado médio         : {formatar_reais(sum(resultados) / n)}")
    print(f"  mediana                 : {formatar_reais(resultados[n // 2])}")
    print(f"  depósitos por pessoa    : {formatar_numero(aportes / n, 1)}")
    print(f"  melhor resultado        : {formatar_reais(resultados[-1])}")
    print(f"  pior resultado          : {formatar_reais(resultados[0])}")
    print()
    histograma(resultados)
    print()
    print("A cauda da direita existe. Ela é real e alguém sempre está nela.")
    print("Ela também é a única parte deste gráfico que você vê no story de")
    print("alguém. O resto da distribuição não posta print.")
    print()


if __name__ == "__main__":
    main()
