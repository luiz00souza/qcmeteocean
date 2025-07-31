import streamlit as st
import numpy as np
import plotly.graph_objects as go

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
    "MSF": 1.9322736 / 3600,  # frequência associada ao ciclo mensal de maré
    "MM": 0.5443747 / 3600,   # maré mensal
}

# Presets de exemplo
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

# Funções de cálculo e plotagem
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
        title='Previsão de Maré para 1 Ano',
        xaxis_title='Tempo (dias)',
        yaxis_title='Altura da Maré (m)',
        template='plotly_dark'
    )
    return fig

# Interface Streamlit
st.title("Plataforma Interativa para Análise de Componentes de Maré")

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

# Divide a página em duas colunas: inputs e gráficos
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
    # Calcula e plota com os valores atuais
    tempos = np.linspace(0, 28*24, 28*24)  # 28 dias * 24 horas = 672 horas
    frequencias_selecionadas = [frequencias[comp] for comp in componentes_selecionados]

    mare = calcular_mare(amplitudes, fases, frequencias_selecionadas, tempos)
    st.plotly_chart(plotar_mare(tempos, mare), use_container_width=True)
    st.plotly_chart(plotar_componentes(tempos, componentes_selecionados, amplitudes, fases, frequencias_selecionadas), use_container_width=True)
