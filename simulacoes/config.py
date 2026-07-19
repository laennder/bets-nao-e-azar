"""Parâmetros compartilhados, iguais aos usados na página.

https://naoeazar.com.br
"""

APOSTA = 100.0            # valor de cada aposta, em reais
BANCA_INICIAL = 1000.0    # com quanto o apostador começa
DEPOSITO = 1000.0         # quanto ele deposita quando o dinheiro acaba

APOSTADORES = 10_000      # Monte Carlo
APOSTAS_POR_PESSOA = 500

BANCA_MARTINGALE = 10_000.0
APOSTA_BASE_MARTINGALE = 100.0

# Quanto das apostas volta como prêmio. As duas estimativas oficiais
# discordam, e a página mostra as duas em vez de escolher a mais dramática.
RETORNO_BC = 0.85         # Banco Central, Estudo Especial 119/2024
RETORNO_SPA = 0.94        # SPA / Ministério da Fazenda

ALIQUOTA_GGR_2026 = 0.13  # Lei 14.790/2023 com a LC 224/2025


def formatar_numero(valor: float, casas: int = 0) -> str:
    """Padrão brasileiro: milhar com ponto, decimal com vírgula."""
    txt = f"{abs(valor):,.{casas}f}"
    txt = txt.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return ("-" if valor < 0 else "") + txt


def formatar_reais(valor: float, casas: int = 0) -> str:
    return (f"R$ {formatar_numero(valor, casas)}" if valor >= 0
            else f"-R$ {formatar_numero(abs(valor), casas)}")


def formatar_pct(fracao: float, casas: int = 1) -> str:
    return formatar_numero(fracao * 100, casas) + "%"
