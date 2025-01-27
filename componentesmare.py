import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Frequências dos componentes de maré (em Hz)
frequencias = { 
    "M2": 28.9841042 / 3600, "S2": 30.0000000 / 3600, "N2": 28.4397295 / 3600, "O1": 13.9430356 / 3600,
    "K1": 15.0410686 / 3600, "K2": 30.0821373 / 3600, "MU2": 27.9682084 / 3600, "M4": 57.9682084 / 3600,
    "L2": 29.5284789 / 3600, "Q1": 13.3986609 / 3600, "MN4": 57.4238337 / 3600, "NU2": 28.5125831 / 3600,
    "M3": 43.4761563 / 3600, "T2": 29.9589333 / 3600
}

# Função para calcular cada componente de maré individualmente
def calcular_componente(amplitude, fase, frequencia, tempos):
    fase_rad = np.radians(fase)
    return amplitude * np.cos(2 * np.pi * frequencia * tempos + fase_rad)

# Função para gerar o gráfico de componentes
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

# Função para calcular a maré combinada
def calcular_mare(amplitudes, fases, frequencias, tempos):
    mare = np.zeros_like(tempos)
    for i in range(len(amplitudes)):
        fase_rad = np.radians(fases[i])
        mare += amplitudes[i] * np.cos(2 * np.pi * frequencias[i] * tempos + fase_rad)
    return mare

# Função para gerar o gráfico de maré combinada
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

# Configuração do Streamlit
st.title("Previsão de Maré para 1 Ano")

# Seleção dos componentes
componentes_disponiveis = list(frequencias.keys())
componentes_selecionados = st.multiselect("Selecione os componentes de maré", componentes_disponiveis, default=["M2", "S2", "O1"])

# Inputs dos componentes selecionados
amplitudes = []
fases = []
for componente in componentes_selecionados:
    st.subheader(f"Componente {componente}")
    ampl = st.number_input(f"Amplitude do componente {componente} (m)", min_value=0.0, value=1.0)
    fase = st.number_input(f"Fase do componente {componente} (graus)", min_value=0.0, max_value=360.0, value=0.0)
    amplitudes.append(ampl)
    fases.append(fase)

# Ajuste no intervalo de tempo: resolução horária (1 ano = 8760 horas)
tempos = np.linspace(0, 8760, 8760)

# Frequências dos componentes selecionados
frequencias_selecionadas = [frequencias[componente] for componente in componentes_selecionados]

# Calculando a maré combinada
mare = calcular_mare(amplitudes, fases, frequencias_selecionadas, tempos)

# Plotando o gráfico de maré combinada
st.plotly_chart(plotar_mare(tempos, mare))

# Plotando o gráfico de cada componente individual
st.plotly_chart(plotar_componentes(tempos, componentes_selecionados, amplitudes, fases, frequencias_selecionadas))
