import pandas as pd

import streamlit as st
import plotly.express as px
from Acesso_Dados_servidor_FTP import *

# Certifique-se de carregar seu DataFrame df_ondas_nao_direcionais antes de executar este código
def main():
    # Título do aplicativo
    st.title("Visualização de Séries Temporais de Ondas Não Direcionais")
    
    # Descrição
    st.markdown("""
    Este aplicativo permite visualizar séries temporais para os dados de ondas não direcionais.
    Selecione as colunas e ajuste os filtros para explorar os dados.
    """)

    # Carregar o DataFrame
    @st.cache_data(ttl=1800)  # Cache com validade de 30 minutos (1800 segundos)
    def carregar_dados():
        
        df = importar_dados_servidor_ftp()
        df_ondas_nao_direcionais = df.iloc[255:]
        df_ondas_nao_direcionais['TIMESTAMP_ORIGINAL'] = pd.to_datetime(df_ondas_nao_direcionais['TIMESTAMP'])
        df_ondas_nao_direcionais = df_ondas_nao_direcionais.set_index('TIMESTAMP_ORIGINAL')
        df_ondas_nao_direcionais = df_ondas_nao_direcionais.resample('30T').mean()
        return df_ondas_nao_direcionais

    df = carregar_dados()

    # Mostrar informações do DataFrame
    st.sidebar.subheader("Opções de Visualização")
    st.sidebar.write(f"Total de registros: {len(df)}")
    
    # Filtro de intervalo de datas
    st.sidebar.subheader("Filtro de Data")
    min_date, max_date = df.index.min(), df.index.max()
    date_range = st.sidebar.date_input("Selecione o intervalo", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]

    # Seleção de colunas para plotagem
    st.sidebar.subheader("Colunas para Visualização")
    colunas_disponiveis = [col for col in df.columns if col not in ["TIMESTAMP", "RECORD"]]  # Remove "RECORD"
    colunas_selecionadas = st.sidebar.multiselect(
        "Selecione as colunas", colunas_disponiveis, default=colunas_disponiveis
    )

    # Mostrar dados mais recentes
    if colunas_selecionadas:
        st.subheader("Dados Mais Recentes")
        ultimo_registro = df.iloc[-1]  # Obtém o último registro do DataFrame
        ultimo_timestamp = df.index[-1]  # Obtém o timestamp mais recente

        # Card para o timestamp
        st.markdown(f"### Última Atualização: {ultimo_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # Exibir os valores em uma grade com fonte menor
        num_colunas = 3  # Número de colunas por linha na grade
        for i in range(0, len(colunas_selecionadas), num_colunas):
            cols = st.columns(num_colunas)
            for j, coluna in enumerate(colunas_selecionadas[i:i+num_colunas]):
                with cols[j]:
                    st.markdown(
                        f"""
                        <div style="text-align: left; font-size: 14px;">
                            <strong>{coluna}</strong><br>
                            {ultimo_registro[coluna]:.2f}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Gerar gráfico interativo
    if colunas_selecionadas:
        st.subheader("Gráfico de Séries Temporais")
        for coluna in colunas_selecionadas:
            fig = px.line(df, x=df.index, y=coluna, title=f"Série Temporal: {coluna}", labels={"x": "Data e Hora", "y": coluna})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione ao menos uma coluna para visualização.")

# Executar a aplicação
if __name__ == "__main__":
    main()
