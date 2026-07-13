import pytest
import pandas as pd
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)

from transformacao import (
    _filtrar_anos_completos,
    _calcular_resumo_anual,
    _calcular_fator_composto,
    _agregar_e_calcular_fatores,
    processar_dados_ipca
)

@pytest.fixture
def df_anos_completos():
    """Cria um DataFrame com dados para um ano completo (12 meses) e um incompleto (3 meses)."""
    # 2022: 12 meses, inflação mensal de 1%
    meses_2022 = ["202201", "202202", "202203", "202204", "202205", "202206",
                  "202207", "202208", "202209", "202210", "202211", "202212"]

    # 2023: 3 meses, inflação mensal de 2%
    meses_2023 = ["202301", "202302", "202303"]

    codigos = meses_2022 + meses_2023
    anos = [2022] * 12 + [2023] * 3
    inflacoes = [1.0] * 12 + [2.0] * 3

    df = pd.DataFrame({
        "Codigo_Mes": codigos,
        "Ano": anos,
        "Inflacao_Mensal": inflacoes,
    })
    df["Fator"] = 1 + (df["Inflacao_Mensal"] / 100)
    return df

@pytest.fixture
def df_resumo_mock():
    """Cria um DataFrame mock representando o output de _calcular_resumo_anual, para 12 anos."""
    anos = list(range(2010, 2022)) # 12 anos

    df = pd.DataFrame({
        "Ano": anos,
        "Media_Mensal": [1.0] * 12,
        "Acumulado_Ano": [10.0] * 12,
    })
    return df

def test_filtrar_anos_completos(df_anos_completos):
    df_filtrado = _filtrar_anos_completos(df_anos_completos)

    # Deve conter apenas o ano de 2022 (que tem 12 registros)
    assert 2022 in df_filtrado["Ano"].unique()
    assert 2023 not in df_filtrado["Ano"].unique()
    assert len(df_filtrado) == 12

def test_calcular_resumo_anual():
    # Cria df com 1 ano completo com inflacao de 1% e outro de 2%
    anos = [2022] * 12 + [2023] * 12
    codigos = ["202201", "202202", "202203", "202204", "202205", "202206", "202207", "202208", "202209", "202210", "202211", "202212"] + ["202301", "202302", "202303", "202304", "202305", "202306", "202307", "202308", "202309", "202310", "202311", "202312"]
    inflacoes = [1.0] * 12 + [2.0] * 12

    df = pd.DataFrame({
        "Codigo_Mes": codigos,
        "Ano": anos,
        "Inflacao_Mensal": inflacoes,
    })
    df["Fator"] = 1 + (df["Inflacao_Mensal"] / 100)

    df_resumo = _calcular_resumo_anual(df)

    assert len(df_resumo) == 2
    assert "Ano" in df_resumo.columns
    assert "Media_Mensal" in df_resumo.columns
    assert "Acumulado_Ano" in df_resumo.columns

    # Para 2022: inflação de 1%. Acumulado = (1.01 ^ 12 - 1) * 100
    esperado_2022 = ((1.01 ** 12) - 1) * 100
    # round 4 digits como no código original
    esperado_2022 = round(esperado_2022, 4)
    assert df_resumo.loc[df_resumo["Ano"] == 2022, "Acumulado_Ano"].values[0] == esperado_2022
    assert df_resumo.loc[df_resumo["Ano"] == 2022, "Media_Mensal"].values[0] == 1.0

def test_calcular_resumo_anual_erro_vazio():
    df = pd.DataFrame(columns=["Ano", "Codigo_Mes", "Inflacao_Mensal", "Fator"])
    with pytest.raises(ValueError, match="Nenhum ano completo"):
        _calcular_resumo_anual(df)

def test_calcular_fator_composto(df_resumo_mock):
    df_fator = _calcular_fator_composto(df_resumo_mock)

    # Deve retornar os últimos 10 anos (2012 a 2021)
    assert len(df_fator) == 10
    assert df_fator["Ano"].min() == 2012
    assert df_fator["Ano"].max() == 2021

    # Verifica colunas
    assert "Fator_Composto_Acumulado" in df_fator.columns
    assert "Inflacao_Composta_Acumulada_Perc" in df_fator.columns
    assert "Fator_Anual" not in df_fator.columns

    # Fator_Anual seria 1 + 10/100 = 1.1.
    # No primeiro ano (2012): cumprod = 1.1
    # No segundo ano (2013): cumprod = 1.1 * 1.1 = 1.21
    assert df_fator.loc[df_fator["Ano"] == 2012, "Fator_Composto_Acumulado"].values[0] == 1.1000
    assert df_fator.loc[df_fator["Ano"] == 2013, "Fator_Composto_Acumulado"].values[0] == 1.2100

def test_agregar_e_calcular_fatores(df_anos_completos):
    # Usa df_anos_completos, mas como _calcular_resumo exige 12 meses e tem um ano com 12
    df_resumo = _agregar_e_calcular_fatores(df_anos_completos)

    # Deve conter apenas o ano de 2022
    assert len(df_resumo) == 1
    assert df_resumo["Ano"].values[0] == 2022
    assert "Fator_Composto_Acumulado" in df_resumo.columns

def test_processar_dados_ipca_integration(tmp_path):
    # Cria CSV bruto fictício
    arquivo_bruto = tmp_path / "ipca_bruto.mock.csv"
    arquivo_limpo = tmp_path / "ipca_limpo.mock.csv"

    # Dados brutos para 2022 completo e 2023 completo
    meses_2022 = ["202201", "202202", "202203", "202204", "202205", "202206", "202207", "202208", "202209", "202210", "202211", "202212"]
    meses_2023 = ["202301", "202302", "202303", "202304", "202305", "202306", "202307", "202308", "202309", "202310", "202311", "202312"]

    codigos = [""] + meses_2022 + meses_2023
    valores = [""] + ["1,5"] * 12 + ["2,5"] * 12

    df_raw = pd.DataFrame({
        "Nível Territorial (Código)": ["Mês (Código)"] + codigos[1:],
        "Brasil": ["Valor"] + valores[1:]
    })

    df_raw.to_csv(arquivo_bruto, index=False)

    processar_dados_ipca(str(arquivo_bruto), str(arquivo_limpo))

    assert os.path.exists(arquivo_limpo)

    df_limpo = pd.read_csv(arquivo_limpo, sep=";")
    assert len(df_limpo) == 2
    assert 2022 in df_limpo["Ano"].values
    assert 2023 in df_limpo["Ano"].values
    assert "Inflacao_Composta_Acumulada_Perc" in df_limpo.columns
