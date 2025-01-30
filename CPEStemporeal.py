import pandas as pd
import plotly.graph_objects as go

import streamlit as st
import plotly.express as px
from Acesso_Dados_servidor_FTP import *
from QC_OPERACIONAL_UMISAN import *

def exibir_tabela(df):
    """Exibe a tabela com os dados e inclui opção para download."""
    st.subheader("Tabela de Dados")
    
    # Filtros de data
    st.sidebar.subheader("Filtrar por Período")
    data_inicio = st.sidebar.date_input("Data Inicial", df['GMT-03:00'].min().date())
    data_fim = st.sidebar.date_input("Data Final", df['GMT-03:00'].max().date())

    if data_inicio > data_fim:
        st.error("A data inicial não pode ser posterior à data final.")
        return

    # Filtrar dados com base no período selecionado
    df_filtrado = df[(df['GMT-03:00'].dt.date >= data_inicio) & (df['GMT-03:00'].dt.date <= data_fim)]
    
    # Verificar permissão do usuário
    if st.session_state.permissao != "admin":
        # Remover colunas terminadas em "flag" para usuários comuns
        df_filtrado = df_filtrado[[col for col in df_filtrado.columns if not col.endswith("flag")]]
    
    # Exibir tabela
    st.dataframe(df_filtrado)

    # Botão para download dos dados filtrados
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="Baixar Dados",
        data=csv,
        file_name="dados_mare_filtrados.csv",
        mime="text/csv"
    )
def exibir_grafico(df):
    st.subheader("Gráficos Dinâmicos - Iterando sobre Colunas")
    
    # Lista de colunas para gráficos (excluindo 'GMT-03:00' e colunas que começam com 'Flag')
    colunas_para_graficos = [col for col in df.columns if col != 'GMT-03:00' and not col.startswith('Flag')]
    
    # Inicializar estado para rastrear o gráfico atual
    if "grafico_atual" not in st.session_state:
        st.session_state.grafico_atual = 0
    
    # Gerar o gráfico com base na coluna atual
    def gerar_grafico(coluna):
        # Configuração de cores para as flags
        cores_legenda = {4: 'red', 0: 'blue'}
        fig = go.Figure()

        # Adicionar a linha principal
        fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df[coluna], mode='lines',
                                 name=coluna, line=dict(color='blue'), showlegend=False))

        # Adicionar pontos coloridos com base nos valores de flag
        for flag_value, color in cores_legenda.items():
            mask = df[f'Flag_{coluna}'] == flag_value
            fig.add_trace(go.Scatter(x=df['GMT-03:00'][mask], y=df[coluna][mask], mode='markers',
                                     name=f'Flag {flag_value}', 
                                     marker=dict(color=color, size=8), visible='legendonly'))

        # Configurar layout do gráfico
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

    # Obter a coluna atual com base no índice
    coluna_atual = colunas_para_graficos[st.session_state.grafico_atual]
    fig = gerar_grafico(coluna_atual)
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Navegação: Anterior e Próximo
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
    def exibir_navegacao(df):
        """Exibe botões de navegação para outras funcionalidades."""

        # Abas no topo da página
        abas = ["Maré", "Meteorologia", "Correntes", "Ondas", "Ondas Não Direcionais"]
        aba_selecionada = st.selectbox("Escolha uma seção:", abas)


        if aba_selecionada == "Ondas Não Direcionais":
            exibir_ondas_nao_direcionais(df)

    df = carregar_dados()
    # df=aplicar_filtros(df, parameter_columns, dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike, dict_lt_time_and_regressao)

    # Lista de novos nomes das colunas
    parameter_columns_ondas_nao_direcionais = [
        'GMT-03:00',
        'Battery',
        # "Distancia_radar",
        "Sensor_Velki", 
        'Pressure',
        'Tide_Temperature',
        'Tide Pressure',
        'Tide_Level',
        'Sign_Height',
        'Max_Height',
        'Mean_Period',
        'Peak_Period',

        'CutOff_Freq_High',
        # 'Cutoff',
        # 'HS_256Hz',
        # 'TP_256Hz',
        # 'Tmean_calc_256Hz',
        # 'Hmax_calc_256Hz'
    ]

    df = df.drop(columns=["RECORD", 'Sensor_radar','Distancia_radar'])
    df.columns = parameter_columns_ondas_nao_direcionais

    for coluna in df.columns:
        df[f'Flag_{coluna}'] = 0
    df=importar_e_aplicar_QC(df,parametro_para_teste)

    # 

    # Mostrar informações do DataFrame
    st.sidebar.subheader("Opções de Visualização")
    st.sidebar.write(f"Total de registros: {len(df)}")
    
    # Filtro de intervalo de datas
    st.sidebar.subheader("Filtro de Data")
    min_date, max_date = df.index.min(), df.index.max()
    date_range = st.sidebar.date_input("Selecione o intervalo", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]

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
        colunas_selecionadas = [col for col in colunas_selecionadas if col != 'GMT-03:00' and not col.startswith('Flag')]

        st.table(df.head(10))  # Exibe apenas os primeiros 10 registros

        st.subheader("Gráfico de Séries Temporais")
        for coluna in colunas_selecionadas:
            fig = px.line(df, x=df.index, y=coluna, title=f"Série Temporal: {coluna}", labels={"x": "Data e Hora", "y": coluna})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione ao menos uma coluna para visualização.")
    
    exibir_navegacao(df)

# Executar a aplicação
if __name__ == "__main__":
    main()
