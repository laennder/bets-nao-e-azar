"""Quanto custa apostar todo mês por dez anos?

Duas contas simples, lado a lado. A da esquerda é o que sai da conta e não
volta. A da direita é o que o mesmo dinheiro faria rendendo à taxa real de
um título público, sem promessa nenhuma de rentabilidade extraordinária.

A taxa vem do Tesouro Transparente e tem data. Não é um "10% ao ano"
escolhido para o argumento ficar bonito.
"""

import argparse

from .config import formatar_numero, formatar_pct, formatar_reais
from .dados import carregar_tesouro


def valor_futuro(mensal: float, taxa_anual: float, meses: int) -> float:
    """Aportes mensais iguais, juro composto. Série de pagamentos."""
    i = (1 + taxa_anual) ** (1 / 12) - 1
    return mensal * (((1 + i) ** meses - 1) / i)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--valores", type=float, nargs="+",
                    default=[50, 100, 200, 300, 500, 1000])
    ap.add_argument("--ao-vivo", action="store_true")
    args = ap.parse_args()
    t = carregar_tesouro(args.ao_vivo)

    print("=" * 64)
    print("A CONTA DE DEZ ANOS")
    print("=" * 64)
    base = "/".join(reversed(t["data_base"].split("-")))
    print(f"Referência: {t['titulo']}, "
          f"{formatar_numero(t['taxa_pct'], 2)}% ao ano,")
    print(f"posição de {base}, {t['fonte']}.\n")

    print(f"  {'por mês':>10} {'em 1 ano':>13} {'em 5 anos':>14} "
          f"{'em 10 anos':>14} {'guardado':>15}")
    print("  " + "-" * 68)
    for v in args.valores:
        fv = valor_futuro(v, t["taxa_anual"], 120)
        print(f"  {formatar_reais(v):>10} {formatar_reais(v * 12):>13} "
              f"{formatar_reais(v * 60):>14} {formatar_reais(v * 120):>14} "
              f"{formatar_reais(fv):>15}")
    print()

    v = 100.0
    fv = valor_futuro(v, t["taxa_anual"], 120)
    print(f"  {formatar_reais(v)} por mês são {formatar_reais(v * 120)} em dez anos.")
    print(f"  Guardados, seriam {formatar_reais(fv)}: "
          f"{formatar_pct(fv / (v * 120) - 1)} a mais, sem apostar em nada.")
    print()
    print("A conta assume que o dinheiro depositado não volta, que é o destino")
    print("estatístico da esmagadora maioria dos apostadores no longo prazo.")
    print("Não é uma recomendação de investimento: é a régua mais conservadora")
    print("que existe, usada só para dar tamanho ao que está sendo perdido.")
    print()


if __name__ == "__main__":
    main()
