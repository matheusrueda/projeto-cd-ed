import pytest
import pandas as pd
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)

from transformacao import _limpar_e_converter_tipos

def test_limpar_e_converter_tipos_edge_cases():
    """
    Testes de regressão para garantir o comportamento de _limpar_e_converter_tipos
    em diferentes casos envolvendo nulos e valores problemáticos, especialmente
    após a conversão (to_numeric com errors="coerce").
    """
    # Cenário: Mistura de válidos, nulos originais e strings inválidas que vão virar NaN.
    # Também testa datas válidas, inválidas e nulas.
    data = {
        "Codigo_Mes": ["202301", "202302", "invalido", "202304", "202305"],
        "Inflacao_Mensal": ["1,5", None, "2,0", "invalido", "3.0"]
    }
    df = pd.DataFrame(data)

    df_limpo = _limpar_e_converter_tipos(df.copy())

    # Verifica se as linhas com valores inválidos e nulos de inflação/data foram removidas.
    # 202301: Inflacao 1.5, Data OK -> Mantém
    # 202302: Inflacao None -> Remove
    # invalido: Inflacao 2.0, mas Data Invalida -> Remove (errors=coerce no to_datetime gera NaT)
    # 202304: Inflacao "invalido" -> Remove (errors=coerce no to_numeric gera NaN)
    # 202305: Inflacao 3.0 -> Mantém
    assert len(df_limpo) == 2
    assert df_limpo["Codigo_Mes"].tolist() == ["202301", "202305"]
    assert df_limpo["Inflacao_Mensal"].tolist() == [1.5, 3.0]

def test_limpar_e_converter_tipos_todos_nulos():
    # Cenário: Todos os valores da inflação se tornam NaN
    data = {
        "Codigo_Mes": ["202301", "202302"],
        "Inflacao_Mensal": [None, "invalido"]
    }
    df = pd.DataFrame(data)
    df_limpo = _limpar_e_converter_tipos(df.copy())
    assert len(df_limpo) == 0

def test_limpar_e_converter_tipos_nenhum_nulo():
    # Cenário: Todos os valores são válidos e nenhum se torna NaN
    data = {
        "Codigo_Mes": ["202301", "202302"],
        "Inflacao_Mensal": ["1,5", "2,0"]
    }
    df = pd.DataFrame(data)
    df_limpo = _limpar_e_converter_tipos(df.copy())
    assert len(df_limpo) == 2
    assert df_limpo["Inflacao_Mensal"].tolist() == [1.5, 2.0]
