"""Onde está a vantagem da casa numa cotação que parece justa.

Casa, empate e visitante cobrem tudo que pode acontecer num jogo: não
existe um quarto resultado. A soma das probabilidades teria que dar
exatamente 100%. O que passa disso é a casa.
"""

import argparse

from .config import APOSTA, formatar_numero, formatar_pct, formatar_reais
from .dados import RESULTADOS, jogos, margem_media, perda_por_real


def implicitas(jogo: dict) -> dict:
    return {k: 1.0 / jogo["odds"][k] for k in RESULTADOS}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ao-vivo", action="store_true")
    args = ap.parse_args()
    js = jogos(args.ao_vivo)
    j = js[0]

    print("=" * 64)
    print("A MARGEM DA CASA")
    print("=" * 64)
    print(f"{j['casa']} x {j['visitante']}\n")

    imp = implicitas(j)
    rot = {"casa": j["casa"], "empate": "Empate", "visitante": j["visitante"]}
    print(f"  {'resultado':<24} {'cotação':>8} {'o que a odd diz':>17} {'chance real':>13}")
    print("  " + "-" * 62)
    for k in RESULTADOS:
        print(f"  {rot[k][:24]:<24} {formatar_numero(j['odds'][k], 2):>8} "
              f"{formatar_pct(imp[k]):>17} {formatar_pct(j['real'][k]):>13}")
    soma = sum(imp.values())
    print("  " + "-" * 62)
    print(f"  {'SOMA':<24} {'':>8} {formatar_pct(soma):>17} {formatar_pct(1.0):>13}")
    print()
    print(f"  Não existe evento com {formatar_pct(soma, 2)} de chance de acontecer.")
    print(f"  Os {formatar_numero(j['margem'] * 100, 2)} pontos que sobram são a casa,")
    print("  cobrados antes de a bola rolar, com você ganhando ou perdendo.")
    print()
    print("  Você é SORTEADO pela chance real e PAGO pela cotação.")
    print("  A diferença entre as duas colunas é o negócio.")
    print()

    m = margem_media(js)
    p = perda_por_real(js)
    print(f"Na rodada inteira ({len(js)} jogos):")
    print(f"  margem média do mercado  : {formatar_pct(m, 2)}")
    print(f"  perda esperada por real  : {formatar_pct(p, 2)}   [m / (1 + m)]")
    print(f"  {('em ' + formatar_reais(APOSTA) + ' apostados'):<25}: "
          f"{formatar_reais(-p * APOSTA, 2)}")
    print()
    print("  Vale para qualquer um dos três resultados. Com o livro")
    print("  normalizado, não existe escolha melhor: só a margem.")
    print()


if __name__ == "__main__":
    main()
