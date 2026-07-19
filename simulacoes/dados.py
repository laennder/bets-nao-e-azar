"""Carrega as cotações e a taxa do Tesouro usadas nas simulações.

Por padrão lê os arquivos em `dados/`, que são um retrato real coletado do
mercado. Assim o repositório roda offline e o resultado é reproduzível.

Com `--ao-vivo`, busca os mesmos arquivos que a página consome, então a
simulação usa as cotações da rodada de agora.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Dict, List

RAIZ = Path(__file__).resolve().parent.parent
LOCAL_ODDS = RAIZ / "dados" / "odds.json"
LOCAL_TESOURO = RAIZ / "dados" / "tesouro.json"

# De onde o --ao-vivo puxa: os mesmos arquivos que a página consome.
SITE = "https://naoeazar.com.br/dados"

RESULTADOS = ("casa", "empate", "visitante")


def _buscar(arquivo: str) -> dict:
    req = urllib.request.Request(
        f"{SITE}/{arquivo}", headers={"User-Agent": "nao-e-azar/2.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def carregar_odds(ao_vivo: bool = False) -> dict:
    if ao_vivo:
        try:
            return _buscar("odds.json")
        except Exception as e:                       # rede caiu: segue com o retrato
            print(f"  (não deu para buscar ao vivo: {e}; usando dados/odds.json)")
    return json.loads(LOCAL_ODDS.read_text(encoding="utf-8"))


def carregar_tesouro(ao_vivo: bool = False) -> dict:
    if ao_vivo:
        try:
            return _buscar("tesouro.json")
        except Exception as e:
            print(f"  (não deu para buscar ao vivo: {e}; usando dados/tesouro.json)")
    return json.loads(LOCAL_TESOURO.read_text(encoding="utf-8"))


def jogos(ao_vivo: bool = False) -> List[dict]:
    return carregar_odds(ao_vivo)["jogos"]


def margem_media(js: List[dict]) -> float:
    """Excedente médio da soma das probabilidades implícitas.

    Se as três cotações de um jogo somam 107,5% de probabilidade implícita,
    a margem é 7,5%. Aqui é a média dessa margem entre os jogos.
    """
    return sum(j["margem"] for j in js) / len(js)


def perda_por_real(js: List[dict]) -> float:
    """Fração de cada real apostado que se perde, em média.

    Com margem m, o retorno esperado é 1/(1+m), logo a perda é m/(1+m).
    Vale para QUALQUER um dos três resultados: num livro normalizado
    proporcionalmente, o valor esperado é o mesmo nos três. Não existe
    escolha melhor, só a margem.
    """
    m = margem_media(js)
    return m / (1 + m)
