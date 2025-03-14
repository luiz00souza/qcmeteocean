import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px 
from Acesso_Dados_servidor_FTP_01 import *
from OPERACIONAL_UMI_SIMPLIFICADO import *
from previsaomare import *
import altair as alt
import json
@st.cache_data
def carregar_dados(todos_os_resultados):
    df = todos_os_resultados
    df.rename(columns={"Teste": "Filtro"}, inplace=True)
    return df

def exibir_matriz_calor(df, parametro_selecionado):
    df_filtrado = df[df['parameter_column'] == parametro_selecionado].copy()
    if not df_filtrado.empty:
        st.subheader(f"Tabela de Dados: {parametro_selecionado}")
        df_filtrado['Porcentagem Falhos'] = df_filtrado['Porcentagem Falhos'].clip(upper=100)
        matriz_calor = df_filtrado.pivot_table(
            index="Parametro", columns="Filtro", values="Porcentagem Falhos", aggfunc="mean"
        ).reset_index()
        
        
        matriz_calor_melt = matriz_calor.melt(id_vars=["Parametro"], var_name="Filtro", value_name="Porcentagem Falhos")
        chart = alt.Chart(matriz_calor_melt).mark_rect().encode(
            x='Filtro:N',
            y=alt.Y('Parametro:N', sort=alt.SortField(field='Indice Extraido', order='ascending')),
            color=alt.Color('Porcentagem Falhos:Q', scale=alt.Scale(domain=[0, 100])),
            tooltip=['Parametro', 'Filtro', 'Porcentagem Falhos']
        ).properties(
            title=f"Matriz de Calor: {parametro_selecionado}",
            width=800,
            height=500
        )
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(df_filtrado)  # Exibir dados sem a coluna auxiliar
    else:
        st.warning(f"Não há dados para {parametro_selecionado}.")

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
    # if st.session_state.permissao != "admin":
    df_filtrado = df_filtrado[[col for col in df_filtrado.columns if not col.endswith("flag")]]
    st.dataframe(df_filtrado)
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="Baixar Dados",
        data=csv,
        file_name="dados_mare_filtrados.csv",
        mime="text/csv"
    )
testes_qualidade = {
    1: ("Time Offset", 
        "Verifica se os registros de tempo estão dentro de um intervalo aceitável.",
        "Se muitos registros forem marcados como inválidos, pode haver falha na sincronização de horário ou no sistema de aquisição.",
        ["TIMESTAMP"],
        "[IOC Guide to Operational Ocean Monitoring](https://www.oceanexpert.org/document/27347)"),
    
    2: ("Range Check Sensors", 
        "Valida se os valores dos sensores estão dentro dos limites aceitáveis.",
        "Valores fora dos limites indicam possível falha do sensor, erro de calibração ou condições ambientais extremas.",
        ["Sensor_radar", "Distancia_radar", "Sensor_Velki", "Tide_Temperature", "Tide_Pressure", "Tide_Level"],
        "[IOC Guide to QC of Oceanographic Data](https://unesdoc.unesco.org/ark:/48223/pf0000121583)"),
    
    3: ("Range Check Environment", 
        "Verifica se os valores ambientais estão dentro dos limites aceitáveis.",
        "Se houver muitos valores fora dos limites, pode ser necessário revisar os limiares definidos ou verificar a integridade dos sensores.",
        ["Pressure", "Tide_Temperature"],
        "[WMO Guide to Instruments](https://library.wmo.int/index.php?lvl=notice_display&id=21428)"),
    
    4: ("Identificar Gaps", 
        "Detecta lacunas temporais nos dados devido à falta de amostras dentro da frequência definida.",
        "Se houver muitos gaps, pode indicar falhas na comunicação ou problemas operacionais na estação.",
        ["TIMESTAMP"],
        "[IOC Guide to QC of Oceanographic Data](https://unesdoc.unesco.org/ark:/48223/pf0000121583)"),
    
    5: ("Identificar Dados Nulos", 
        "Procura por valores ausentes ou inválidos, sinalizando registros problemáticos.",
        "Um alto número de dados nulos pode indicar falha no sensor ou erro no processamento.",
        ["Todas as variáveis"],
        "[ISO 19157 – Data Quality](https://www.iso.org/standard/32575.html)"),
    
    6: ("Spike Test", 
        "Detecta picos abruptos nos dados ao comparar a variação entre pontos consecutivos.",
        "Se houver muitos picos, pode indicar interferência externa no sensor ou falha nos circuitos.",
        ["Tide_Level", "Sign_Height", "Max_Height", "Mean_Period", "Peak_Period"],
        "[IOC Guide to QC of Oceanographic Data](https://unesdoc.unesco.org/ark:/48223/pf0000121583)"),
    
    7: ("Rate of Change", 
        "Verifica se a diferença entre medições consecutivas excede um limite máximo.",
        "Variações abruptas podem indicar eventos ambientais intensos ou falhas no sensor.",
        ["Tide_Level", "Sign_Height", "Max_Height"],
        "[IOC Guide to Operational Ocean Monitoring](https://www.oceanexpert.org/document/27347)"),
    
    8: ("Continuidade Temporal", 
        "Analisa a estabilidade de um parâmetro ao longo do tempo.",
        "Se houver muitas quebras na continuidade, pode ser indício de interferência externa ou falha do equipamento.",
        ["Tide_Level", "Sign_Height", "Max_Height"],
        "[ISO 19157 – Data Quality](https://www.iso.org/standard/32575.html)"),
    
    9: ("Identificar Duplicatas", 
        "Verifica se há timestamps duplicados, o que pode indicar erros na coleta dos dados.",
        "Duplicatas podem surgir por problemas na sincronização ou falhas na transmissão.",
        ["TIMESTAMP"],
        "[IOC Guide to QC of Oceanographic Data](https://unesdoc.unesco.org/ark:/48223/pf0000121583)"),
    
    10: ("Verificar Dados Repetidos", 
         "Identifica valores que permanecem inalterados por tempo excessivo.",
         "Se os dados estiverem sendo repetidos por muito tempo, pode indicar travamento do sensor.",
         ["Todas as variáveis"],
         "[ISO 19157 – Data Quality](https://www.iso.org/standard/32575.html)"),
    
    11: ("Teste de Climatologia", 
         "Compara os dados atuais com registros históricos para identificar anomalias.",
         "Se os dados estiverem fora da faixa histórica, pode indicar erro no sensor ou evento incomum.",
         ["Tide_Level", "Pressure", "Temperature"],
         "[WMO Guide to Climate Data QC](https://library.wmo.int/index.php?lvl=notice_display&id=21428)"),
    
    12: ("Teste de Persistência", 
         "Verifica se um valor permanece constante por muito tempo.",
         "Se os dados não mudam por um período longo, pode indicar travamento do sensor.",
         ["Todas as variáveis"],
         "[ISO 19157 – Data Quality](https://www.iso.org/standard/32575.html)"),
    
    13: ("Teste de Consistência Espacial", 
         "Compara valores entre estações próximas para detectar discrepâncias.",
         "Grandes diferenças podem indicar erro de calibração ou problema local.",
         ["Tide_Level", "Pressure", "Temperature"],
         "[WMO Guide to Climate Data QC](https://library.wmo.int/index.php?lvl=notice_display&id=21428)"),
    
    14: ("Teste de Consistência Temporal", 
         "Verifica se as tendências dos dados fazem sentido ao longo do tempo.",
         "Oscilações fora do esperado podem indicar erro no sensor ou evento incomum.",
         ["Tide_Level", "Pressure"],
         "[IOC Guide to QC of Oceanographic Data](https://unesdoc.unesco.org/ark:/48223/pf0000121583)"),
    
    15: ("Teste de Correlação", 
         "Analisa a relação entre variáveis que deveriam estar conectadas.",
         "Se a correlação esperada não estiver presente, pode haver erro na medição.",
         ["Sign_Height", "Mean_Period", "Peak_Period"],
         "[ISO 19157 – Data Quality](https://www.iso.org/standard/32575.html)"),
    
    16: ("Teste de Desvio-Padrão", 
         "Calcula a dispersão dos valores ao longo do tempo.",
         "Se o desvio-padrão for muito alto ou baixo, pode indicar erro no sensor.",
         ["Todas as variáveis"],
         "[ISO 19157 – Data Quality](https://www.iso.org/standard/32575.html)"),
    
    17: ("Verificação de Tendência", 
         "Identifica mudanças na tendência dos dados.",
         "Mudanças bruscas podem indicar falhas no sensor ou eventos extremos.",
         ["Tide_Level", "Pressure"],
         "[WMO Guide to Climate Data QC](https://library.wmo.int/index.php?lvl=notice_display&id=21428)"),
    
    18: ("Teste de Harmônicos", 
         "Compara os dados com modelos de maré para verificar sua consistência.",
         "Se houver grandes desvios, pode ser necessário calibrar os sensores.",
         ["Tide_Level"],
         "[IOC Guide to Tidal Analysis](https://unesdoc.unesco.org/ark:/48223/pf0000184096)"),
}

def exibir_graficos(df):
    st.subheader("Gráficos Dinâmicos")
    colunas_para_graficos = [col for col in df.columns if col != 'GMT-03:00' and not col.startswith('Flag')]
    abas = st.tabs(colunas_para_graficos)

    def gerar_grafico(coluna):
        cores_legenda = {4: '#D72638', 0: '#348AA7'} 
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
    for aba, coluna in zip(abas, colunas_para_graficos):
        with aba:
            st.plotly_chart(gerar_grafico(coluna), use_container_width=True)

def exibir_grafico_(df):
    st.subheader("Gráficos de Maré - Observada, Filtro e Prevista")
    cores_legenda = {4: 'red', 0: 'blue'}
    df['Tide_Level']=df['Pressure_S1']
    df['maré_observada']=df['Tide_Level']**0.9
    df['maré_prevista']=df['Tide_Level']**1.1
    if 'maré_observada' not in df.columns or 'maré_prevista' not in df.columns:
        st.error("O DataFrame precisa conter as colunas 'maré_observada' e 'maré_prevista'.")
        return
    fig = go.Figure()
    colunas_para_graficos = [col for col in df.columns if col == "maré_observada" and not col.startswith('Flag')]
    for coluna in colunas_para_graficos:
        fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_observada'], mode='lines', 
                                 name='Maré Observada', line=dict(color='blue')))
        for flag_value, color in cores_legenda.items():
            mask = df[f'Flag_{coluna}'] == flag_value
            fig.add_trace(go.Scatter(x=df['GMT-03:00'][mask], y=df[coluna][mask], mode='markers',
                                     name=f'Flag {flag_value}', 
                                     marker=dict(color=color, size=8)))
    fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_filtro_fraco'], mode='lines', 
                             name='Maré com Filtro Fraco', line=dict(color='green'),visible='legendonly'))
    fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_filtro_medio'], mode='lines', 
                             name='Maré com Filtro Médio', line=dict(color='orange'),visible='legendonly'))
    fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_prevista'], mode='lines', 
                             name='Maré Prevista', line=dict(color='red'),visible='legendonly'))
    fig.update_layout(
        title="Série Temporal de Maré",
        yaxis_title="Altura da Maré (m)",
        legend_title="Tipos de Maré",
        showlegend=True,  # Exibir a legenda
        xaxis=dict(
            rangeslider=dict(visible=False),  # Ativar o slider
            type='date'  # Usar formato de data para o eixo X
        )
    )
    st.plotly_chart(fig, use_container_width=True)
def formatar_dados(dados):
    """Converte um dicionário aninhado em um DataFrame formatado."""
    dados_formatados = []
    for categoria, filtros in dados.items():
        for tipo_filtro, parametros in filtros.items():
            for parametro, valores in parametros.items():
                for filtro, valor in valores.items():
                    dados_formatados.append({
                        'Categoria': categoria,
                        'Tipo de Filtro': tipo_filtro,
                        'Parâmetro': parametro,
                        'Filtro': filtro,
                        'Valor': valor
                    })
    return pd.DataFrame(dados_formatados)
def exibir_grafico_e_tabela_qc(df,opcao):
    """Exibe conteúdo da aba Maré"""
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_graficos(df)
    elif opcao == "Tabela":
        exibir_tabela(df)
def criar_grafico(df, titulo):
    """Cria um gráfico de matriz de calor usando Altair."""
    df['Porcentagem Falhos'] = df['Porcentagem Falhos'].clip(upper=100)
    def extrair_indice(valor):
        if isinstance(valor, str) and '#' in valor:
            return int(valor.split('#')[-1])
        return 0
    df.loc[:, 'Indice Extraido'] = df['Parametro'].apply(extrair_indice)
    matriz_calor = df.pivot_table(index="Parametro", columns="Filtro", values="Porcentagem Falhos", aggfunc="mean").reset_index()
    matriz_calor_melt = matriz_calor.melt(id_vars=["Parametro"], var_name="Filtro", value_name="Porcentagem Falhos")
    matriz_calor_melt.loc[:, 'Indice Extraido'] = matriz_calor_melt['Parametro'].apply(extrair_indice)
    matriz_calor_melt = matriz_calor_melt.sort_values(by="Indice Extraido", ascending=True)
    chart = alt.Chart(matriz_calor_melt).mark_rect().encode(
        x='Filtro:N',
        y=alt.Y('Parametro:N', sort=list(matriz_calor_melt['Parametro'].unique())),  # Ordenação manual baseada nos dados
        color=alt.Color('Porcentagem Falhos:Q', scale=alt.Scale(domain=[0, 100])),
        tooltip=['Parametro', 'Filtro', 'Porcentagem Falhos']
    ).properties(
        title=titulo,
        width=800,
        height=500
    )
    return chart
def graficos_comparativos(df, col_x, col_y1, col_y2):
    if col_x not in df or col_y1 not in df or col_y2 not in df:
        st.error("Uma ou mais colunas não foram encontradas no DataFrame.")
        return
    fig = px.line(df, x=col_x, y=[col_y1, col_y2], 
                  labels={"value": "Altura (m)", col_x: "Tempo"},
                  title=f"Comparação de {col_y1} e {col_y2}")
    st.plotly_chart(fig, use_container_width=True)
df_map = {
    "ONDAS_NAO_DIRECIONAIS":df_ondas_nao_direcionais,
    "METEOROLOGIA": df_meteo,
    "CORRENTES": df_correntes,
    "ONDAS": df_ondas,
    "MARE": df_tide
}
def matriz_calor_correntes(df,opcao):
    df_filtrado = df[df["parameter_column"] == opcao]
    
    df_amplitude = df_filtrado[df_filtrado['Parametro'].str.contains('Amplitude', case=False, na=False)]
    df_velocidade = df_filtrado[df_filtrado['Parametro'].str.contains('Speed', case=False, na=False)]
    df_direcao = df_filtrado[df_filtrado['Parametro'].str.contains('Direction', case=False, na=False)]
    df_outros = df_filtrado[~df_filtrado['Parametro'].str.contains('Amplitude|Speed|Direction', case=False, na=False)]

    st.subheader("Gráfico de Outros Parâmetros")
    st.altair_chart(criar_grafico(df_outros, "Matriz de Calor: Outros Parâmetros"))
    st.subheader("Tabela de Outros Parâmetros")
    st.dataframe(df_outros)

    st.subheader("Gráfico de Amplitude")
    st.altair_chart(criar_grafico(df_amplitude, "Matriz de Calor: Amplitude"))
    st.subheader("Tabela de Amplitude")
    st.dataframe(df_amplitude)
    
    st.subheader("Gráfico de Velocidade")
    st.altair_chart(criar_grafico(df_velocidade, "Matriz de Calor: Velocidade"))
    st.subheader("Tabela de Velocidade")
    st.dataframe(df_velocidade)
    
    st.subheader("Gráfico de Direção")
    st.altair_chart(criar_grafico(df_direcao, "Matriz de Calor: Direção"))
    st.subheader("Tabela de Direção")
    st.dataframe(df_direcao)
def processar_dados(df, opcao):
    """ Processa e exibe os dados de acordo com a opção selecionada. """
    df = df.set_index("GMT-03:00", drop=False)
    st.sidebar.subheader("Opções de Visualização")
    st.sidebar.write(f"Total de registros: {len(df)}")
    st.sidebar.subheader("Filtro de Data")
    min_date, max_date = df.index.min(), df.index.max()
    date_range = st.sidebar.date_input("Selecione o intervalo", [min_date, max_date], min_value=min_date, max_value=max_date)
    if len(date_range) == 2:
        start_date, end_date = map(pd.to_datetime, date_range)
        df.index = pd.to_datetime(df.index)
        df = df[(df.index >= start_date) & (df.index <= end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
    st.sidebar.subheader("Colunas para Visualização")
    colunas_disponiveis = [col for col in df.columns if col not in ["TIMESTAMP", "RECORD"]]
    colunas_selecionadas = st.sidebar.multiselect("Selecione as colunas", colunas_disponiveis, default=colunas_disponiveis)
    aba1, aba2, aba3, aba4, aba5 = st.tabs(["📄 Dados Brutos", "Dados Processados","QA/QC","Dicionários","Sobre"])
    with aba1:
        if colunas_selecionadas:
            colunas_selecionadas = [col for col in colunas_selecionadas if col != 'GMT-03:00' and not col.startswith('Flag')]
            ultimo_registro = df.iloc[-1]
            ultimo_timestamp = df.index[-1]
            st.markdown(f"### Última Atualização: {ultimo_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            num_colunas = 3
            for i in range(0, len(colunas_selecionadas), num_colunas):
                cols = st.columns(num_colunas)
                for j, coluna in enumerate(colunas_selecionadas[i:i+num_colunas]):
                    with cols[j]:
                        st.markdown(f"<div style='text-align: left; font-size: 14px;'><strong>{coluna}</strong><br>{ultimo_registro[coluna]:.2f}</div>", unsafe_allow_html=True)
            df_filtrado = df[colunas_selecionadas].head(10)
            st.dataframe(df_filtrado.style.set_properties(**{'white-space': 'nowrap'}))
            st.subheader("Gráfico de Séries Temporais")
            for coluna in colunas_selecionadas:
                fig = px.line(df, x=df.index, y=coluna, title=f"Série Temporal: {coluna}", labels={"x": "Data e Hora", "y": coluna})
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Selecione ao menos uma coluna para visualização.")

    with aba2:
        exibir_grafico_e_tabela_qc(df,opcao)
        if opcao =="MARE":
            streamlituploadautomatico(df_tide,time_col = 'GMT-03:00',height_col = 'Pressure_S1', latitude =-21,tipo_de_filtro='Filtro Médio',avg_delta_t = 300)# UTILIZAR PARA ARQUIVO PREDEFINIDO COM CONFIGURACOES PREDEFINIDAS
    with aba3: 
        st.subheader("Analise QC")
        if opcao!="CORRENTES":
            exibir_matriz_calor(df_matriz_qc,opcao)   
        if opcao=="CORRENTES":
            matriz_calor_correntes(df_matriz_qc,opcao)
    with aba4:
        json_path = r"C:\Users\campo\Desktop\dicionarios.json"
        
        with open(json_path, 'r') as file:
            dados = json.load(file)
        
        dados = formatar_dados(dados)   

        # Criar um select box com as categorias únicas
        categorias = dados["Categoria"].unique().tolist()
        categoria_selecionada = st.selectbox("Selecione uma categoria:", ["Todas"] + categorias)

        # Filtrar os dados com base na seleção (apenas para visualização e edição)
        if categoria_selecionada != "Todas":
            dadosf = dados[dados["Categoria"] == categoria_selecionada]
        else:
            dadosf = dados

        # Editar os dados filtrados
        edited_df = st.data_editor(dadosf, disabled=["Categoria", "Tipo de Filtro", "Parâmetro", "Filtro"], key="editable_table")

        # Botão para salvar as alterações
        if st.button("Salvar Alterações"):
            # Use os dados completos (não filtrados) para reconstruir o JSON
            dados_atualizados = reconstruir_json(edited_df)
            
            # Substitui as partes editadas nos dados originais
            if categoria_selecionada != "Todas":
                dados.loc[dados["Categoria"] == categoria_selecionada] = dados_atualizados
            else:
                dados = dados_atualizados

            # Salve os dados completos (não filtrados) de volta no arquivo JSON
            with open(json_path, 'w') as file:
                json.dump(dados, file, indent=4)

            st.success("Alterações salvas com sucesso!")
    with aba5:
        st.title("🔍 Testes de Qualidade de Dados Meteoceanográficos")

        # Exibe os 18 testes de forma clara
        for num, (teste, descricao, analise, parametros, normativa) in testes_qualidade.items():
            st.markdown(f"### {num}. {teste}")
            st.write(f"**Descrição:** {descricao}")
            st.write(f"**Como analisar os resultados:** {analise}")
            st.write(f"**Parâmetros analisáveis:** {', '.join(parametros)}")
            st.markdown(f"**Normativas associadas:** {normativa}")
            st.markdown("---")  # Linha separadora
df_matriz_qc = carregar_dados(todos_os_resultados)
parametros_unicos = df_matriz_qc['parameter_column'].unique()
def main():
    st.title("Visualização de Séries Temporais Meteoceanográficas")
    opcao = st.sidebar.radio(
        "Selecione o tipo de dado:",
        ("ONDAS_NAO_DIRECIONAIS", "ONDAS", "CORRENTES", "METEOROLOGIA", "MARE")
    )
    st.markdown("""
    Este aplicativo permite visualizar séries temporais para os dados meteoceanográficos.
    Selecione as colunas e ajuste os filtros para explorar os dados.
    """)
    if opcao in df_map:
        processar_dados(df_map[opcao], opcao)
        
if __name__ == "__main__":
    main()