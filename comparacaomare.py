import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import scipy.stats as stats

# Caminho do arquivo
file_path = r"C:\Users\campo\Downloads\dados_mare_com_residuos (1).csv"

# Função para carregar os dados
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, delimiter=",")  # Ajuste o delimitador se necessário
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], dayfirst=True)  # Ajuste se necessário
    df = df.dropna(subset=["Filtro Fraco", "Pacmare", "Altura Prevista UTIDE", "TIMESTAMP"])
    return df

df = load_data(file_path)

# Função para calcular métricas
def calcular_metricas(verdadeiro, previsto):
    mae = mean_absolute_error(verdadeiro, previsto)
    rmse = np.sqrt(mean_squared_error(verdadeiro, previsto))
    r2 = r2_score(verdadeiro, previsto)
    mape = np.mean(np.abs((verdadeiro - previsto) / verdadeiro)) * 100
    return mae, rmse, r2, mape

# Cálculo das métricas
mae_pacmare, rmse_pacmare, r2_pacmare, mape_pacmare = calcular_metricas(df["Filtro Fraco"], df["Pacmare"])
mae_utide, rmse_utide, r2_utide, mape_utide = calcular_metricas(df["Filtro Fraco"], df["Altura Prevista UTIDE"])

# Erros individuais
df["Erro_Pacmare"] = df["Filtro Fraco"] - df["Pacmare"]
df["Erro_UTIDE"] = df["Filtro Fraco"] - df["Altura Prevista UTIDE"]

# Teste estatístico (Wilcoxon para dados pareados)
stat, p_value = stats.wilcoxon(df["Erro_Pacmare"], df["Erro_UTIDE"])

# Exibir métricas
st.write("### Avaliação dos Modelos")
st.write(f"**Pacmare:** MAE = {mae_pacmare:.4f}, RMSE = {rmse_pacmare:.4f}, R² = {r2_pacmare:.4f}, MAPE = {mape_pacmare:.2f}%")
st.write(f"**UTIDE:** MAE = {mae_utide:.4f}, RMSE = {rmse_utide:.4f}, R² = {r2_utide:.4f}, MAPE = {mape_utide:.2f}%")

st.write(f"**Teste estatístico Wilcoxon:** p-value = {p_value:.4f}")
if p_value < 0.05:
    st.write("🔹 Há diferença estatisticamente significativa entre os modelos.")
else:
    st.write("⚠️ Não há diferença estatística significativa entre os modelos.")

# Gráficos de erro
fig_residuos = px.line(df, x="TIMESTAMP", y=["Erro_Pacmare", "Erro_UTIDE"],
                       labels={"value": "Erro (m)", "TIMESTAMP": "Tempo"},
                       title="Resíduos dos Modelos")
st.plotly_chart(fig_residuos)

fig_hist = px.histogram(df, x=["Erro_Pacmare", "Erro_UTIDE"], 
                        title="Distribuição dos Erros", 
                        nbins=50, barmode="overlay")
st.plotly_chart(fig_hist)

# Gráfico de série temporal original
fig = px.line(df, x="TIMESTAMP", y=["Filtro Fraco", "Pacmare", "Altura Prevista UTIDE"], 
              labels={"value": "Altura (m)", "TIMESTAMP": "Tempo"},
              title="Comparação: Dados Observados vs Modelos")
st.plotly_chart(fig)
