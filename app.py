import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from src.constants import (
    VALORES_EXEMPLO,
    OPCOES_EXEMPLO,
    DESCRICOES,
    INTRODUCAO_MD,
    SIMULADOR_MD,
    TITLE_BAR,
    TITLE_AREA,
    TITLE_TABLE,
    HR_STYLE,
    CSS_STYLES,
    ANALISE_HISTORICA_MD,
    ARQUIVO_LIMPO,
)

# 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS
st.set_page_config(
    page_title="Análise de Inflação - IPCA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS para visual limpo e legível (Dark Mode adaptado com Fira Code nos números)
st.html(CSS_STYLES)


# 2. CARREGAMENTO DE DADOS COM CACHE
@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    """
    Carrega e retorna os dados consolidados do IPCA a partir do arquivo CSV.

    Parameters
    ----------
    caminho : str
        Caminho do arquivo CSV de entrada.

    Returns
    -------
    pd.DataFrame
        DataFrame contendo a série histórica limpa.
    """
    if not pd.io.common.file_exists(caminho):
        return pd.DataFrame()
    return pd.read_csv(caminho, sep=";")


df_ipca = carregar_dados(ARQUIVO_LIMPO)
if not df_ipca.empty:
    df_ipca["Fator_Interno"] = 1 + (df_ipca["Acumulado_Ano"] / 100)


def calcular_metricas_periodo(df: pd.DataFrame) -> tuple:
    """
    Calcula as métricas agregadas para o período selecionado de forma performática.

    Args:
        df (pd.DataFrame): DataFrame filtrado pelos anos selecionados.

    Returns:
        tuple: Contendo fator_periodo, inflacao_acumulada_periodo, media_mensal_periodo, pico_ano, pico_valor.
    """
    if df.empty:
        return 1.0, 0.0, 0.0, 0, 0.0

    fator_periodo = df["Fator_Interno"].prod()
    inflacao_acumulada_periodo = (fator_periodo - 1) * 100

    media_mensal_periodo = df["Media_Mensal"].mean()

    idx_max = df["Acumulado_Ano"].idxmax()
    pico_ano = int(df.loc[idx_max, "Ano"])
    pico_valor = df.loc[idx_max, "Acumulado_Ano"]

    return (
        fator_periodo,
        inflacao_acumulada_periodo,
        media_mensal_periodo,
        pico_ano,
        pico_valor,
    )


# 3. INTERFACE DE USUÁRIO (STREAMLIT)
if df_ipca.empty:
    st.error("Base de dados local não encontrada!")
    st.info(
        "Por favor, execute o pipeline de dados no terminal: `python src/extracao_ibge.py` seguido por `python src/transformacao.py`."
    )
else:
    # Sidebar Acadêmica
    st.sidebar.markdown(
        "## :blue[**Painel IPCA**]\n\n" ":gray[Ciência de Dados & Estrutura de Dados]"
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        ":gray[Este painel analisa a trajetória histórica da inflação oficial do país de forma interativa.]"
    )

    st.sidebar.markdown("### Filtros temporais")
    anos_disponiveis = df_ipca["Ano"].unique()

    # Filtro de seleção de anos
    anos_selecionados = st.sidebar.multiselect(
        "Selecione os Anos de Análise:",
        options=anos_disponiveis,
        default=anos_disponiveis,
    )

    if not anos_selecionados:
        st.warning(
            "Selecione pelo menos um ano na barra lateral para carregar as análises."
        )
    else:
        # Filtra os dados com base na seleção
        df_filtrado = df_ipca[df_ipca["Ano"].isin(anos_selecionados)].copy()
        df_filtrado = df_filtrado.sort_values("Ano").reset_index(drop=True)

        # Cabeçalho Principal (Storytelling Humano)
        st.title("Inflação Acumulada e o Custo de Vida no Brasil")
        st.markdown(INTRODUCAO_MD)
        st.markdown("---")

        # Calculo dinâmico de inflação acumulada total para o período filtrado
        (
            fator_periodo,
            inflacao_acumulada_periodo,
            media_mensal_periodo,
            pico_ano,
            pico_valor,
        ) = calcular_metricas_periodo(df_filtrado)

        # KPIs (Hero Section)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Inflação Acumulada no Período",
                value=f"{inflacao_acumulada_periodo:.2f}%",
                help="Variação inflacionária composta considerando todos os anos que estão ativos no seu filtro lateral.",
            )
        with col2:
            st.metric(
                label="Média Mensal da Inflação",
                value=f"{media_mensal_periodo:.2f}%",
                help="A média das taxas de variação mensais registradas nos anos selecionados.",
            )
        with col3:
            st.metric(
                label=f"Pico de Inflação ({pico_ano})",
                value=f"{pico_valor:.2f}%",
                help="O ano dentro da sua seleção que registrou a maior taxa fechada acumulada.",
            )

        st.markdown("\n\n")

        # SEÇÃO NOVA: SIMULADOR DE PODER DE COMPRA
        st.markdown("### O Impacto da Inflação no seu Bolso")

        st.markdown(SIMULADOR_MD)

        # Caixas do simulador lado a lado
        s_col1, s_col2 = st.columns([1.2, 1.8])
        with s_col1:
            exemplo_selecionado = st.selectbox(
                "Escolha um exemplo real:", options=OPCOES_EXEMPLO
            )

            valor_base = VALORES_EXEMPLO[exemplo_selecionado]

            valor_original = st.number_input(
                "Ou digite outro valor (R$):",
                min_value=0.1,
                value=float(valor_base),
                step=10.0,
                help="Digite o valor que servirá de base histórica no início do período.",
            )

        valor_necessario = valor_original * fator_periodo
        perda_poder_compra = (1 - (1 / fator_periodo)) * 100
        ano_inicial = df_filtrado["Ano"].min()
        ano_final = df_filtrado["Ano"].max()

        item_nome = DESCRICOES[exemplo_selecionado]

        with s_col2:
            st.markdown(
                f"{item_nome} que custava :green[**R\\$ {valor_original:.2f}**] em {ano_inicial}, custaria aproximadamente "
                f":red[**R\\$ {valor_necessario:.2f}**] em {ano_final} "
                f"para manter exatamente o mesmo padrão de consumo de itens equivalentes.\n\n"
                f":gray[Isso representa uma **corrosão real de {perda_poder_compra:.1f}% no poder de compra** do Real brasileiro durante este período.]"
            )

        st.markdown(HR_STYLE)

        # Abas
        tab_graficos, tab_tabela, tab_analise = st.tabs(
            [
                "Visualização Gráfica",
                "Tabela de Dados Consolidados",
                "Análise Histórica & Crises",
            ]
        )

        with tab_graficos:
            # Gráficos em duas colunas
            g_col1, g_col2 = st.columns(2)

            with g_col1:
                st.markdown(TITLE_BAR)

                # Gráfico de Barras Plotly
                fig_bar = px.bar(
                    df_filtrado,
                    x="Ano",
                    y="Acumulado_Ano",
                    text="Acumulado_Ano",
                    labels={"Acumulado_Ano": "Variação Anual (%)", "Ano": "Ano"},
                    template="plotly_dark",
                )

                # Customização visual do gráfico de barras
                fig_bar.update_traces(
                    marker_color="#2563eb",
                    texttemplate="%{text:.2f}%",
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>Ano:</b> %{x}<br><b>Inflação Acumulada:</b> %{y:.2f}%<extra></extra>",
                )
                fig_bar.update_layout(
                    margin=dict(l=10, r=10, t=25, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
                    xaxis=dict(
                        type="category",
                        showgrid=False,
                        linecolor="rgba(255,255,255,0.08)",
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.04)",
                        zeroline=True,
                        zerolinecolor="rgba(255,255,255,0.08)",
                        linecolor="rgba(255,255,255,0.08)",
                    ),
                    height=380,
                    hovermode="x",
                )
                st.plotly_chart(
                    fig_bar, width="stretch", config={"displayModeBar": False}
                )

            with g_col2:
                st.markdown(TITLE_AREA)

                # Gráfico de Linha / Área para Trajetória Composta
                df_filtrado["Trajetoria_Composta"] = (
                    df_filtrado["Fator_Interno"].cumprod() - 1
                ) * 100

                fig_line = px.area(
                    df_filtrado,
                    x="Ano",
                    y="Trajetoria_Composta",
                    labels={
                        "Trajetoria_Composta": "Inflação Acumulada Composta (%)",
                        "Ano": "Ano",
                    },
                    template="plotly_dark",
                )
                # Customização visual da linha e área
                fig_line.update_traces(
                    line_color="#db2777",
                    line_width=3,
                    fillcolor="rgba(219, 39, 119, 0.08)",
                    hovertemplate="<b>Ano:</b> %{x}<br><b>Inflação Composta Acumulada:</b> %{y:.2f}%<extra></extra>",
                )

                # Adiciona marcadores de pontos na linha de trajetória
                fig_line.add_trace(
                    go.Scatter(
                        x=df_filtrado["Ano"],
                        y=df_filtrado["Trajetoria_Composta"],
                        mode="markers+text",
                        text=df_filtrado["Trajetoria_Composta"].round(1).astype(str)
                        + "%",
                        textposition="top center",
                        marker=dict(color="#db2777", size=8),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

                fig_line.update_layout(
                    margin=dict(l=10, r=10, t=25, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
                    xaxis=dict(
                        type="category",
                        showgrid=False,
                        linecolor="rgba(255,255,255,0.08)",
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(255,255,255,0.04)",
                        zeroline=True,
                        zerolinecolor="rgba(255,255,255,0.08)",
                        linecolor="rgba(255,255,255,0.08)",
                    ),
                    height=380,
                )
                st.plotly_chart(
                    fig_line, width="stretch", config={"displayModeBar": False}
                )

        with tab_tabela:
            st.markdown(TITLE_TABLE)

            df_tabela = df_filtrado.copy()
            df_tabela["Ano"] = df_tabela["Ano"].astype(str)
            df_tabela["Media_Mensal"] = df_tabela["Media_Mensal"].map("{:.2f}%".format)
            df_tabela["Acumulado_Ano"] = df_tabela["Acumulado_Ano"].map(
                "{:.2f}%".format
            )
            df_tabela["Inflacao_Composta_Acumulada_Perc"] = df_tabela[
                "Inflacao_Composta_Acumulada_Perc"
            ].map("{:.2f}%".format)

            # Remove colunas auxiliares
            df_tabela = df_tabela.drop(columns=["Fator_Interno", "Trajetoria_Composta"])

            # Renomeia colunas para a exibição
            df_tabela.columns = [
                "Ano",
                "Média Inflação Mensal",
                "Inflação Acumulada Anual (IPCA)",
                "Fator de Multiplicação Composto",
                "Inflação Composta Acumulada (Série Total)",
            ]

            st.dataframe(df_tabela, width="stretch", hide_index=True)

        with tab_analise:
            # Análise Histórica Contextual formatada
            st.markdown(ANALISE_HISTORICA_MD)
