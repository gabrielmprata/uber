# Uber Earnings Analytics

Pipeline de dados para extração, tratamento e armazenamento dos ganhos semanais obtidos como motorista da Uber.

O projeto transforma os extratos semanais de ganhos disponibilizados pela Uber em dados estruturados, armazenados em PostgreSQL na nuvem (Aiven) e posteriormente utilizados no Power BI para construção de um dashboard analítico.

---

## 🎯 Objetivo

Criar uma pipeline simples e automatizada para transformar os extratos semanais de ganhos da Uber em uma base histórica de dados.

O projeto tem três etapas principais:

```text
PDF da Uber
    ↓
Extract
    ↓
Transform
    ↓
Load
    ↓
PostgreSQL / Aiven
    ↓
Power BI
````

A principal tabela analítica será:

```text
ft_transacoes
```

Ela armazenará as transações de viagens identificadas nos extratos semanais.

---

## 🏗️ Arquitetura

```text
                    ┌──────────────────┐
                    │    PDF Uber      │
                    │  (arquivo local) │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    extract.py    │
                    │     Extração     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    DataFrame     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   transform.py   │
                    │  Tratamento      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    DataFrame     │
                    │    tratado       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     load.py      │
                    │      Load        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ PostgreSQL Aiven │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Power BI     │
                    └──────────────────┘
```

---

## 🔐 Privacidade dos dados

Os extratos da Uber contêm informações pessoais e financeiras.

Por esse motivo, **os arquivos PDF não fazem parte do repositório GitHub**.

Os PDFs permanecem exclusivamente no computador local e são informados ao ETL no momento da execução.

Exemplo:

```text
C:\Users\Documents\uber\relatorio_17_08_2026.pdf
```

O projeto não deve armazenar PDFs pessoais no GitHub.

O `.gitignore` também bloqueia arquivos PDF:

```gitignore
*.pdf
data/
```

---

## 📁 Estrutura do projeto

```text
uber-earnings-analytics/
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── main.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

### `extract.py`

Responsável exclusivamente pela extração das informações presentes no PDF.

Principais responsabilidades:

* abrir o PDF;
* localizar a seção `Transações`;
* identificar as transações;
* extrair os campos disponíveis;
* retornar um DataFrame pandas.

---

### `transform.py`

Responsável pelo tratamento dos dados extraídos.

Principais responsabilidades:

* converter datas;
* converter horários;
* transformar valores monetários;
* padronizar nomes das colunas;
* ajustar tipos de dados;
* realizar validações da extração.

---

### `load.py`

Responsável por carregar os dados tratados no PostgreSQL hospedado na Aiven.

O módulo utiliza a conexão PostgreSQL já configurada no projeto.

---

### `main.py`

Responsável por orquestrar todo o processo:

```text
PDF
 ↓
extract
 ↓
transform
 ↓
load
```

---

# 🗄️ Modelo de dados

A principal tabela do projeto será:

## `ft_transacoes`

Estrutura inicial:

| Campo                  | Tipo          | Descrição                  |
| ---------------------- | ------------- | -------------------------- |
| `id_transacao`         | BIGSERIAL     | Identificador da transação |
| `data_transacao`       | DATE          | Data da transação          |
| `hora_transacao`       | TIME          | Horário da transação       |
| `data_viagem`          | DATE          | Data associada à viagem    |
| `hora_viagem`          | TIME          | Horário associado à viagem |
| `produto`              | VARCHAR       | Produto da viagem          |
| `valor`                | NUMERIC(10,2) | Valor da transação         |
| `saldo_apos_transacao` | NUMERIC(10,2) | Saldo após a transação     |

---

## 📊 Análises planejadas

A base permitirá construir indicadores como:

### Indicadores gerais

* Ganhos totais
* Quantidade de viagens
* Ticket médio
* Ganho médio por viagem
* Ganho por dia

### Análises temporais

* Ganhos por dia
* Ganhos por semana
* Ganhos por mês
* Ganhos por horário
* Melhores dias da semana
* Melhores horários para dirigir

### Análises por produto

* Ganhos com Uber X
* Ganhos com Prioridade
* Quantidade de viagens por produto
* Ticket médio por produto
* Participação de cada produto nos ganhos

---

# ⚙️ Configuração

As credenciais do PostgreSQL/Aiven não devem ser armazenadas diretamente no código.

Utilize variáveis de ambiente ou um arquivo `.env`.

Exemplo:

```text
DB_HOST=seu_host
DB_PORT=27005
DB_NAME=defaultdb
DB_USER=avnadmin
DB_PASSWORD=sua_senha
```

O arquivo `.env` deve estar no `.gitignore`:

```gitignore
.env
```

---

# ▶️ Execução

O PDF é informado diretamente na execução do programa.

Exemplo:

```powershell
python src\main.py "C:\Users\Documents\Uber\relatorio_17_08_2026.pdf"
```

O fluxo será:

```text
1. Ler PDF
       ↓
2. Extrair transações
       ↓
3. Criar DataFrame
       ↓
4. Transformar dados
       ↓
5. Validar dados
       ↓
6. Carregar PostgreSQL
```

---

# 🔎 Exemplo de execução

```text
Transações extraídas: 16

Transformação concluída.

Total de ganhos: R$ 188,96

Carga concluída com sucesso.

Tabela: ft_transacoes
```

---

# 🧪 Validação dos dados

O pipeline deve validar se todas as transações presentes no PDF foram extraídas.

Uma das validações consiste em comparar:

```text
Total das transações extraídas
        =
Total de ganhos apresentado no relatório
```

Essa validação é importante para evitar que alterações futuras no layout do PDF provoquem uma carga incompleta no banco de dados.

---

# 🔄 Atualização semanal

O projeto foi pensado para receber um novo extrato semanal.

O processo será:

```text
Novo PDF Uber
      ↓
Executar main.py
      ↓
Extract
      ↓
Transform
      ↓
Load
      ↓
Aiven
      ↓
Power BI
```

Não é necessário alterar o código a cada semana.

Basta informar o novo arquivo PDF:

```powershell
python src\main.py "C:\Users\Documents\uber\novo_relatorio.pdf"
```

---

# 📈 Power BI

O PostgreSQL/Aiven será utilizado como fonte de dados do Power BI.

A arquitetura final será:

```text
Uber
 │
 │ PDF semanal
 ▼
Python ETL
 │
 ├── Extract
 ├── Transform
 └── Load
       │
       ▼
PostgreSQL / Aiven
       │
       ▼
Power BI
       │
       ▼
Uber Earnings Analytics
```

---

# 🛠️ Tecnologias

* Python
* Pandas
* pdfplumber
* PostgreSQL
* Aiven
* Power BI
* Git / GitHub

---

# 📌 Próximos passos

* [ ] Automatizar identificação do período do relatório
* [ ] Criar validação automática do total de ganhos
* [ ] Criar dimensão calendário
* [ ] Criar dimensão de produtos
* [ ] Criar histórico semanal
* [ ] Evitar duplicação de transações
* [ ] Criar métricas DAX
* [ ] Criar dashboard no Power BI
* [ ] Analisar ganho por hora
* [ ] Analisar ganho por dia da semana
* [ ] Analisar desempenho por produto
* [ ] Criar indicadores de rentabilidade



# 👨‍💻 Autor

Gabriel Prata

Especialista em Business Intelligence (BI) | Cientista de Dados | Data Viz Developer | Analytics Engineer

📍 Rio de Janeiro - Brasil
