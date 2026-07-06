VALORES_EXEMPLO = {
    "Customizado (R$ 100)": 100.0,
    "Cafezinho Simples (R$ 3,50)": 3.50,
    "Almoço Comercial (R$ 25,00)": 25.0,
    "Cesta Básica Familiar (R$ 400,00)": 400.0,
    "Salário Mínimo de 2016 (R$ 880,00)": 880.0,
}
OPCOES_EXEMPLO = list(VALORES_EXEMPLO.keys())

DESCRICOES = {
    "Customizado (R$ 100)": "Uma compra genérica",
    "Cafezinho Simples (R$ 3,50)": "Aquele cafezinho rápido na padaria",
    "Almoço Comercial (R$ 25,00)": "Um almoço comercial básico",
    "Cesta Básica Familiar (R$ 400,00)": "A cesta de mantimentos e alimentos da família",
    "Salário Mínimo de 2016 (R$ 880,00)": "A renda mensal equivalente a um salário mínimo da época",
}

INTRODUCAO_MD = """Quando falamos sobre a variação da inflação (IPCA), estamos olhando para a forma como o dinheiro que ganhamos perde poder de compra ao longo do tempo. Este painel foi construído de forma acadêmica para nos ajudar a compreender como a inflação se comportou ano a ano e o efeito cumulativo composto desse aumento no bolso do brasileiro."""

SIMULADOR_MD = """
**Simulador Prático de Perda de Poder de Compra**

:gray[Insira um valor em dinheiro no início do período filtrado. O simulador calculará o quanto seria equivalente hoje, demonstrando visualmente o efeito da corrosão inflacionária.]
"""


TITLE_BAR = "**Inflação Oficial Registrada Ano a Ano**"
TITLE_AREA = "**Trajetória da Inflação Composta no Período**"
TITLE_TABLE = "**Tabela de Dados Consolidados**"
HR_STYLE = "---"

CSS_STYLES = """
    <style>
        /* Ajuste de fontes globais no app */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Efeito de Glassmorphism suave nos cartões de métrica */
        div[data-testid="metric-container"] {
            background-color: rgba(30, 41, 59, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            padding: 22px 26px !important;
            border-radius: 14px !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="metric-container"]:hover {
            transform: translateY(-2px) !important;
            border-color: rgba(37, 99, 235, 0.4) !important;
            box-shadow: 0 15px 20px -5px rgba(37, 99, 235, 0.1) !important;
        }

        /* Estilização específica dos valores da métrica (Fonte mono-espaçada Fira Code para dados) */
        div[data-testid="stMetricValue"] {
            font-family: 'Fira Code', monospace !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }

        /* Estilização da sidebar */
        section[data-testid="stSidebar"] {
            background-color: #0b0f19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* Ajuste das caixas do Simulador */
        .simulador-card {
            background-color: rgba(30, 41, 59, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
        }

        /* Esconder decorações padrão do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background: transparent !important;}
    </style>
"""


ANALISE_HISTORICA_MD = """
#### :blue[**Entendendo o Comportamento Inflacionário Recente**]

:gray[A inflação brasileira é muito influenciada por eventos de grande escala, climáticos e geopolíticos. A seguir, explicamos de forma simples os três momentos mais marcantes da última década:]

**:red[●] Ajuste Econômico e Tarifas (2016)**

:gray[O ano de 2016 iniciou-se sob o reflexo da recessão econômica de 2015 e do forte realinhamento de preços administrados. Tarifas públicas como a conta de luz e o preço do combustível precisaram ser reajustadas de forma acentuada, mantendo o IPCA em um nível elevado de 6.29%.]

**:blue[●] Pandemia e Desorganização Global (2021)**

:gray[A inflação atingiu dois dígitos (10.03%) em 2021. As restrições de saúde no mundo todo paralisaram fábricas e portos, gerando escassez de componentes essenciais e encarecendo drasticamente o valor do frete internacional. No Brasil, o desequilíbrio na taxa de câmbio acelerou o encarecimento dos alimentos e produtos essenciais.]

**:green[●] Conflitos Geopolíticos e Alimentos (2022)**

:gray[Em 2022 a inflação fechou em 5.79%, sendo puxada fortemente pelo choque internacional decorrente do conflito armado na Ucrânia. O evento disparou o preço do petróleo e de insumos fundamentais (como fertilizantes e trigo). A inflação só não foi maior devido à redução emergencial de impostos federais e estaduais sobre energia e combustíveis.]
"""


ARQUIVO_LIMPO = "data/ipca_limpo.csv"
