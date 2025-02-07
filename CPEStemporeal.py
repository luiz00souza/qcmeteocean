import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px 
from Acesso_Dados_servidor_FTP_01 import *
from QC_OPERACIONAL_UMISAN import *
@st.cache_data(ttl=1800)  # Cache com validade de 30 minutos (1800 segundos)

def carregar_dados():
    df = importar_dados_servidor_ftp()
    df = df.drop(columns=["Sea_Level_filtered"])

    df['TIMESTAMP_ORIGINAL'] = pd.to_datetime(df['TIMESTAMP'])
    df= df.set_index('TIMESTAMP_ORIGINAL')
    df.columns = parameter_columns_ondas_nao_direcionais
    for coluna in df.columns:
        df[f'Flag_{coluna}'] = 0
    return df
def exibir_tabela(df):
    """Exibe a tabela com os dados e inclui opção para download."""
    st.subheader("Tabela de Dados")
    st.sidebar.subheader("Filtrar por Período")
    data_inicio = st.sidebar.date_input("Data Inicial", df['GMT-03:00'].min().date())
    data_fim = st.sidebar.date_input("Data Final", df['GMT-03:00'].max().date())
    if data_inicio > data_fim:
        st.error("A data inicial não pode ser posterior à data final.")
        return
    df_filtrado = df[(df['GMT-03:00'].dt.date >= data_inicio) & (df['GMT-03:00'].dt.date <= data_fim)]
    if st.session_state.permissao != "admin":
        df_filtrado = df_filtrado[[col for col in df_filtrado.columns if not col.endswith("flag")]]
    st.dataframe(df_filtrado)
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="Baixar Dados",
        data=csv,
        file_name="dados_mare_filtrados.csv",
        mime="text/csv"
    )
def exibir_grafico(df):
    st.subheader("Gráficos Dinâmicos - Iterando sobre Colunas")
    colunas_para_graficos = [col for col in df.columns if col != 'GMT-03:00' and not col.startswith('Flag')]
    if "grafico_atual" not in st.session_state:
        st.session_state.grafico_atual = 0
    def gerar_grafico(coluna):
        cores_legenda = {4: '#D72638',  0: '#348AA7'} 
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df[coluna], mode='lines',
                                 name=coluna, line=dict(color='blue'), showlegend=False))
        for flag_value, color in cores_legenda.items():
            mask = df[f'Flag_{coluna}'] == flag_value
            fig.add_trace(go.Scatter(x=df['GMT-03:00'][mask], y=df[coluna][mask], mode='markers',
                                     name=f'Flag {flag_value}', 
                                     marker=dict(color=color, size=8), visible='legendonly'))
        fig.update_layout(
            title=f"Série Temporal de {coluna}",
            yaxis_title=coluna,
            legend_title="Flag",
            showlegend=True,
            xaxis=dict(
                rangeslider=dict(visible=False),
                type='date'
            )
        )
        return fig
    coluna_atual = colunas_para_graficos[st.session_state.grafico_atual]
    fig = gerar_grafico(coluna_atual)
    st.plotly_chart(fig, use_container_width=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Anterior"):
            if st.session_state.grafico_atual > 0:
                st.session_state.grafico_atual -= 1
            else:
                st.warning("Você já está no primeiro gráfico!")
    with col2:
        if st.button("Próximo"):
            if st.session_state.grafico_atual < len(colunas_para_graficos) - 1:
                st.session_state.grafico_atual += 1
            else:
                st.warning("Você já está no último gráfico!")
def exibir_ondas_nao_direcionais(df):
    """Exibe conteúdo da aba Meteorologia"""
    st.subheader("Informações Ondas Não Direcionais")
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_grafico(df)
    elif opcao == "Tabela":
        exibir_tabela(df)
def exibir_navegacao(df):
    """Exibe botões de navegação para outras funcionalidades."""
    abas = ["Maré", "Meteorologia", "Correntes", "Ondas", "Ondas Não Direcionais"]
    st.subheader("Visualização controle de qualidade em tempo real")

    aba_selecionada = st.selectbox("Escolha uma seção:", abas)
    if aba_selecionada == "Ondas Não Direcionais":
        exibir_ondas_nao_direcionais(df)

def main():
    st.title("Visualização de Séries Temporais de Ondas Não Direcionais")
    st.markdown("""
    Este aplicativo permite visualizar séries temporais para os dados de ondas não direcionais.
    Selecione as colunas e ajuste os filtros para explorar os dados.
    """)


    df = carregar_dados()

    df=importar_e_aplicar_QC(df,parametro_para_teste)
    st.sidebar.subheader("Opções de Visualização")
    st.sidebar.write(f"Total de registros: {len(df)}")
    st.sidebar.subheader("Filtro de Data")
    min_date, max_date = df.index.min(), df.index.max()
    date_range = st.sidebar.date_input("Selecione o intervalo", [min_date, max_date], min_value=min_date, max_value=max_date)
    if len(date_range) == 2:
        
        start_date, end_date = date_range
        start_date = pd.to_datetime(start_date)  # Converte para pd.Timestamp
        end_date = pd.to_datetime(end_date)  # Converte para pd.Timestamp
        df.index = pd.to_datetime(df.index)
        # df = df[(df.index >= start_date) & (df.index <= end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
# 
        df = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
    st.sidebar.subheader("Colunas para Visualização")
    colunas_disponiveis = [col for col in df.columns if col not in ["TIMESTAMP", "RECORD"]]  # Remove "RECORD"
    colunas_selecionadas = st.sidebar.multiselect(
        "Selecione as colunas", colunas_disponiveis, default=colunas_disponiveis
    )
    if colunas_selecionadas:
        colunas_selecionadas = [col for col in colunas_selecionadas if col != 'GMT-03:00' and not col.startswith('Flag')]

        st.subheader("Dados Mais Recentes")
        ultimo_registro = df.iloc[-1]  # Obtém o último registro do DataFrame
        ultimo_timestamp = df.index[-1]  # Obtém o timestamp mais recente
        st.markdown(f"### Última Atualização: {ultimo_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
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
    if colunas_selecionadas: 
        colunas_selecionadas = [col for col in colunas_selecionadas if col != 'GMT-03:00' and not col.startswith('Flag')]
        st.table(df.head(10))  # Exibe apenas os primeiros 10 registros
        st.subheader("Gráfico de Séries Temporais")
        for coluna in colunas_selecionadas:
            fig = px.line(df, x=df.index, y=coluna, title=f"Série Temporal: {coluna}", labels={"x": "Data e Hora", "y": coluna})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione ao menos uma coluna para visualização.")
    exibir_navegacao(df)
if __name__ == "__main__":
    main()
