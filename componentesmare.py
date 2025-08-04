import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
# Frequências completas (incluindo compostas)
frequencias = { 
    "M2": 28.9841042 / 3600,
    "S2": 30.0000000 / 3600,
    "N2": 28.4397295 / 3600,
    "O1": 13.9430356 / 3600,
    "K1": 15.0410686 / 3600,
    "K2": 30.0821373 / 3600,
    "MU2": 27.9682084 / 3600,
    "M4": 57.9682084 / 3600,
    "L2": 29.5284789 / 3600,
    "Q1": 13.3986609 / 3600,
    "MN4": 57.4238337 / 3600,
    "NU2": 28.5125831 / 3600,
    "M3": 43.4761563 / 3600,
    "T2": 29.9589333 / 3600,
    "MSF": 1.9322736 / 3600,
    "MM": 0.5443747 / 3600,
}

presets_locais = {
    "CPES-Vitória": {
        "M2": (0.4587739969048418, 82.16921719923965),
        "K1": (0.045779721927129445, 169.73298760362874),
        "M4": (0.0031038639381563643, 59.627326215354664),
    },
    "Samarco – Ubu": {
        "M2": (0.5820684105897616, 180.41713134014032),
        "K1": (0.1734321320257419, 210.98874760600413),
        "M4": (0.026945604631100437, 279.602197775661),
    },
    "Itaguaí": {
        "M2": (0.29630946245269113, 78.24866964923923),
        "M4": (0.12530952513386817, 66.3473426106271),
        "K1": (0.08788699956826367, 200.03110936076735),
    },
    "Porto do Açu Toil": {
        "M2": (0.45454942011676547, 85.97285706503982),
        "S2": (0.22507785902010036, 122.47269029615013),
        "O1": (0.133965933019395, 110.6967659002902),
    },
    "Ilha de Barnabé": {
        "M2": (0.40928405715926325, 175.65725759511687),
        "S2": (0.3674345877298507, 183.8165546465426),
        "O1": (0.11664018080083313, 125.26525034054676),
        "MSF": (0.0896375677055137, 358.78975632764786),
        "MM": (0.06933287814677602, 158.62996627728032),
        "N2": (0.06266214663352522, 228.83744072258355),
        "M3": (0.05080402265029361, 346.62209845785327),
        "K1": (0.03942527218297983, 180.9379917885554),
    },
    "Outro (personalizado)": {}
}

# Funções auxiliares
def calcular_componente(amplitude, fase, frequencia, tempos):
    fase_rad = np.radians(fase)
    return amplitude * np.cos(2 * np.pi * frequencia * tempos + fase_rad)

def plotar_componentes(tempos, componentes, amplitudes, fases, frequencias):
    fig = go.Figure()
    for i, componente in enumerate(componentes):
        valores = calcular_componente(amplitudes[i], fases[i], frequencias[i], tempos)
        fig.add_trace(go.Scatter(x=tempos / 24, y=valores, mode='lines', name=f"{componente}"))
    fig.update_layout(
        title='Comportamento de Cada Componente de Maré',
        xaxis_title='Tempo (dias)',
        yaxis_title='Altura (m)',
        template='plotly_dark'
    )
    return fig

def calcular_mare(amplitudes, fases, frequencias, tempos):
    mare = np.zeros_like(tempos)
    for i in range(len(amplitudes)):
        fase_rad = np.radians(fases[i])
        mare += amplitudes[i] * np.cos(2 * np.pi * frequencias[i] * tempos + fase_rad)
    return mare

def plotar_mare(tempos, mare):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tempos / 24, y=mare, mode='lines', name='Maré Combinada'))
    fig.update_layout(
        title='Previsão de Maré para 28 Dias',
        xaxis_title='Tempo (dias)',
        yaxis_title='Altura da Maré (m)',
        template='plotly_dark'
    )
    return fig

# Sidebar para navegação
aba = st.sidebar.radio("🔍 Navegação", ["📘 Apresentação", "🌊 Simulação"])

# Página de apresentação
if aba == "📘 Apresentação":
    st.markdown("""
    # 🌊 Plataforma Interativa de Simulação de Maré

    Esta plataforma permite explorar de forma interativa como as **componentes harmônicas da maré** se combinam para gerar o comportamento observado do nível do mar em diferentes localidades.

    ## 🧭 Contexto

    A maré é o resultado da combinação de diversos componentes periódicos, cada um com sua **frequência**, **amplitude** e **fase**. Essas componentes estão associadas principalmente à interação gravitacional entre a Terra, a Lua e o Sol.

    Cada local possui uma assinatura única dessas componentes, o que explica por que o padrão de maré em Vitória é diferente do observado em Santos, por exemplo.

    ## ⚙️ O que esta ferramenta faz?

    - Permite **selecionar uma localidade** (ou inserir dados personalizados).
    - Visualiza, de forma gráfica, **a contribuição de cada componente** da maré ao longo do tempo.
    - Gera uma **previsão combinada da maré** com base nas componentes selecionadas.
    - Facilita o entendimento dos efeitos de **fase e amplitude** na variação do nível do mar.

    ## 🧪 Aplicações

    - Apoio a estudos oceanográficos e hidrodinâmicos.
    - Ensino de fundamentos sobre marés.
    - Planejamento costeiro e portuário.
    - Exploração de dados de calibração de modelos numéricos.

    ## 💡 Como usar

    1. Escolha uma localidade com componentes pré-definidos, ou selecione "Outro (personalizado)" para inserir os valores manualmente.
    2. Ajuste as amplitudes e fases conforme necessário.
    3. Visualize os gráficos para entender como as marés se formam e se somam ao longo dos dias.

    ---

    🔬 Esta ferramenta é parte de um esforço para **democratizar o entendimento dos processos físicos costeiros** e oferecer uma **visão holística** das variações do nível do mar.
    """, unsafe_allow_html=True)
    componentes = pd.DataFrame({
    "Componente": ["M2", "S2", "N2", "K1", "O1", "K2", "P1", "Q1", "M4", "MS4", "R2"],
    "Tipo": ["Lunar principal", "Solar principal", "Lunar declinação", "Luni-solar declinação", 
             "Lunar declinação", "Luni-solar", "Solar declinação", "Lunar declinação", 
             "Harmônica", "Harmônica mista", "Solar"],
    "Período (horas)": [12.42, 12.00, 12.66, 23.93, 25.82, 11.97, 24.07, 26.87, 6.21, 6.10, 12.00],
    "Descrição": [
        "Principal componente semidiurna causada pela Lua",
        "Componente semidiurna causada pelo Sol",
        "Variações lunares de declinação",
        "Combinação dos efeitos da Lua e do Sol (diurna)",
        "Componente diurna lunar",
        "Componente semidiurna mista",
        "Componente solar diurna",
        "Pequena componente lunar diurna",
        "Segunda harmônica de M2 (maré de fundo)",
        "Interação entre M2 e S2",
        "Outra componente solar semidiurna"
    ]
    })
    
    st.markdown("### 📋 Tabela de Componentes Harmônicas da Maré")
    st.dataframe(componentes)


# Página de simulação
elif aba == "🌊 Simulação":
    st.title("🌊 Plataforma interativa: Simulação de maré a partir de suas componentes")

    local = st.selectbox("Selecione uma localidade", list(presets_locais.keys()))

    if local != "Outro (personalizado)":
        componentes_selecionados = list(presets_locais[local].keys())
    else:
        componentes_disponiveis = list(frequencias.keys())
        componentes_selecionados = st.multiselect(
            "Selecione os componentes de maré", 
            componentes_disponiveis, 
            default=["M2", "S2", "O1"]
        )

    col_inputs, col_graficos = st.columns([1, 2])

    amplitudes = []
    fases = []

    with col_inputs:
        st.markdown("### Componentes da Maré")
        with st.expander("Editar componentes da maré", expanded=True):
            for componente in componentes_selecionados:
                st.markdown(f"<h5 style='margin-bottom: 3px;'>Componente {componente}</h5>", unsafe_allow_html=True)

                if local != "Outro (personalizado)":
                    valor_amp, valor_fase = presets_locais[local][componente]
                else:
                    valor_amp, valor_fase = 1.0, 0.0

                col1, col2 = st.columns(2)
                with col1:
                    ampl = st.number_input(
                        "Amplitude (m)", 
                        min_value=0.0, 
                        value=valor_amp, 
                        key=f"amp_{componente}"
                    )
                with col2:
                    fase = st.number_input(
                        "Fase (°)", 
                        min_value=0.0, 
                        max_value=360.0, 
                        value=valor_fase, 
                        key=f"fase_{componente}"
                    )

                amplitudes.append(ampl)
                fases.append(fase)

    with col_graficos:
        tempos = np.linspace(0, 28*24, 28*24)
        frequencias_selecionadas = [frequencias[comp] for comp in componentes_selecionados]

        mare = calcular_mare(amplitudes, fases, frequencias_selecionadas, tempos)
        st.plotly_chart(plotar_mare(tempos, mare), use_container_width=True)
        st.plotly_chart(plotar_componentes(tempos, componentes_selecionados, amplitudes, fases, frequencias_selecionadas), use_container_width=True)
