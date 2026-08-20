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
