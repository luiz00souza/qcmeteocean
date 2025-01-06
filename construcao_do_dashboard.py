# Modulos
import streamlit as st
import pandas as pd
import numpy as np

# Dados
np.random.seed(42)  # Para resultados reprodutíveis
tempo = pd.date_range(start='2025-01-01', end='2025-12-31', freq='ME')
consumo = np.random.normal(100, 25, size=len(tempo))
classificacao = np.random.choice(['A', 'B', 'C'], size=len(tempo))
latitude = np.random.uniform(-23.0, -22.0, size=len(tempo))
longitude = np.random.uniform(-43.5, -42.5, size=len(tempo)) 

dados = pd.DataFrame({
    'tempo': tempo,
    'consumo': consumo,
    'classificacao': classificacao,
    'latitude': latitude,
    'longitude': longitude
}).set_index('tempo')

# Configuração da página do Streamlit
st.set_page_config(layout="wide")

# Título do dashboard
st.title("Dashboard de Consumo com Localização")

# Exibindo os dados tabelados
st.subheader("Tabela de Dados")
st.dataframe(dados)

# Gráfico de série temporal
st.subheader("Gráfico de Série Temporal")
st.line_chart(dados['consumo'])

# Histograma
st.subheader("Histograma de Consumo")
st.bar_chart(dados['consumo'].value_counts(bins=20).sort_index())

# Mapa
st.subheader("Mapa de Localização")
st.map(dados[['latitude', 'longitude']])