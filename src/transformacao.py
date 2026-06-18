import os
import logging
import pandas as pd

# Configura o logging para acompanhar o processo
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _carregar_dados_brutos(caminho_bruto: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV de dados brutos e ajusta o cabeçalho.

    Args:
        caminho_bruto (str): Caminho para o arquivo CSV bruto.

    Returns:
        pd.DataFrame: DataFrame com os dados carregados e cabeçalho ajustado.

    Raises:
        FileNotFoundError: Se o arquivo de dados brutos não existir.
    """
    logger.info(f"Carregando dados brutos de: {caminho_bruto}")
    if not os.path.exists(caminho_bruto):
        raise FileNotFoundError(
            f"Arquivo de dados brutos não encontrado em: {caminho_bruto}"
        )

    # Lê os dados brutos
    df_raw = pd.read_csv(caminho_bruto, dtype=str)

    # Ajusta cabeçalho (a primeira linha contém a descrição amigável das colunas)
    df = df_raw.copy()
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    return df


def _validar_estrutura_e_renomear(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida a presença das colunas obrigatórias e renomeia para colunas internas.

    Args:
        df (pd.DataFrame): DataFrame original carregado.

    Returns:
        pd.DataFrame: DataFrame contendo apenas as colunas relevantes renomeadas.

    Raises:
        KeyError: Se as colunas necessárias não forem encontradas no DataFrame.
    """
    logger.info("Filtrando e renomeando colunas relevantes...")
    # Verifica se as colunas esperadas estão presentes
    colunas_necessarias = {"Mês (Código)", "Valor"}
    if not colunas_necessarias.issubset(df.columns):
        raise KeyError(
            f"As colunas necessárias {colunas_necessarias} não foram encontradas no arquivo bruto. "
            f"Colunas encontradas: {list(df.columns)}"
        )

    df = df[["Mês (Código)", "Valor"]].copy()
    df.columns = ["Codigo_Mes", "Inflacao_Mensal"]
    return df


def _limpar_e_converter_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza a conversão numérica de inflação, remoção de nulos, parsing de data e ordenação.

    Args:
        df (pd.DataFrame): DataFrame com colunas internas renomeadas.

    Returns:
        pd.DataFrame: DataFrame limpo e ordenado cronologicamente.
    """
    # Conversão de tipos e tratamento de valores nulos
    df["Inflacao_Mensal"] = pd.to_numeric(
        df["Inflacao_Mensal"].str.replace(",", ".", regex=False), errors="coerce"
    )
    # Se houver algum nulo na inflação, removemos a linha correspondente
    if df["Inflacao_Mensal"].isnull().any():
        nulos_count = df["Inflacao_Mensal"].isnull().sum()
        logger.warning(
            f"Encontrados {nulos_count} valores nulos na coluna Inflacao_Mensal. Removendo-os."
        )
        df = df.dropna(subset=["Inflacao_Mensal"])

    # Trata datas e anos
    df["Data"] = pd.to_datetime(df["Codigo_Mes"], format="%Y%m", errors="coerce")
    if df["Data"].isnull().any():
        logger.warning(
            "Linhas com datas inválidas foram encontradas e serão removidas."
        )
        df = df.dropna(subset=["Data"])

    df["Ano"] = df["Data"].dt.year

    # Ordenação cronológica rigorosa para cálculos compostos acumulados
    df = df.sort_values("Data").reset_index(drop=True)

    return df


def _agregar_e_calcular_fatores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula o acumulado anual, filtra anos incompletos, seleciona os últimos 10 anos,
    e computa o fator composto acumulado.

    Args:
        df (pd.DataFrame): DataFrame limpo e ordenado.

    Returns:
        pd.DataFrame: DataFrame de resumo anual contendo as colunas finais calculadas.

    Raises:
        ValueError: Se nenhum ano completo com 12 meses for encontrado.
    """
    # Fator de inflação: (1 + variação_mensal / 100)
    df["Fator"] = 1 + (df["Inflacao_Mensal"] / 100)

    logger.info("Realizando consolidação anual e cálculo de fatores compostos...")

    # Filtra anos incompletos de forma vetorizada
    counts = df.groupby("Ano")["Codigo_Mes"].transform("count")
    anos_ignorados = df[counts != 12]["Ano"].unique()

    if len(anos_ignorados) > 0:
        logger.info(
            f"Anos ignorados por conterem dados incompletos: {list(anos_ignorados)}"
        )

    df_valido = df[counts == 12]

    # Agregação vetorizada
    df_resumo = (
        df_valido.groupby("Ano")
        .agg(Media_Mensal=("Inflacao_Mensal", "mean"), Fator_Prod=("Fator", "prod"))
        .reset_index()
    )

    # Calcula o acumulado anual
    df_resumo["Acumulado_Ano"] = (df_resumo["Fator_Prod"] - 1) * 100

    # Formatação e seleção das colunas desejadas para igualar ao comportamento original
    df_resumo["Media_Mensal"] = df_resumo["Media_Mensal"].round(4)
    df_resumo["Acumulado_Ano"] = df_resumo["Acumulado_Ano"].round(4)
    df_resumo = df_resumo[["Ano", "Media_Mensal", "Acumulado_Ano"]]

    if df_resumo.empty:
        raise ValueError(
            "Nenhum ano completo (com 12 meses) foi encontrado para processamento."
        )

    # Ordena por ano
    df_resumo = df_resumo.sort_values("Ano").reset_index(drop=True)

    # Filtra estritamente os últimos 10 anos cheios disponíveis
    df_resumo = df_resumo.tail(10).reset_index(drop=True)

    # Cálculo do fator composto acumulado ao longo da série de 10 anos (inflação composta acumulada ano a ano)
    # Fator anual correspondente: 1 + (Acumulado_Ano / 100)
    df_resumo["Fator_Anual"] = 1 + (df_resumo["Acumulado_Ano"] / 100)

    # Multiplicação acumulada dos fatores anuais para obter a trajetória da inflação composta
    df_resumo["Fator_Composto_Acumulado"] = df_resumo["Fator_Anual"].cumprod()
    # Inflação composta acumulada em percentual a partir do início da série
    df_resumo["Inflacao_Composta_Acumulada_Perc"] = (
        df_resumo["Fator_Composto_Acumulado"] - 1
    ) * 100

    # Arredondamentos finais para gravação limpa no CSV
    df_resumo["Media_Mensal"] = df_resumo["Media_Mensal"].round(2)
    df_resumo["Acumulado_Ano"] = df_resumo["Acumulado_Ano"].round(2)
    df_resumo["Fator_Composto_Acumulado"] = df_resumo["Fator_Composto_Acumulado"].round(
        4
    )
    df_resumo["Inflacao_Composta_Acumulada_Perc"] = df_resumo[
        "Inflacao_Composta_Acumulada_Perc"
    ].round(2)

    # Remove a coluna auxiliar do fator anual antes de salvar
    df_resumo = df_resumo.drop(columns=["Fator_Anual"])

    return df_resumo


def _salvar_dados_processados(df_resumo: pd.DataFrame, caminho_limpo: str) -> None:
    """
    Grava os dados consolidados em formato CSV adequado para consumo.

    Args:
        df_resumo (pd.DataFrame): DataFrame de resumo contendo dados consolidados.
        caminho_limpo (str): Caminho onde o arquivo final limpo será salvo.
    """
    # Salvar o CSV limpo de forma compatível com Excel brasileiro e sistemas gerais (delimitador ";", utf-8-sig)
    os.makedirs(os.path.dirname(caminho_limpo), exist_ok=True)
    df_resumo.to_csv(caminho_limpo, index=False, sep=";", encoding="utf-8-sig")
    logger.info(f"Dados limpos salvos com sucesso em: {caminho_limpo}")


def processar_dados_ipca(
    caminho_bruto: str = "data/ipca_bruto.csv",
    caminho_limpo: str = "data/ipca_limpo.csv",
) -> None:
    """
    Lê os dados brutos de IPCA, realiza o processamento e limpeza, calcula as métricas
    anuais acumuladas e o fator composto, e salva o arquivo final limpo.

    Args:
        caminho_bruto (str): Caminho para o arquivo CSV bruto (padrão: "data/ipca_bruto.csv").
        caminho_limpo (str): Caminho onde os dados limpos e consolidados serão salvos (padrão: "data/ipca_limpo.csv").

    Raises:
        FileNotFoundError: Se o arquivo de dados brutos não for encontrado.
        KeyError: Se as colunas necessárias não estiverem no DataFrame.
        ValueError: Se houver problemas com os valores durante o processamento.
        RuntimeError: Para erros gerais durante o pipeline de transformação.
    """
    try:
        df = _carregar_dados_brutos(caminho_bruto)
        df = _validar_estrutura_e_renomear(df)
        df = _limpar_e_converter_tipos(df)
        df_resumo = _agregar_e_calcular_fatores(df)
        _salvar_dados_processados(df_resumo, caminho_limpo)
    except (FileNotFoundError, KeyError, ValueError) as e:
        logger.error(f"Erro de validação ou leitura nos dados do IPCA: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Erro crítico e inesperado no processamento de dados do IPCA: {e}"
        )
        raise RuntimeError(f"Falha na transformação de dados: {e}") from e


if __name__ == "__main__":
    import sys

    try:
        processar_dados_ipca()
        sys.exit(0)
    except Exception as erro:
        logger.error(f"Execução do pipeline de transformação falhou: {erro}")
        sys.exit(1)
