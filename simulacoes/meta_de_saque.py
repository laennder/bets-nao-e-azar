"""E se eu combinar comigo mesmo de sacar quando ganhar um tanto?

É a objeção mais razoável que existe contra as outras simulações. Nelas o
apostador não tem regra de saída, então quebrar é quase uma questão de
tempo. Aqui ele tem: escolhe uma meta de lucro, e no instante em que a
alcança, saca e vai embora para sempre.

Duas coisas acontecem ao mesmo tempo, e é aí que quase todo mundo se
perde. Com meta pequena, a MAIORIA realmente bate a meta e sai ganhando.
E o resultado médio continua negativo.

Não há contradição. Quem bate a meta leva o valor combinado, que é pouco.
Quem quebra no caminho perde a banca inteira, que é muito. Mais gente
ganhando pouco não compensa menos gente perdendo tudo.

E a meta não é um dial que faça a conta virar: subir a meta só troca a
proporção. Mais gente quebra antes de chegar lá, e a média afunda.
"""

import argparse
import random
from typing import Dict, List

from .aposta import aposta_aleatoria
from .config import (APOSTA, BANCA_INICIAL, META_MAXIMA, META_MINIMA,
                     META_PADRAO, PESSOAS_META, TETO_DE_APOSTAS,
                     formatar_numero, formatar_pct, formatar_reais)
from .dados import jogos


def uma_pessoa(js: List[dict], meta: float, rng: random.Random) -> Dict:
    """Aposta até sacar a meta ou ficar sem nada. Devolve o desfecho."""
    banca = BANCA_INICIAL
    apostas = 0

    while apostas < TETO_DE_APOSTAS:
        if banca >= BANCA_INICIAL + meta:
            return {"resultado": banca - BANCA_INICIAL,
                    "apostas": apostas, "sacou": True}
        if banca < 0.01:
            break
        apostas += 1
        # Com menos de R$ 100 na conta, aposta o troco. É o que a pessoa
        # faz, e é o que faz todo mundo que perde terminar no mesmo ponto,
        # zerado, em vez de parar espalhado entre R$ 1 e R$ 99.
        banca += aposta_aleatoria(js, min(APOSTA, banca), rng)
        if banca < 0.01:
            banca = 0.0

    # Sair por aqui é raro a ponto de nunca ter acontecido nos testes: a
    # pessoa resolve, para um lado ou para o outro, em algumas dezenas de
    # apostas. O teto existe para o laço não poder ser infinito.
    return {"resultado": banca - BANCA_INICIAL,
            "apostas": apostas, "sacou": False}


def lote(js: List[dict], meta: float, pessoas: int,
         rng: random.Random) -> Dict:
    resultados, apostas, sacaram, quebraram = [], 0, 0, 0
    for _ in range(pessoas):
        p = uma_pessoa(js, meta, rng)
        resultados.append(p["resultado"])
        apostas += p["apostas"]
        if p["sacou"]:
            sacaram += 1
        elif p["resultado"] <= -BANCA_INICIAL + 0.01:
            quebraram += 1
    return {
        "resultados": resultados,
        "sacaram": sacaram,
        "quebraram": quebraram,
        "media": sum(resultados) / pessoas,
        "apostas": apostas / pessoas,
    }


def histograma(valores: List[float], faixas: int = 14) -> None:
    """Duas populações, não uma distribuição.

    Quem perde termina sempre no mesmo ponto, zerado, porque aposta o troco
    antes de acabar. Então esse grupo é uma linha só, com o valor exato, e
    não um balde cujo centro seria -R$ 958 para gente que perdeu -R$ 1.000.
    O resto, que é quem sacou, aí sim tem forma e vale distribuir em faixas.

    A barra de quem perdeu engole a escala, e é para engolir mesmo: a
    desproporção entre ela e a faixa de quem sacou é o argumento. Nada de
    eixo cortado aqui.
    """
    perdeu = [v for v in valores if v < 0]
    sacou = [v for v in valores if v >= 0]
    if not sacou:
        return
    pico = max(len(perdeu), 1)

    lo, hi = min(sacou), max(sacou)
    largura = (hi - lo) / faixas if hi > lo else 1.0
    baldes = [0] * faixas
    for v in sacou:
        baldes[min(faixas - 1, int((v - lo) / largura))] += 1
    pico = max(pico, max(baldes))

    print(f"  {'resultado':>17}   {'':<44} {'pessoas':>7}")
    if perdeu:
        barra = "█" * max(1, round(len(perdeu) / pico * 44))
        rotulo = f"perdeu tudo"
        print(f"  {rotulo:>17}   {barra:<44} {len(perdeu):>7}")
        print(f"  {'':>17}   {'':<44}")
    for i, n in enumerate(baldes):
        if not n:
            continue
        centro = lo + largura * (i + 0.5)
        barra = "█" * max(1, round(n / pico * 44))
        print(f"  {'+' + formatar_reais(centro):>17}   {barra:<44} {n:>7}")


def varredura(js: List[dict], pessoas: int, rng: random.Random) -> None:
    """A mesma simulação em cada meta possível, para ver a troca."""
    print(f"  {'meta':>10}  {'sacou':>7}  {'perdeu tudo':>12}  "
          f"{'média':>12}  {'apostas':>8}")
    print("  " + "-" * 56)
    meta = META_MINIMA
    while meta <= META_MAXIMA:
        r = lote(js, meta, pessoas, rng)
        print(f"  {formatar_reais(meta):>10}  "
              f"{formatar_pct(r['sacaram'] / pessoas, 0):>7}  "
              f"{formatar_pct(r['quebraram'] / pessoas, 0):>12}  "
              f"{formatar_reais(r['media']):>12}  "
              f"{formatar_numero(r['apostas'], 0):>8}")
        meta += 200.0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--meta", type=float, default=META_PADRAO,
                    help="lucro que o apostador combina consigo mesmo antes de sacar")
    ap.add_argument("--pessoas", type=int, default=PESSOAS_META)
    ap.add_argument("--semente", type=int, default=None)
    ap.add_argument("--ao-vivo", action="store_true")
    ap.add_argument("--rapido", action="store_true",
                    help="menos pessoas na varredura, para uma passada rápida")
    args = ap.parse_args()
    rng = random.Random(args.semente)
    js = jogos(args.ao_vivo)

    print("=" * 64)
    print("EU PARO QUANDO ESTIVER GANHANDO")
    print("=" * 64)
    print(f"{formatar_numero(args.pessoas)} pessoas, cada uma com "
          f"{formatar_reais(BANCA_INICIAL)}, apostando {formatar_reais(APOSTA)} "
          f"por vez.")
    print(f"Cada uma saca e vai embora ao ganhar {formatar_reais(args.meta)}. "
          f"Ninguém deposita de novo.\n")

    r = lote(js, args.meta, args.pessoas, rng)
    n = args.pessoas
    print(f"  bateram a meta e saíram : {formatar_pct(r['sacaram'] / n, 0)}  "
          f"({formatar_numero(r['sacaram'])} pessoas)")
    print(f"  perderam tudo           : {formatar_pct(r['quebraram'] / n, 0)}  "
          f"({formatar_numero(r['quebraram'])} pessoas)")
    print(f"  resultado médio         : {formatar_reais(r['media'])}")
    print(f"  apostas até resolver    : {formatar_numero(r['apostas'], 0)}")
    print()
    histograma(r["resultados"])
    print()

    if r["sacaram"] > n / 2:
        print("A maioria saiu ganhando. E o resultado médio foi negativo.")
        print("As duas coisas são verdade ao mesmo tempo: quem sacou levou")
        print(f"{formatar_reais(args.meta)}, quem quebrou perdeu "
              f"{formatar_reais(BANCA_INICIAL)}.")
    else:
        print(f"{formatar_pct(r['quebraram'] / n, 0)} perderam tudo. "
              "Quanto maior a meta, mais fácil quebrar antes.")
        print("Meta maior quer dizer mais apostas antes de poder sacar, e")
        print("cada aposta a mais é outra fatia para a casa.")
    print()

    print("-" * 64)
    print("A MESMA SIMULAÇÃO EM CADA META")
    print("-" * 64)
    varredura(js, 2_000 if args.rapido else args.pessoas // 2, rng)
    print()
    print("Não existe meta que faça a conta virar. Dá para escolher entre")
    print("ganhar pouco com frequência e ganhar muito raramente. Não dá para")
    print("escolher ganhar.")
    print()


if __name__ == "__main__":
    main()
