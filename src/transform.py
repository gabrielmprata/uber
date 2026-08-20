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
