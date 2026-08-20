Sim, **é totalmente possível** — e esse PDF já tem uma estrutura muito boa para transformar em uma pequena base de dados para um dashboard de ganhos da Uber.

Eu faria a modelagem pensando desde o início em **Power BI**, principalmente porque você já está trabalhando com ETL, PostgreSQL e Star Schema nos seus outros projetos.

O relatório cobre **10/08/2026 04:00 a 17/08/2026 04:00**. 

### Eu criaria 3 tabelas

#### 1. `ft_transacoes` — principal

Essa seria a tabela mais importante do projeto.

A partir da seção **Transações**, temos, por exemplo:

| data       | hora  | tipo   | categoria | valor |
| ---------- | ----- | ------ | --------- | ----: |
| 14/08/2026 | 22:09 | Viagem | Uber X    | 34,51 |
| 14/08/2026 | 21:12 | Viagem | Uber X    |  6,99 |
| 14/08/2026 | 20:59 | Viagem | Uber X    |  7,19 |
| 14/08/2026 | 20:49 | Viagem | Uber X    |  8,30 |
| 14/08/2026 | 20:39 | Viagem | Uber X    |  8,17 |
| 14/08/2026 | 20:29 | Viagem | Uber X    | 11,66 |
| 14/08/2026 | 20:09 | Viagem | Uber X    |  6,99 |
| 14/08/2026 | 19:56 | Viagem | Uber X    |  7,40 |
| 14/08/2026 | 19:44 | Viagem | Uber X    |  7,10 |
| 11/08/2026 | 15:18 | Viagem | Uber X    |  6,99 |
| ...        | ...   | ...    | ...       |   ... |

Essas transações estão detalhadas nas páginas 3 e 4 do relatório.  

Eu acrescentaria também:

```text
id_transacao
data
hora
tipo_transacao
produto
valor
saldo_apos_transacao
```

Assim podemos calcular:

* ganhos por dia;
* ganhos por hora;
* quantidade de viagens;
* ticket médio;
* ganhos por produto;
* evolução dos ganhos;
* melhores dias;
* melhores horários.

---

### 2. `ft_resumo_ganhos`

O próprio relatório traz um resumo semanal:

| indicador      |     valor |
| -------------- | --------: |
| Saldo inicial  | R$ 362,80 |
| Seus ganhos    | R$ 188,96 |
| Transferências | R$ 362,80 |
| Saldo final    | R$ 188,96 |

Esses valores estão no resumo semanal. 

E temos ainda o detalhamento dos ganhos:

| componente                 |         valor |
| -------------------------- | ------------: |
| Base                       |     R$ 170,04 |
| Preço dinâmico             |      R$ 15,00 |
| Tempo na parada            |       R$ 1,61 |
| UberX Prioridade           |       R$ 1,90 |
| Tempo de espera na partida |       R$ 0,41 |
| **Total**                  | **R$ 188,96** |



Isso daria uma segunda visão muito interessante no dashboard.

---

### 3. `dm_produto`

Como você está fazendo Star Schema nos seus projetos, eu criaria também uma dimensão simples:

| id_produto | produto    |
| ---------: | ---------- |
|          1 | Uber X     |
|          2 | Prioridade |

No relatório aparecem **Uber X** e **Prioridade** como tipos de viagem/transação.  

---

# E o dashboard poderia ficar muito legal

Eu imaginaria algo assim:

```text
┌──────────────────────────────────────────────────────────────┐
│                 UBER EARNINGS ANALYTICS                      │
│                10/08/2026 → 17/08/2026                      │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ GANHOS       │ VIAGENS      │ TICKET MÉDIO │ GANHO/HORA     │
│ R$ 188,96    │     16       │    R$ xx     │    R$ xx       │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                                                              │
│              EVOLUÇÃO DOS GANHOS POR DIA                    │
│                                                              │
├─────────────────────────────┬────────────────────────────────┤
│ GANHOS POR HORÁRIO          │ PRODUTOS                       │
│                             │                                │
│ 14h ███████████             │ Uber X       R$ xxx            │
│ 15h ███████                 │ Prioridade   R$ xxx            │
│ 20h ███████████████         │                                │
│ 21h █████████████████       │                                │
├─────────────────────────────┴────────────────────────────────┤
│                                                              │
│                    TRANSAÇÕES                                │
│ Data | Hora | Produto | Valor | Saldo                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

E tem uma coisa especialmente interessante: **a seção Transações permite reconstruir a sequência do saldo**, porque o relatório mostra o valor da transação e o saldo após cada evento. Por exemplo, após uma corrida de R$ 34,51, o saldo passa para R$ 188,96. 

## Minha sugestão

Como esse é um projeto novo, eu **não começaria pelo Power BI**.

Faria:

**PDF → Python → DataFrames → PostgreSQL → Power BI**

E podemos construir um ETL que aceite **cada novo PDF semanal**, extraia as transações e faça `append` na tabela:

```text
ft_transacoes
```

Assim, daqui a alguns meses você terá um histórico completo e poderá responder perguntas muito mais interessantes:

> **Quanto eu ganho por hora dirigindo?**

> **Qual dia da semana é mais rentável?**

> **Qual horário tem maior ganho médio por viagem?**

> **Uber X ou Prioridade gera maior receita?**

> **Meu ganho por viagem está aumentando ou diminuindo?**

> **Quanto ganho por R$ 1 de tempo online?**

E aí temos um projeto de **Analytics pessoal de verdade**, não apenas um dashboard do extrato semanal.

Se quiser, o próximo passo pode ser justamente **eu montar a estrutura da `ft_transacoes` e extrair as 15 transações desse PDF para uma tabela pronta para importar no PostgreSQL**.

Sim. E encontrei um detalhe importante no PDF: **não são 15 transações de viagens, mas 16**. São 9 viagens em 14/08 e 7 em 11/08. Além disso, existe uma transação separada de transferência bancária de R$ 362,80, que eu **não colocaria na `ft_transacoes` de viagens**.  

Eu estruturaria a fato pensando já no futuro dashboard.

## 1. Estrutura da `ft_transacoes`

Sugiro:

```sql
CREATE TABLE IF NOT EXISTS ft_transacoes (
    id_transacao BIGSERIAL PRIMARY KEY,
    data_transacao DATE NOT NULL,
    hora_transacao TIME NOT NULL,
    data_viagem DATE,
    hora_viagem TIME,
    produto VARCHAR(30) NOT NULL,
    valor NUMERIC(10,2) NOT NULL,
    saldo_apos_transacao NUMERIC(10,2)
);
```

### Por que duas datas/horários?

O relatório apresenta dois horários:

```text
22:09
14 de ago. 21:38
```

Ou seja, temos o horário da transação/processamento e o horário associado à viagem. Vou preservar os dois, em vez de assumir que são a mesma coisa. 

Isso será útil posteriormente para analisar, por exemplo:

* horário em que a corrida aconteceu;
* tempo entre a viagem e o processamento;
* ganhos por hora.

---

# 2. Dados extraídos do PDF

As 16 viagens são:

| Data       | Hora transação | Hora viagem | Produto    | Valor |  Saldo |
| ---------- | -------------: | ----------: | ---------- | ----: | -----: |
| 14/08/2026 |          22:09 |       21:38 | Uber X     | 34,51 | 188,96 |
| 14/08/2026 |          21:12 |       21:04 | Uber X     |  6,99 | 154,45 |
| 14/08/2026 |          20:59 |       20:45 | Uber X     |  7,19 | 147,46 |
| 14/08/2026 |          20:49 |       20:36 | Uber X     |  8,30 | 140,27 |
| 14/08/2026 |          20:39 |       20:29 | Uber X     |  8,17 | 131,97 |
| 14/08/2026 |          20:29 |       20:12 | Uber X     | 11,66 | 123,80 |
| 14/08/2026 |          20:09 |       19:50 | Uber X     |  6,99 | 112,14 |
| 14/08/2026 |          19:56 |       19:42 | Uber X     |  7,40 | 105,15 |
| 14/08/2026 |          19:44 |       19:35 | Uber X     |  7,10 |  97,75 |
| 11/08/2026 |          15:18 |       14:58 | Uber X     |  6,99 |  90,65 |
| 11/08/2026 |          15:07 |       14:48 | Uber X     |  9,94 |  83,66 |
| 11/08/2026 |          14:51 |       14:31 | Uber X     |  6,99 |  73,72 |
| 11/08/2026 |          14:38 |       14:25 | Uber X     |  7,24 |  66,73 |
| 11/08/2026 |          14:24 |       14:05 | Prioridade | 11,45 |  59,49 |
| 11/08/2026 |          14:09 |       13:53 | Uber X     | 12,06 |  48,04 |
| 10/08/2026 |          08:03 |       07:21 | Uber X     | 35,98 |  35,98 |

Os valores e saldos acima são os apresentados na seção **Transações** do relatório.  

---

# 3. INSERT para PostgreSQL

Você pode executar diretamente no Aiven:

```sql
INSERT INTO ft_transacoes (
    data_transacao,
    hora_transacao,
    data_viagem,
    hora_viagem,
    produto,
    valor,
    saldo_apos_transacao
)
VALUES
    ('2026-08-14', '22:09', '2026-08-14', '21:38', 'Uber X', 34.51, 188.96),
    ('2026-08-14', '21:12', '2026-08-14', '21:04', 'Uber X', 6.99, 154.45),
    ('2026-08-14', '20:59', '2026-08-14', '20:45', 'Uber X', 7.19, 147.46),
    ('2026-08-14', '20:49', '2026-08-14', '20:36', 'Uber X', 8.30, 140.27),
    ('2026-08-14', '20:39', '2026-08-14', '20:29', 'Uber X', 8.17, 131.97),
    ('2026-08-14', '20:29', '2026-08-14', '20:12', 'Uber X', 11.66, 123.80),
    ('2026-08-14', '20:09', '2026-08-14', '19:50', 'Uber X', 6.99, 112.14),
    ('2026-08-14', '19:56', '2026-08-14', '19:42', 'Uber X', 7.40, 105.15),
    ('2026-08-14', '19:44', '2026-08-14', '19:35', 'Uber X', 7.10, 97.75),

    ('2026-08-11', '15:18', '2026-08-11', '14:58', 'Uber X', 6.99, 90.65),
    ('2026-08-11', '15:07', '2026-08-11', '14:48', 'Uber X', 9.94, 83.66),
    ('2026-08-11', '14:51', '2026-08-11', '14:31', 'Uber X', 6.99, 73.72),
    ('2026-08-11', '14:38', '2026-08-11', '14:25', 'Uber X', 7.24, 66.73),
    ('2026-08-11', '14:24', '2026-08-11', '14:05', 'Prioridade', 11.45, 59.49),
    ('2026-08-11', '14:09', '2026-08-11', '13:53', 'Uber X', 12.06, 48.04),

    ('2026-08-10', '08:03', '2026-08-10', '07:21', 'Uber X', 35.98, 35.98);
```

---

# 4. Validação importantíssima

Antes de levar para o Power BI, execute:

```sql
SELECT
    COUNT(*) AS quantidade_transacoes,
    SUM(valor) AS total_ganhos
FROM ft_transacoes;
```

O resultado deve ser:

```text
quantidade_transacoes = 16
total_ganhos          = R$ 188,96
```

Isso bate exatamente com o **"Seus ganhos R$ 188,96"** apresentado no resumo e no detalhamento do relatório.  

### E temos uma validação ainda melhor

A soma das viagens por dia deve resultar em:

| Data      |        Ganhos |
| --------- | ------------: |
| 10/08     |      R$ 35,98 |
| 11/08     |      R$ 55,17 |
| 14/08     |      R$ 97,81 |
| **Total** | **R$ 188,96** |

Isso nos dá uma ótima primeira camada de **data quality** para o projeto.

---

## 5. Uma melhoria que eu faria agora

Como você quer transformar isso em um **dashboard de ganhos como motorista**, eu não pararia na `ft_transacoes`.

Eu criaria:

```text
dm_calendario
dm_produto
        │
        ▼
ft_transacoes
```

E futuramente podemos adicionar uma `ft_resumo_ganhos`.

Aí seu projeto começa a ficar com uma arquitetura muito parecida com a que você está usando na ANATEL:

```text
                 dm_calendario
                       │
                       │
dm_produto ─────── ft_transacoes
                       │
                       │
                dm_tipo_evento
```

E a partir daí podemos construir métricas como **ganho por viagem, ganho por hora, ticket médio, melhor horário, melhor dia, participação do Uber X/Prioridade e evolução semanal/mensal**.

Sim. Como você já tem o **LOAD para o Aiven**, eu deixaria esse ETL bem enxuto, seguindo exatamente a separação:

```text
PDF
 ↓
extract.py
 ↓
transform.py
 ↓
load.py
 ↓
Aiven
```

Para esse primeiro PDF, a extração precisa lidar com a estrutura da seção **Transações**, que contém data/hora da transação, produto, data/hora da viagem, valor e saldo. 

## 1. `extract.py`

Eu usaria `pdfplumber`, que é simples e adequado para esse PDF.

```python
import pdfplumber
import pandas as pd


def extract_transacoes(pdf_path: str) -> pd.DataFrame:
    transacoes = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            texto = page.extract_text()

            if not texto or "Transações" not in texto:
                continue

            linhas = texto.splitlines()

            for i, linha in enumerate(linhas):

                # Identifica linhas que começam com a data da transação
                if linha.startswith(("seg.,", "ter.,", "qua.,", "qui.,", "sex.", "sáb.", "dom.")):

                    # Aqui a transformação será feita posteriormente
                    transacoes.append({
                        "linha": linha
                    })

    return pd.DataFrame(transacoes)
```

Mas, para **esse PDF específico**, eu faria uma extração um pouco mais direcionada, porque o texto está quebrado em várias linhas.

---

# 2. `extract.py` — versão que eu realmente usaria

```python
import pdfplumber
import pandas as pd
import re


def extract_transacoes(pdf_path: str) -> pd.DataFrame:

    registros = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            texto = page.extract_text()

            if not texto or "Transações" not in texto:
                continue

            linhas = texto.splitlines()

            i = 0

            while i < len(linhas):

                linha = linhas[i]

                # Identifica início de uma transação
                if re.match(
                    r"^(seg\.|ter\.|qua\.|qui\.|sex\.|sáb\.|dom\.)",
                    linha
                ):

                    data_transacao = linha
                    hora_transacao = linhas[i + 1]

                    produto = linhas[i + 2]

                    data_viagem = linhas[i + 3]
                    hora_viagem = linhas[i + 4]

                    valor = linhas[i + 5]
                    saldo = linhas[i + 6]

                    registros.append({
                        "data_transacao": data_transacao,
                        "hora_transacao": hora_transacao,
                        "produto": produto,
                        "data_viagem": data_viagem,
                        "hora_viagem": hora_viagem,
                        "valor": valor,
                        "saldo": saldo
                    })

                    i += 7

                else:
                    i += 1

    return pd.DataFrame(registros)
```

Essa função é responsável **somente pela extração**. Não vamos colocar regras de negócio aqui.

---

# 3. `transform.py`

Aqui fazemos a limpeza e transformação.

```python
import pandas as pd


MESES = {
    "jan.": "01",
    "fev.": "02",
    "mar.": "03",
    "abr.": "04",
    "mai.": "05",
    "jun.": "06",
    "jul.": "07",
    "ago.": "08",
    "set.": "09",
    "out.": "10",
    "nov.": "11",
    "dez.": "12",
}


def transformar_transacoes(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # ---------------------------------------------------------
    # Data da transação
    # ---------------------------------------------------------

    df["data_transacao"] = (
        df["data_transacao"]
        .str.replace("seg., ", "", regex=False)
        .str.replace("ter., ", "", regex=False)
        .str.replace("qua., ", "", regex=False)
        .str.replace("qui., ", "", regex=False)
        .str.replace("sex., ", "", regex=False)
        .str.replace("sáb., ", "", regex=False)
        .str.replace("dom., ", "", regex=False)
    )

    df["data_transacao"] = pd.to_datetime(
        df["data_transacao"],
        format="%d de %b. de %Y"
    )

    # ---------------------------------------------------------
    # Data da viagem
    # ---------------------------------------------------------

    df["data_viagem"] = pd.to_datetime(
        df["data_viagem"],
        format="%d de %b."
    ).apply(
        lambda x: x.replace(year=2026)
    )

    # ---------------------------------------------------------
    # Valores monetários
    # ---------------------------------------------------------

    for coluna in ["valor", "saldo"]:

        df[coluna] = (
            df[coluna]
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.replace("-", "", regex=False)
            .astype(float)
        )

    # ---------------------------------------------------------
    # Tipos
    # ---------------------------------------------------------

    df["hora_transacao"] = pd.to_datetime(
        df["hora_transacao"],
        format="%H:%M"
    ).dt.time

    df["hora_viagem"] = pd.to_datetime(
        df["hora_viagem"],
        format="%H:%M"
    ).dt.time

    # ---------------------------------------------------------
    # Renomear
    # ---------------------------------------------------------

    df = df.rename(
        columns={
            "saldo": "saldo_apos_transacao"
        }
    )

    return df
```

### Porém, eu faria uma alteração importante

Como esse ETL vai ser usado **toda semana**, não devemos colocar:

```python
year=2026
```

fixo.

O ideal é extrair o ano do cabeçalho do relatório:

```text
10 de ago. de 2026 4h - 17 de ago. de 2026 4h
```

Assim o ETL continuará funcionando em 2027, 2028 etc.

Podemos fazer isso na próxima versão.

---

# 4. `load.py`

Como você já tem seu LOAD funcionando para o Aiven, **não precisamos reinventar essa parte**.

Seu `main.py` poderia simplesmente orquestrar:

```python
from extract import extract_transacoes
from transform import transformar_transacoes
from load import load_transacoes


PDF_PATH = "data/relatorio_17_de_ago.pdf"


def main():

    # EXTRACT
    df = extract_transacoes(PDF_PATH)

    print(f"Transações extraídas: {len(df)}")

    # TRANSFORM
    df = transformar_transacoes(df)

    print(df.info())

    # LOAD
    load_transacoes(df)


if __name__ == "__main__":
    main()
```

---

# 5. Estrutura do projeto

Eu deixaria assim:

```text
uber-earnings-dashboard/
│
├── data/
│   └── relatorio_17_de_ago.pdf
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
│
├── requirements.txt
│
└── README.md
```

E o fluxo fica:

```text
                 PDF Uber
                    │
                    ▼
              ┌───────────┐
              │  extract  │
              └─────┬─────┘
                    │
                    ▼
                DataFrame
                    │
                    ▼
              ┌───────────┐
              │ transform │
              └─────┬─────┘
                    │
                    ▼
             DataFrame tratado
                    │
                    ▼
              ┌───────────┐
              │   load    │
              └─────┬─────┘
                    │
                    ▼
             PostgreSQL Aiven
                    │
                    ▼
                 Power BI
```

### Uma melhoria que eu considero essencial

Como você pretende usar isso **semanalmente**, eu faria o ETL aceitar simplesmente:

```bash
python main.py data/relatorio_24_de_ago.pdf
```

e o próprio `extract.py` descobrir:

* período do relatório;
* ano;
* datas;
* quantidade de transações;
* produtos;
* valores.

Assim você não precisará alterar o código toda semana.

E eu também colocaria uma validação no `transform.py`:

```python
assert round(df["valor"].sum(), 2) == 188.96
```

**mas somente como validação temporária deste PDF**. O ideal é comparar o total extraído com o `Seus ganhos` do resumo do próprio PDF, para que o ETL detecte automaticamente se alguma transação não foi extraída. O relatório informa `Seus ganhos = R$ 188,96`. 

Isso deixaria o projeto muito mais robusto: **se a Uber mudar o layout do PDF e o extractor perder uma transação, o pipeline falha em vez de gravar silenciosamente um valor errado no Aiven.**
