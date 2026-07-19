"""Para onde vão R$ 100 apostados?

"Mas é legal e regulamentado" costuma encerrar a conversa. Regulamentado
significa que o Estado cobra imposto sobre o que a casa retém, não que a
casa retenha menos. Este script segue o caminho do dinheiro.
"""

import argparse

from .config import (ALIQUOTA_GGR_2026, RETORNO_BC, RETORNO_SPA,
                     formatar_pct, formatar_reais)

# Lei 14.790/2023 na redação original e as alíquotas da LC 224/2025.
ALIQUOTAS = [(2024, 0.12), (2026, 0.13), (2027, 0.14), (2028, 0.15)]


def repartir(valor: float, retorno: float, ggr: float) -> dict:
    premio = valor * retorno
    retido = valor - premio            # é o GGR, a receita bruta da casa
    estado = retido * ggr
    casa = retido - estado
    return {"premio": premio, "retido": retido, "estado": estado, "casa": casa}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--valor", type=float, default=100.0)
    args = ap.parse_args()
    v = args.valor

    print("=" * 64)
    print(f"PARA ONDE VÃO {formatar_reais(v)} APOSTADOS")
    print("=" * 64)
    print("As duas estimativas oficiais de retorno ao apostador discordam.")
    print("Em vez de escolher a mais conveniente, aqui estão as duas.\n")

    for nome, retorno in (("Banco Central", RETORNO_BC),
                          ("SPA / Fazenda", RETORNO_SPA)):
        d = repartir(v, retorno, ALIQUOTA_GGR_2026)
        print(f"  {nome}  (retorno de {formatar_pct(retorno, 0)})")
        print(f"    volta como prêmio  {formatar_reais(d['premio'], 2):>10}   "
              f"{'▓' * round(d['premio'] / v * 40)}")
        print(f"    fica com a casa    {formatar_reais(d['casa'], 2):>10}   "
              f"{'▒' * max(1, round(d['casa'] / v * 40))}")
        print(f"    vai para o Estado  {formatar_reais(d['estado'], 2):>10}   "
              f"{'░' * max(1, round(d['estado'] / v * 40))}")
        print()

    print(f"Alíquota do GGR ao longo do tempo (sobre o retido, "
          f"retorno de {formatar_pct(RETORNO_BC, 0)}):")
    print(f"  {'ano':>9} {'alíquota':>10} {'Estado':>12} {'casa':>12}")
    print("  " + "-" * 45)
    for ano, aliq in ALIQUOTAS:
        d = repartir(v, RETORNO_BC, aliq)
        rot = "original" if ano == 2024 else str(ano)
        print(f"  {rot:>9} {formatar_pct(aliq, 0):>10} "
              f"{formatar_reais(d['estado'], 2):>12} "
              f"{formatar_reais(d['casa'], 2):>12}")
    print()
    print("Repare no que a regulamentação muda e no que ela não muda.")
    print("A fatia do Estado cresce. A fatia que sai do apostador, não:")
    print("ela é definida pela cotação, e a cotação foi decidida antes.")
    print()
    print("O prêmio que 'volta' também não sai do jogo. Ele volta para a")
    print("mesma conta, dentro do mesmo aplicativo, e costuma ser reapostado.")
    print("Cada volta pela mesa cobra a margem de novo.")
    print()
    print("Simplificado: não inclui o imposto de renda sobre prêmios nem os")
    print("tributos gerais da empresa.")
    print()


if __name__ == "__main__":
    main()
