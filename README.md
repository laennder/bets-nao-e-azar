# Não é azar: o código das simulações

Código-fonte das simulações da página **[Não é azar](https://naoeazar.com.br)**, uma peça de conscientização sobre apostas.

A página faz uma afirmação forte: **no longo prazo o apostador perde, e isso é matemática, não opinião.** Este repositório existe para você não precisar acreditar na palavra de ninguém. Rode o código, mude os parâmetros, refaça as contas.

Se você encontrar um erro, [abra uma issue](../../issues). Erro encontrado é erro corrigido.

## Como rodar

Necessário Python 3.8 ou superior, só biblioteca padrão.

```bash
git clone https://github.com/laennder/bets-nao-e-azar.git
cd bets-nao-e-azar
python3 rodar_tudo.py
```

Três opções úteis:

```bash
python3 rodar_tudo.py --semente 7    # sorteio fixo, resultado reproduzível
python3 rodar_tudo.py --rapido       # menos repetições, passada rápida
python3 rodar_tudo.py --ao-vivo      # busca as cotações da rodada de agora
```

Ou rode uma simulação isolada:

```bash
python3 -m simulacoes.martingale
python3 -m simulacoes.monte_carlo --pessoas 50000 --semente 1
python3 -m simulacoes.meta_de_saque --meta 500
```

## As cotações são reais

A página não usa números inventados. Um coletor pega as cotações de jogos do **Brasileirão Série A** em dezenas de casas de aposta e publica a **mediana** de cada mercado, de seis em seis horas. Nenhuma casa é nomeada: o alvo é o mecanismo, não uma marca.

Um retrato dessa coleta está versionado em [`dados/odds.json`](dados/odds.json), então o repositório roda offline e o resultado é reproduzível. Com `--ao-vivo`, os scripts leem exatamente os mesmos arquivos que a página consome.

O mesmo vale para a taxa de juros usada no comparativo: [`dados/tesouro.json`](dados/tesouro.json) traz um título Prefixado real, com data-base, colhido do Tesouro Transparente.

## O que cada simulação responde

| Arquivo | Pergunta |
|---|---|
| [`margem.py`](simulacoes/margem.py) | Onde está a vantagem da casa numa cotação que parece justa? |
| [`longo_prazo.py`](simulacoes/longo_prazo.py) | O que acontece com o saldo conforme o número de apostas cresce? |
| [`monte_carlo.py`](simulacoes/monte_carlo.py) | De 10.000 apostadores, quantos terminam no lucro? |
| [`martingale.py`](simulacoes/martingale.py) | A estratégia de dobrar a aposta funciona? |
| [`meta_de_saque.py`](simulacoes/meta_de_saque.py) | E se o apostador combinar de sacar quando ganhar um tanto? |
| [`quase_ganho.py`](simulacoes/quase_ganho.py) | Por que "faltou pouco" acontece tanto? |
| [`caminho_do_dinheiro.py`](simulacoes/caminho_do_dinheiro.py) | Para onde vão R$ 100 apostados? |
| [`calculadora.py`](simulacoes/calculadora.py) | Quanto custa apostar todo mês por dez anos? |

O motor comum está em [`aposta.py`](simulacoes/aposta.py), e vale ler primeiro: é lá que a vantagem da casa fica explícita.

## A matemática, em resumo

### Você é sorteado por uma probabilidade e pago por outra

Vitória do mandante, empate ou vitória do visitante cobrem tudo que pode acontecer num jogo. Não existe um quarto resultado. Logo, as três probabilidades teriam que somar exatamente 100%.

Pegue um jogo real do arquivo de dados, Atlético Mineiro x Bahia:

| resultado | cotação | probabilidade implícita (1 ÷ cotação) |
|---|---|---|
| Atlético Mineiro | 2,09 | 47,85% |
| Empate | 3,30 | 30,30% |
| Bahia | 3,46 | 28,90% |
| **soma** | | **107,05%** |

Não existe evento com 107,05% de chance de acontecer. Esses **7,05 pontos percentuais** excedentes são a margem, cobrada antes de a bola rolar.

Normalizando as três para somar 100%, chega-se à probabilidade **real**. A simulação sorteia o resultado por ela e paga o apostador pela **cotação**. A diferença entre as duas é o negócio inteiro.

### Não existe escolha melhor, só a margem

Num livro normalizado proporcionalmente, o valor esperado é **idêntico** nos três resultados. Com margem `m`, cada real apostado devolve `1 / (1 + m)`, então a perda esperada é:

```
perda por real = m / (1 + m)
```

Na coleta versionada aqui, a margem média dos 19 jogos é de **8,06%**, o que dá **7,46% de perda esperada** a cada real apostado. Apostar no favorito, no azarão ou no empate não muda esse número. Só a margem muda.

### A Lei dos Grandes Números faz o resto

A perda esperada cresce **linearmente** com o número de apostas (`n × EV`), enquanto o desvio-padrão cresce com a **raiz** de `n`. A razão entre os dois diverge: a sorte é diluída, a margem não.

Formalmente, pela lei forte dos grandes números, a fortuna acumulada `R_n ≈ n · E(Δ)` tende a menos infinito com probabilidade 1 sempre que `E(Δ) < 0`.

### E a ruína do apostador fecha a porta

Com banca finita contra um adversário de banca praticamente infinita, e valor esperado negativo, a probabilidade de ruína tende a 1. O problema clássico é de Huygens, 1657. Não é uma descoberta recente nem uma opinião sobre apostas.

### Uma regra de saída não salva, e a meta não é um dial

É a objeção mais razoável contra as outras simulações: nelas ninguém tem
regra de saída, então quebrar vira questão de tempo. Com regra, o retrato
muda de forma, não de sinal.

Com meta pequena, a **maioria** realmente bate a meta e sai ganhando, e o
resultado médio continua negativo. Não há contradição, há assimetria de
magnitude: quem saca leva a meta, que é pouco; quem quebra perde a banca
inteira, que é muito. Mais gente ganhando pouco não compensa menos gente
perdendo tudo.

Subir a meta também não resolve, porque troca uma coisa pela outra. Meta
maior exige mais apostas antes de poder sacar, e cada aposta a mais é
outra fatia para a casa: a chance de quebrar no caminho cresce mais rápido
que o prêmio no fim dele. Rodando a mesma simulação em cada meta, a
proporção de quem saca cai de cerca de 68% para 14% e a média afunda,
sem cruzar o zero em ponto nenhum.

O desenho da distribuição diz o mesmo: são duas populações, não uma. Um
bloco em -R$ 1.000, um vazio, e uma faixa que começa na meta. Quase
ninguém termina morno.

### Duas regras que mudam o retrato

A maioria das simulações de aposta ignora as duas, e por isso subestima o estrago:

- **Não dá para apostar o que não se tem.** Com menos que o valor cheio na conta, a simulação aposta o troco.
- **Zerou, deposita de novo.** É o que a pessoa real faz, e é disso que a casa depende. Por isso o saldo na tela quase sempre parece administrável enquanto o total depositado só cresce. As duas colunas contam histórias diferentes, e o aplicativo só mostra uma.

## Fontes dos números que não são simulados

- **Banco Central**, Estudo Especial 119/2024: volume via Pix, número de apostadores, retenção média das casas, beneficiários do Bolsa Família.
- **Tesouro Nacional**, [Tesouro Transparente](https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto): taxa dos títulos ofertados.
- **Lei 14.790/2023** e **Lei Complementar 224/2025**: regulamentação e alíquota sobre a receita bruta das casas.

A lista completa, com avaliação de cada fonte, está no rodapé da [página](https://naoeazar.com.br).

## Se apostar virou um problema

**CVV · Centro de Valorização da Vida**: Disque 188, ligação gratuita, 24 horas por dia.

## Licença

MIT. Use, copie, adapte, traduza. Se isso ajudar alguém a fazer a conta antes de apostar, cumpriu a função.
