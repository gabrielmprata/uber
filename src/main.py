from extract import extract_transacoes
from transform import transformar_transacoes
# from load import load_transacoes


PDF_PATH = "data/relatorio_17_de_ago.pdf"


def main():

    # EXTRACT
    df = extract_transacoes(PDF_PATH)

    print(f"Transações extraídas: {len(df)}")

    # TRANSFORM
    df = transformar_transacoes(df)

    print(df.info())

    # LOAD
    # load_transacoes(df)


if __name__ == "__main__":
    main()
