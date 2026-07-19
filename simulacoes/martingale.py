"""A estratégia de dobrar a aposta funciona?

O Martingale é a "estratégia infalível" mais antiga que existe: perdeu,
dobra; quando ganhar, recupera tudo e sobra a aposta inicial.

O detalhe é que aqui a simulação é generosa até o limite do absurdo: o
jogo é JUSTO, 50% de chance e pagamento igual, SEM margem da casa. Nem
assim funciona, porque o problema não é a margem, é a banca finita. A
sequência dobra exponencialmente e a sua conta, não.

Numa casa real, com margem, o mesmo acontece mais rápido.
"""

import argparse
import random
from typing import Dict

from .config import (APOSTA_BASE_MARTINGALE, BANCA_MARTINGALE, formatar_numero,
                     formatar_reais)

LIMITE = 50_000
DESISTE = 1_000.0     # abaixo disso a pessoa para em vez de recomeçar


def rodar(banca: float, base: float, rng: random.Random) -> Dict:
    """Martingale com recomeço, que é como a coisa acontece de verdade.

    Quando a dobra seguinte não cabe no caixa, ninguém para com dinheiro
    no bolso: engole o prejuízo e volta à aposta base, um Martingale
    emendado no outro. Só desiste quando a trava o deixa com menos de 10%
    do que tinha.

    Sem essa regra a simulação parava com o apostador às vezes ainda rico,
    só porque a próxima dobra não coube, o que dá um retrato falso: na
    prática ele recomeça e o dinheiro acaba.
    """
    aposta = base
    vitorias = seq = maior_seq = rodadas = recomecos = 0
    maior_aposta = base

    while rodadas < LIMITE:
        if aposta > banca:                # não dá para cobrir a próxima dobra
            recomecos += 1
            if banca < DESISTE:
                break
            aposta, seq = base, 0
            continue
        rodadas += 1
        maior_aposta = max(maior_aposta, aposta)
        if rng.random() < 0.5:
            banca += aposta
            vitorias += 1
            seq = 0
            aposta = base
        else:
            banca -= aposta
            seq += 1
            maior_seq = max(maior_seq, seq)
            aposta *= 2

    return {"banca": banca, "rodadas": rodadas, "vitorias": vitorias,
            "maior_aposta": maior_aposta, "maior_seq": maior_seq,
            "recomecos": recomecos, "sem_saldo": banca < DESISTE,
            "proxima": aposta}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rodadas", type=int, default=200,
                    help="quantas vezes repetir a estratégia inteira")
    ap.add_argument("--semente", type=int, default=None)
    args = ap.parse_args()
    rng = random.Random(args.semente)

    print("=" * 64)
    print("MARTINGALE, NO JOGO MAIS JUSTO POSSÍVEL")
    print("=" * 64)
    print(f"Banca de {formatar_reais(BANCA_MARTINGALE)}, aposta base de "
          f"{formatar_reais(APOSTA_BASE_MARTINGALE)}.")
    print("Moeda honesta: 50% de chance, pagamento igual, sem margem da casa.\n")

    print("A sequência de dobras, para ver o tamanho do buraco:")
    linha = "  "
    for k in range(9):
        v = APOSTA_BASE_MARTINGALE * (2 ** k)
        linha += f"{formatar_reais(v)}"
        linha += " -> " if k < 8 else ""
    print(linha)
    print(f"  Nove derrotas seguidas exigem "
          f"{formatar_reais(APOSTA_BASE_MARTINGALE * (2 ** 9))} na décima aposta.")
    print("  Nove derrotas seguidas acontecem uma vez a cada 512. Não é raro.\n")

    exemplo = rodar(BANCA_MARTINGALE, APOSTA_BASE_MARTINGALE, rng)
    print("Uma execução:")
    print(f"  apostas feitas        : {formatar_numero(exemplo['rodadas'])}")
    print(f"  vitórias              : {formatar_numero(exemplo['vitorias'])}")
    print(f"  vezes que recomeçou   : {exemplo['recomecos']}")
    print(f"  maior sequência ruim  : {exemplo['maior_seq']} derrotas")
    print(f"  maior aposta feita    : {formatar_reais(exemplo['maior_aposta'])}")
    print(f"  saldo final           : {formatar_reais(exemplo['banca'])}\n")

    sem_saldo = 0
    total_rodadas = 0
    total_recomecos = 0
    resultados = []
    for _ in range(args.rodadas):
        r = rodar(BANCA_MARTINGALE, APOSTA_BASE_MARTINGALE, rng)
        sem_saldo += 1 if r["sem_saldo"] else 0
        total_rodadas += r["rodadas"]
        total_recomecos += r["recomecos"]
        resultados.append(r["banca"] - BANCA_MARTINGALE)

    resultados.sort()
    mediana = resultados[len(resultados) // 2]
    media = sum(resultados) / len(resultados)

    print(f"Repetindo a estratégia {formatar_numero(args.rodadas)} vezes:")
    print(f"  acabaram sem saldo        : {sem_saldo} de {args.rodadas}")
    print(f"  recomeços, média          : {formatar_numero(total_recomecos / args.rodadas, 1)}")
    print(f"  apostas até acabar, média : {formatar_numero(total_rodadas / args.rodadas)}")
    print(f"  resultado MEDIANO         : {formatar_reais(mediana)}")
    print(f"  resultado médio           : {formatar_reais(media)}\n")

    print("  Repare na distância entre a mediana e a média. Num jogo justo o")
    print("  valor esperado é zero, e é a média que preserva isso: bastam")
    print("  uma ou duas execuções que emendaram uma sequência absurda de")
    print("  vitórias para puxá-la, às vezes até para o positivo.")
    print("  A mediana diz o que acontece com QUEM JOGA. A média diz o que")
    print("  acontece com a soma de todo mundo, e é a média que aparece nos")
    print("  prints de quem ganhou.\n")
    print("O Martingale funciona muitas vezes seguidas. É isso que o torna")
    print("convincente: você ganha, ganha, ganha, e devolve tudo de uma vez.")
    print("Ele troca muitos ganhos pequenos por uma perda enorme.")
    print()
    print("E ele nunca termina em derrota: termina em impossibilidade. A")
    print("aposta que recuperaria tudo fica maior que o caixa, e aí só resta")
    print("aceitar a perda e recomeçar, que é o que a simulação faz acima.")
    print()


if __name__ == "__main__":
    main()
