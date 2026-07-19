"""O motor: uma aposta num jogo real, com o sorteio feito direito.

É a peça central do repositório, e o ponto onde a vantagem da casa
aparece de forma explícita:

  1. Cada cotação vira uma probabilidade implícita (1 / cotação).
  2. A soma das três passa de 100%. O excedente é a margem.
  3. Normalizando para 100%, chega-se à probabilidade REAL.
  4. O resultado é SORTEADO pela probabilidade real.
  5. O apostador é PAGO pela cotação da casa.

Você é sorteado por uma probabilidade e pago por outra. A diferença entre
as duas é o negócio.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from .dados import RESULTADOS


def sortear_resultado(jogo: dict, rng: random.Random) -> str:
    """Sorteia casa/empate/visitante pela probabilidade REAL do jogo."""
    r = rng.random()
    acumulado = 0.0
    for k in RESULTADOS:
        acumulado += jogo["real"][k]
        if r < acumulado:
            return k
    return RESULTADOS[-1]


def apostar(jogo: dict, escolha: str, valor: float,
            rng: random.Random) -> Tuple[float, str]:
    """Devolve (ganho ou perda, resultado que saiu)."""
    saiu = sortear_resultado(jogo, rng)
    if saiu == escolha:
        return valor * (jogo["odds"][escolha] - 1.0), saiu
    return -valor, saiu


def aposta_aleatoria(jogos: List[dict], valor: float,
                     rng: random.Random) -> float:
    """Aposta em um jogo sorteado da rodada, num resultado sorteado.

    Qual resultado se escolhe não muda o valor esperado (ver dados.py),
    então sortear é tão bom quanto qualquer critério.
    """
    jogo = jogos[rng.randrange(len(jogos))]
    escolha = RESULTADOS[rng.randrange(3)]
    ganho, _ = apostar(jogo, escolha, valor, rng)
    return ganho


def sessao(jogos: List[dict], n_apostas: int, banca: float, aposta: float,
           aporte: float, rng: random.Random) -> Dict:
    """Uma pessoa apostando n vezes, depositando de novo quando zera.

    Duas regras que a maioria das simulações ignora e que mudam o retrato:

    - Não dá para apostar o que não se tem. Com menos que o valor cheio na
      conta, aposta-se o que sobrou.
    - Zerou, deposita de novo. É o que a pessoa real faz, e é disso que a
      casa depende. Por isso o saldo na tela quase sempre parece
      administrável enquanto o total depositado só cresce.
    """
    depositado = banca
    # Começa em 1: a banca inicial já é um depósito. Contar só as recargas
    # faz quem nunca zerou aparecer com zero, e dá à mesma palavra dois
    # sentidos em lugares diferentes.
    aportes = 1
    quando: List[int] = [0]     # o depósito inicial acontece na aposta 0
    trajetoria = [0.0]                       # prejuízo acumulado

    for i in range(n_apostas):
        if banca < 0.01:
            banca += aporte
            depositado += aporte
            aportes += 1
            quando.append(i)
        banca += aposta_aleatoria(jogos, min(aposta, banca), rng)
        if banca < 0.01:
            banca = 0.0
        trajetoria.append(banca - depositado)

    return {
        "banca": banca,
        "depositado": depositado,
        "resultado": banca - depositado,
        "aportes": aportes,
        "quando": quando,
        "trajetoria": trajetoria,
    }
