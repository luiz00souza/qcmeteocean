import streamlit as st
import pandas as pd
import plotly.express as px
from utide import solve, reconstruct
import numpy as np
from scipy.signal import butter, filtfilt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from OPERACIONAL_UMI_SIMPLIFICADO import *

def calcular_metricas(verdadeiro, previsto):
    mae = mean_absolute_error(verdadeiro, previsto)
    rmse = np.sqrt(mean_squared_error(verdadeiro, previsto))
    r2 = r2_score(verdadeiro, previsto)
    mape = np.mean(np.abs((verdadeiro - previsto) / verdadeiro)) * 100
    return mae, rmse, r2, mape

def processar_dados(df, time_col, height_col):
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col, height_col])
    df = df.sort_values(by=time_col)
    return df
def carregar_e_processar_csv(df, time_col, height_col):
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col, height_col])
    df = df.sort_values(by=time_col)
    return df

def calcular_intervalo(df, time_col):
    df['delta_t'] = df[time_col].diff().dt.total_seconds()
    avg_delta_t = df['delta_t'].mean()
    df = df.drop(columns=['delta_t'])
    return avg_delta_t
def aplicar_filtro(df, height_col, tipo_filtro, sampling_interval):
    Wc_fraco = 0.000224014336917  # Frequência de corte para filtro fraco (em Hz)
    Wc_medio = 0.0000224014336917  # Frequência de corte para filtro médio (em Hz)
    tipo_filtro = tipo_filtro.lower()
    if tipo_filtro == 'fraco':
        cutoff_freq = Wc_fraco
    elif tipo_filtro == 'médio':
        cutoff_freq = Wc_medio
    else:
        raise ValueError("Tipo de filtro inválido. Escolha 'Fraco' ou 'Médio'.")
    nyquist_freq = 1 / (2 * sampling_interval)
    normalized_cutoff = cutoff_freq / nyquist_freq
    if not (0 < normalized_cutoff < 1):
        raise ValueError(
            f"Erro: frequência de corte normalizada ({normalized_cutoff}) "
            f"deve estar entre 0 e 1. Verifique o intervalo de amostragem."
        )
    order = 4
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, df[height_col].values)
    return filtered_data

def reindex_time_gaps(df,time_col, avg_delta_t):
    coluna_tempo=time_col
    time_col = pd.to_datetime(df[coluna_tempo], errors='coerce')
    df[coluna_tempo] = time_col  # Atualiza no DataFrame
    # coluna_tempo='Time, GMT-03:00'
    
    df = df.dropna(subset=[coluna_tempo])
    freq = f"{round(avg_delta_t)}S"  # Frequência em segundos
    df = df.set_index(coluna_tempo)
    full_time_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq=freq)
    df = df.reindex(full_time_range)
    df.index.name = coluna_tempo  # Renomeia o índice para manter a consistência
    return df

def extrair_componentes(df, latitude, time_col, filtered_col):
    maior_bloco = encontrar_maior_bloco(df, filtered_col)
    maior_bloco[time_col] = pd.to_datetime(maior_bloco[time_col], errors='coerce')

    time_dt = maior_bloco[time_col].dt.to_pydatetime()
    coef = solve(time_dt, maior_bloco[filtered_col].values, lat=latitude, method='ols')
    return coef
def encontrar_maior_bloco(df, col):
    mask_valid = df[col].notna()
    df['grupo'] = (mask_valid != mask_valid.shift()).cumsum()
    valid_groups = df.loc[mask_valid, 'grupo']
    group_sizes = valid_groups.value_counts()
    maior_grupo = group_sizes.idxmax()
    df_maior_bloco = df[df['grupo'] == maior_grupo].drop(columns='grupo')
    return df_maior_bloco
def ajustar_offset_gaps(df, time_col, height_col, predicted_col):
    mask_nan = df[height_col].isna()
    df['grupo'] = (mask_nan != mask_nan.shift()).cumsum()  # Agrupar por regiões contínuas de NaN
    for grupo in df['grupo'].unique():
        bloco = df[df['grupo'] == grupo]
        if len(bloco) < 4:
            df.loc[bloco.index, 'Altura Preenchida'] = np.nan  # Definir os valores como NaN

            df.loc[bloco.index, 'Altura Preenchida'] = df['Altura Preenchida'].interpolate(method='linear', limit_direction='both')
        else:
            if bloco[height_col].isna().all():
                idx_inicio = bloco.index[0]
                idx_fim = bloco.index[0] - pd.Timedelta(seconds=300)
                if idx_inicio in df.index and idx_fim in df.index:
                    altura_fim = df.loc[idx_fim, height_col]
                    previsao_inicio = df.loc[idx_inicio, predicted_col]    
                    offset = altura_fim - previsao_inicio
                    df.loc[bloco.index, predicted_col] += offset
    return df
    # df = df.drop(columns=['grupo'])
def gerar_previsao(df, coef, avg_delta_t, time_col):
    df[time_col] = df.index.to_pydatetime()
    forecast_days = 365
    time_forecast = pd.date_range(
        start=df[time_col].max(),
        periods=int(forecast_days * 24 * 3600 / avg_delta_t),
        freq=f"{int(avg_delta_t)}S"
    )
    reconstruction_forecast = reconstruct(time_forecast.to_pydatetime(), coef)
    return pd.DataFrame({
        "Tempo": time_forecast,
        "Altura Prevista": reconstruction_forecast['h']
    })
def reconstruir_mare(df, time_col, coef):
    time_dt = df.index.to_pydatetime()
    reconstruction_obs = reconstruct(time_dt, coef)
    df["Altura Prevista"] = reconstruction_obs['h']
    return df

def calcular_residuos(df, height_col):
    df["Resíduo"] = df[height_col] - df["Altura Prevista"]
    return df

#%%FUNCOES VISUAIS STREAMLIT
def selecionar_colunas(df):
    time_col = st.selectbox("Selecione a coluna de tempo", df.columns)
    height_col = st.selectbox("Selecione a coluna de altura do nivel do mar", df.columns)
    return time_col, height_col

def grafico_original(df, time_col, height_col):
    fig = px.line(
        df, 
        x=time_col, 
        y=height_col, 
        labels={time_col: "Tempo", height_col: "Altura da Maré"},
        title="Altura da Maré Original",
)
    st.plotly_chart(fig)
def grafico_comparativo(df, time_col, height_col, filtered_data_weak, filtered_data_medium):
    # Gráfico com filtros
    fig_filtered = px.line(
        df, 
        x=time_col, 
        y=[height_col, 'Filtro Fraco', 'Filtro Médio'],
        labels={time_col: "Tempo", "value": "Altura da Maré"},
        title="Comparação: Dados Reais vs Filtros (Fraco e Médio)"
    )
    st.plotly_chart(fig_filtered)
    fig_comparison = px.line(
        df, 
        x=time_col, 
        y=[height_col, "Altura Prevista","Altura Preenchida"],
        labels={time_col: "Tempo", "value": "Altura da Maré"},
        title="Maré Observada vs Prevista"
    )
    st.plotly_chart(fig_comparison)
def grafico_residuos(df, time_col):
    fig_residuals = px.line(
        df, 
        x=time_col, 
        y="Resíduo",
        labels={time_col: "Tempo", "Resíduo": "Altura Residual"},
        title="Resíduos da Maré"
    )
    st.plotly_chart(fig_residuals)
def exibir_componentes(coef,tipo_de_filtro):
    st.write(f"Componentes Harmônicas Extraídas:({tipo_de_filtro})")
    st.dataframe(pd.DataFrame({
        "Constituente": coef['name'],
        "Amplitude (m)": coef['A'],
        "Fase (°)": coef['g']
    }))
def grafico_previsao(forecast_df):
    fig_forecast = px.line(
        forecast_df, 
        x="Tempo", 
        y="Altura Prevista",
        title="Previsão de Maré para 1 Ano",
        labels={"Tempo": "Tempo", "Altura Prevista": "Altura da Maré"}
    )
    st.plotly_chart(fig_forecast)

def download_dados(df, forecast_df):
    st.download_button(
        label="Baixar Dados (CSV com previsão e resíduos)",
        data=df.to_csv(index=False),
        file_name="dados_mare_com_residuos.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Baixar Previsão (1 Ano, CSV)",
        data=forecast_df.to_csv(index=False),
        file_name="previsao_mare_1_ano.csv",
        mime="text/csv"
    )

def streamlituploadautomatico(df_tide,time_col ,height_col, latitude,tipo_de_filtro,avg_delta_t):

    st.title("Processamento e Análise de Séries Temporais")
    
    df = df_tide
    
    
    df = carregar_e_processar_csv(df, time_col, height_col)
    filtered_data_weak = aplicar_filtro(df, height_col, 'Fraco', sampling_interval=600)
    filtered_data_medium = aplicar_filtro(df, height_col, 'Médio', sampling_interval=600)
    df['Filtro Fraco'] = filtered_data_weak
    df['Filtro Médio'] = filtered_data_medium
    maior_bloco = encontrar_maior_bloco(df, tipo_de_filtro)
    df = reindex_time_gaps(df, time_col,avg_delta_t)
    coef = extrair_componentes(maior_bloco, latitude, time_col=time_col, filtered_col=tipo_de_filtro)
    df = reconstruir_mare(df, time_col, coef)
    df = calcular_residuos(df, height_col)
    forecast_df = gerar_previsao(df, coef, avg_delta_t, time_col)
    df["Altura Preenchida"] = df[height_col].combine_first(df["Altura Prevista"])
    df_ajustado = ajustar_offset_gaps(df, time_col=time_col, 
                                      height_col=height_col,
                                      predicted_col='Altura Preenchida')
    st.dataframe(df_ajustado)  # Mostra as primeiras 5 linhas
    grafico_original(df, time_col, height_col)
    grafico_comparativo(df_ajustado, time_col, height_col, filtered_data_weak, filtered_data_medium)
    exibir_componentes(coef, tipo_de_filtro)
    df_clean = df[[tipo_de_filtro, "Altura Prevista"]].dropna()
    mae_utide, rmse_utide, r2_utide, mape_utide = calcular_metricas(df_clean[tipo_de_filtro], df_clean["Altura Prevista"])

    st.write("### Avaliação dos Modelos")

    st.write(f"**UTIDE:** MAE = {mae_utide:.4f}, RMSE = {rmse_utide:.4f}, R² = {r2_utide:.4f}, MAPE = {mape_utide:.2f}%")

    st.title("Tabela de Dados")
    st.dataframe(df_ajustado.head())  # Mostra as primeiras 5 linhas
    grafico_residuos(df_ajustado, time_col)
    grafico_previsao(forecast_df)
    download_dados(df_ajustado, forecast_df)
    tid_content = df_ajustado.to_csv(index=False, sep="\t")  # Converte para formato tabulado
    st.download_button(
        label="Baixar Arquivo .tid",
        data=tid_content,
        file_name="dados_processados.tid",
        mime="text/plain"
    )
def streamlituploadmanual():

    st.title("Processamento e Análise de Séries Temporais")
    
    st.write("""
    Carregue um arquivo CSV contendo dados temporais e escolha as colunas correspondentes ao 
    tempo e à altura para gerar análises detalhadas, incluindo gráficos, tabelas e opções de download.
    """)
    uploaded_file = st.file_uploader("Carregue o arquivo CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    
        st.subheader("Selecione as colunas:")
        time_col = st.selectbox("Selecione a coluna do tempo:", df.columns, key="time_col")
        height_col = st.selectbox("Selecione a coluna da altura:", df.columns, key="height_col")
    
        # Só executa as funções após selecionar as colunas
        if time_col and height_col:
            st.success(f"Colunas selecionadas: Tempo = '{time_col}', Altura = '{height_col}'")
            # Seleção do filtro
            tipo_filtro = st.selectbox(
                "Selecione o tipo de filtro que deseja aplicar:",
                options=[f'{height_col}', "Filtro Fraco", "Filtro Médio"],
                index=0  # Default: "Sem Filtro"
            )
    
            filtro_selecionado = st.radio(
                "Escolha o tipo de filtro a ser aplicado:",
                (f'{height_col}', "Filtro Fraco", "Filtro Médio"),
            )
            latitude = st.number_input(r"Insira a latitude do local (exemplo: -21 para o Vitória/ES)", 
                               min_value=-90.0, max_value=90.0, value=-21.0, step=0.1)
    
            # Habilitar botão somente após seleção do filtro
            if filtro_selecionado:
                if st.button("Processar Dados"):
                    with st.spinner("Processando os dados..."):
                        # Processamento inicial
    
      
        
        # time_col = 'Time, GMT-03:00'
        # height_col = 'Scaled Series - Avg, Metros, TESTE_CPES SENSOR 1'
        # df=carregar_dados(r"C:\Users\campo\Downloads\CPES_OUT2024_2024_12_19_09_19_48_ART_1.csv")
        
        # df = processar_dados(df, time_col, height_col)
                        df = carregar_e_processar_csv(df, time_col, height_col)
                        tipo_de_filtro='Filtro Fraco'
                        tipo_de_filtro=filtro_selecionado
                        avg_delta_t = 300
                        filtered_data_weak = aplicar_filtro(df, height_col, 'Fraco', sampling_interval=600)
                        filtered_data_medium = aplicar_filtro(df, height_col, 'Médio', sampling_interval=600)
                        df['Filtro Fraco'] = filtered_data_weak
                        df['Filtro Médio'] = filtered_data_medium
                        maior_bloco = encontrar_maior_bloco(df, tipo_de_filtro)
                        
                        
                        # Reindexar para preencher os gaps no tempo
                        df = reindex_time_gaps(df, time_col,avg_delta_t)
                        coef = extrair_componentes(maior_bloco, latitude,time_col=time_col, filtered_col=tipo_de_filtro)
                        df = reconstruir_mare(df, time_col, coef)
                        df = calcular_residuos(df, height_col)
                        forecast_df = gerar_previsao(df, coef, avg_delta_t, time_col)
                        df["Altura Preenchida"] = df[height_col].combine_first(df["Altura Prevista"])
                        # Ajustar os offsets nos gaps
                        df_ajustado = ajustar_offset_gaps(df, time_col=time_col, 
                                                          height_col=height_col,
                                                          predicted_col='Altura Preenchida')
                        
                        grafico_original(df, time_col, height_col)
                        grafico_comparativo(df_ajustado, time_col, height_col, filtered_data_weak, filtered_data_medium)
                        exibir_componentes(coef, tipo_de_filtro)
                        st.title("Tabela de Dados")
                        st.dataframe(df_ajustado.head())  # Mostra as primeiras 5 linhas
                        
                        grafico_residuos(df_ajustado, time_col)
                        
                        grafico_previsao(forecast_df)
                        
                        download_dados(df_ajustado, forecast_df)
                        tid_content = df_ajustado.to_csv(index=False, sep="\t")  # Converte para formato tabulado
                        
                        # Botão de download para o arquivo .tid
                        st.download_button(
                            label="Baixar Arquivo .tid",
                            data=tid_content,
                            file_name="dados_processados.tid",
                            mime="text/plain"
                        )
    
    
    
    # # Configurações do GitHub
    # GITHUB_TOKEN = st.secrets["github_token"]  # Armazene o token no Streamlit Secrets
    # REPO_NAME = "luiz00souza/qcmeteocean"  # Substitua pelo nome do seu repositório
    
    # # Função para criar uma issue no GitHub
    # def create_github_issue(title, body):
    #     try:
    #         g = Github(GITHUB_TOKEN)
    #         repo = g.get_repo(REPO_NAME)
    #         issue = repo.create_issue(title=title, body=body)
    #         return issue
    #     except Exception as e:
    #         return f"Erro ao criar a issue: {e}"
    
    # # Interface do Streamlit
    # st.title("Caixa de Sugestões")
    # st.write("Envie suas sugestões para melhorar este projeto!")
    
    # # Entrada do usuário
    # suggestion = st.text_area("Escreva sua sugestão aqui:")
    # name = st.text_input("Seu nome (opcional):")
    
    # # Botão para enviar
    # if st.button("Enviar Sugestão"):
    #     if suggestion.strip():
    #         issue_title = f"Sugestão de {name or 'Anônimo'}"
    #         issue_body = suggestion
    #         result = create_github_issue(issue_title, issue_body)
    #         if isinstance(result, str):
    #             st.error(result)
    #         else:
    #             st.success(f"Sugestão enviada com sucesso! [Veja no GitHub]({result.html_url})")
    #     else:
    #         st.warning("Por favor, insira uma sugestão antes de enviar.")
            
# streamlituploadautomatico(df_tide,time_col = 'GMT-03:00',height_col = 'Pressure_S1', latitude =-21,tipo_de_filtro='Filtro Fraco',avg_delta_t = 300)# UTILIZAR PARA ARQUIVO PREDEFINIDO COM CONFIGURACOES PREDEFINIDAS

# streamlituploadmanual()# UTILIZAR PARA PREVISOES RAPIDAS, REALIZANDO O UPLOAD DE QUALQUER ARQUIVO CSV

    
