import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import random
import matplotlib.pyplot as plt
import plotly as plt
from streamlit_option_menu import option_menu


# sys.path.append(r'G:\Drives compartilhados\DHE_REPASSE\2024\ID00_PD_MITR-QCMO\01_Scripts\20241206_Version_008')
from Acesso_Dados_servidor_FTP import *
from QC_OPERACIONAL_UMISAN import *

# Definindo um dicionário com login, senha e permissões
usuarios = {
    "admin": {"senha": "admin123", "permissao": "admin"},
    "usuario1": {"senha": "usuario123", "permissao": "usuario"},
    "usuario2": {"senha": "senha123", "permissao": "usuario"},
}
st.set_page_config(
    page_title="Monitoramento Meteoceanográfico",
    page_icon="🌊",
    layout="wide"
)

def criar_titulo_e_descricao():
    """Exibe o título e a descrição da página inicial."""
    st.title("🌊 Monitoramento Meteoceanográfico em Tempo Real")
    st.markdown(
        "Bem-vindo ao painel de monitoramento em tempo real. Explore dados meteorológicos e oceanográficos para uma melhor compreensão das condições ambientais."
    )

def exibir_mapa_interativo():
    """Cria um mapa interativo com os sensores e suas informações."""
    st.subheader("📍 Localização das Estações")
    data = {
        "Nome": ["Estação 1", "Estação 2", "Estação 3"],
        "Latitude": [-25.0, -24.5, -24.8],
        "Longitude": [-48.0, -47.8, -47.5],
        "Velocidade do Vento (m/s)": [random.uniform(2, 10) for _ in range(3)],
        "Direção do Vento": ["NE", "S", "W"],
    }
    df = pd.DataFrame(data)
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Nome",
        hover_data=["Velocidade do Vento (m/s)", "Direção do Vento"],
        color="Velocidade do Vento (m/s)",
        color_continuous_scale="Viridis",
        zoom=6,
        height=400,
    )
    fig.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig, use_container_width=True)

def exibir_painel_destaques():
    """Exibe os destaques das condições atuais."""
    st.subheader("📊 Condições Atuais")
    cols = st.columns(4)
    cols[0].metric("🌬️ Velocidade do Vento", f"{random.uniform(2, 10):.2f} m/s")
    cols[1].metric("🧭 Direção do Vento", "NE")
    cols[2].metric("🌡️ Temperatura do Ar", f"{random.uniform(20, 30):.2f} °C")
    cols[3].metric("🌊 Altura de Ondas", f"{random.uniform(1, 3):.2f} m")

def criar_menu():
    """Cria uma faixa de navegação no topo."""
    menu = st.radio(
        "",
        options=["Início", "Sobre", "Cases", "Serviços", "Produtos", "Contato", "Login"],
        horizontal=True,
        label_visibility="collapsed",
    )
    return menu

def exibir_inicio():
    """Página inicial com informações gerais."""
    st.title("🌊 Bem-vindo ao Sistema de Monitoramento Meteoceanográfico")
    st.markdown(
        "Explore informações meteoceanográficas em tempo real para suporte a decisões estratégicas. "
        "Este sistema oferece monitoramento detalhado de condições ambientais."
    )
    # exibir_mapa_interativo()
    # exibir_painel_destaques()

def exibir_sobre():
    """Página sobre a empresa ou o sistema."""
    st.title("Sobre Nós")
    st.markdown(
        """
        Somos líderes em monitoramento meteoceanográfico, fornecendo soluções inovadoras para a coleta e análise de dados ambientais.
        Nosso objetivo é capacitar nossos clientes com informações precisas e em tempo real para suportar decisões críticas.
        """
    )
    st.image("https://via.placeholder.com/800x400", caption="Nossa missão é transformar dados em soluções.")

def exibir_cases():
    """Página de estudos de caso."""
    st.title("Nossos Cases de Sucesso")
    st.markdown(
        """
        Descubra como nossas soluções ajudaram empresas a superar desafios e otimizar operações:
        - **Case 1**: Redução de custos operacionais em 20% com monitoramento de marés.
        - **Case 2**: Previsão precisa de condições marítimas para transporte seguro.
        """
    )
    st.image("https://via.placeholder.com/800x400", caption="Impacto positivo com nossas soluções.")

def exibir_servicos():
    """Página de serviços oferecidos."""
    st.title("Nossos Serviços")
    st.markdown(
        """
        Oferecemos uma ampla gama de serviços para atender às suas necessidades:
        - **Monitoramento em Tempo Real**
        - **Análise de Dados Históricos**
        - **Integração com APIs Personalizadas**
        - **Consultoria Técnica**
        """
    )
    st.image("https://via.placeholder.com/800x400", caption="Soluções sob medida para cada cliente.")

def exibir_produtos():
    """Página de produtos."""
    st.title("Nossos Produtos")
    st.markdown(
        """
        Explore nossos produtos inovadores:
        - **Sensores Avançados**: Monitoramento preciso de condições ambientais.
        - **Plataforma Digital**: Visualização e análise de dados em tempo real.
        - **Alertas Inteligentes**: Notificações automáticas para condições críticas.
        """
    )
    st.image("https://via.placeholder.com/800x400", caption="Tecnologia de ponta ao seu alcance.")

def exibir_contato():
    """Página de contato."""
    st.title("Entre em Contato")
    st.markdown(
        """
        Quer saber mais? Estamos aqui para ajudar:
        - 📧 **E-mail**: contato@empresa.com
        - 📞 **Telefone**: (11) 1234-5678
        - 🌐 **Site**: [www.empresa.com](http://www.empresa.com)
        """
    )
    with st.form("form_contato"):
        nome = st.text_input("Seu Nome")
        email = st.text_input("Seu E-mail")
        mensagem = st.text_area("Sua Mensagem")
        enviado = st.form_submit_button("Enviar")
        if enviado:
            st.success("Mensagem enviada com sucesso!")

def exibir_login():
    """Página de login."""

    # Chamada da função principal
    if __name__ == "__main__":
        main()

def main():
    criar_titulo_e_descricao()

    # exibir_graficos_resumidos()
    # exibir_navegacao()
    
    
    # Verificar se o usuário já está autenticado (caso contrário, pede login)
    if 'usuario' not in st.session_state:
        if not login():  # Se o login falhar
            return

    # Exibe a navegação após o login
    # exibir_painel_destaques()

    exibir_mapa_interativo()
    exibir_navegacao()

# Função para autenticação
def autenticar_usuario(usuario, senha):
    """Verifica se o usuário e a senha são válidos e retorna a permissão do usuário."""
    if usuario in usuarios and usuarios[usuario]["senha"] == senha:
        return usuarios[usuario]["permissao"]
    return None

# Função para exibir o conteúdo do administrador
def exibir_conteudo_admin():
    """Exibe conteúdo exclusivo para administradores."""
    st.subheader("Você é um Administrador!")
    st.write("Exemplo de funcionalidades de administrador.")
    exibir_filtro()

# Função para exibir o conteúdo do usuário
def exibir_conteudo_usuario():
    """Exibe conteúdo para usuários comuns."""
    st.subheader("Você é um Usuário Comum!")
    st.write("Você tem acesso a funcionalidades básicas.")
    exibir_filtro()

# Função para exibir os filtros
def exibir_filtro():
    """Exibe filtros interativos para o usuário"""
    st.sidebar.subheader("Filtros de Dados")

    filtro = st.sidebar.selectbox(
        "Escolha uma Estação:",
        ["Estação 1", "Estação 2", "Estação 3"]
    )

    st.sidebar.write(f"Você escolheu: {filtro}")

# Função para exibir uma tabela de exemplo


# Função para exibir texto adicional
def exibir_texto_adicional():
    """Exibe texto explicativo adicional"""
    st.write("Aqui você pode adicionar mais informações ou instruções sobre o uso da aplicação.")
    st.write("Por exemplo, você pode explicar como os filtros funcionam ou dar dicas sobre a utilização do sistema.")

# Função para o login
def login():
    """Tela de login onde o usuário insere suas credenciais."""
    st.title("Acesso ao Sistema")
    usuario = st.text_input("Usuário:")
    senha = st.text_input("Senha:", type="password")

    if st.button("Entrar"):
        permissao = autenticar_usuario(usuario, senha)
        
        if permissao:
            st.session_state.usuario = usuario  # Armazenar o usuário na sessão
            st.session_state.permissao = permissao  # Armazenar a permissão do usuário
            st.success(f"Bem-vindo, {usuario}!")
            return True  # Login bem-sucedido
        else:
            st.error("Usuário ou senha incorretos. Tente novamente.")
            return False  # Login falhou
    return False  # Nenhuma ação de login foi feita

# Função para exibir as abas de navegação
def exibir_navegacao():
    """Exibe botões de navegação para outras funcionalidades."""

    # Abas no topo da página
    abas = ["Maré", "Meteorologia", "Correntes", "Ondas", "Ondas Não Direcionais"]
    aba_selecionada = st.selectbox("Escolha uma seção:", abas)

    if aba_selecionada == "Maré":
        exibir_mare()
    elif aba_selecionada == "Meteorologia":
        exibir_meteorologia()
    elif aba_selecionada == "Correntes":
        exibir_correntes()
    elif aba_selecionada == "Ondas":
        exibir_ondas()
    elif aba_selecionada == "Ondas Não Direcionais":
        exibir_ondas_nao_direcionais()

    # Exibe conteúdo do usuário ou admin
    if st.session_state.permissao == "admin":
        exibir_conteudo_admin()
    else:
        exibir_conteudo_usuario()
    st.subheader("🌐 Explore Mais")
    st.button("🔍 Histórico de Dados")
    # st.button("📅 Previsões")
    st.button("⚙️ Configurar Alertas")
# Funções para as abas
def exibir_mare():
    """Exibe conteúdo da aba Maré"""
    st.subheader("Informações sobre Maré")
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_grafico(df_mare)
        # exibir_grafico_mare(df_mare)
        # exibir_grafico(df_mare)

    elif opcao == "Tabela":
        exibir_tabela(df_mare)
def exibir_meteorologia():
    """Exibe conteúdo da aba Meteorologia"""
    st.subheader("Informações Meteorológicas")
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_grafico_velocidade_vento(df_meteorologia)

        exibir_grafico(df_meteorologia)
    elif opcao == "Tabela":
        exibir_tabela(df_meteorologia)
        
def exibir_correntes():
    """Exibe conteúdo da aba Correntes"""
    st.subheader("Informações sobre Correntes")
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_grafico(df_correntes)
    elif opcao == "Tabela":
        exibir_tabela(df_correntes)
def exibir_ondas():
    """Exibe conteúdo da aba Ondas"""
    st.subheader("Informações sobre Ondas")
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_grafico(df_ondas)
    elif opcao == "Tabela":
        exibir_tabela(df_ondas)    
        
def exibir_ondas_nao_direcionais():
    """Exibe as opções de gráfico ou tabela na aba Ondas Não Direcionais"""
    st.subheader("Informações sobre Ondas Não Direcionais")
    opcao = st.radio("Escolha a opção de visualização", ["Gráfico", "Tabela"])
    if opcao == "Gráfico":
        exibir_grafico(df_ondas_nao_direcionais)
    elif opcao == "Tabela":
        exibir_tabela(df_ondas_nao_direcionais)

# Simulando a função para importar dados (substitua pela função real)
def importar_dados_mare():
    
    # Definir o período de tempo
    timestamps = pd.date_range(start="2024-01-01", periods=100, freq="H")
    
    # Gerar uma variação realista de maré com base em ciclos (seno e cosseno)
    # A maré observada pode ter variações com base no ciclo lunar (aproximadamente 28 dias)
    maré_observada = 1.5 * np.sin(np.linspace(0, 2 * np.pi * (len(timestamps) / 24), len(timestamps))) + 2

    # A maré prevista pode ser um valor similar, mas com um padrão diferente ou mais suave
    maré_prevista = 1.2 * np.sin(np.linspace(0, 2 * np.pi * (len(timestamps) / 24), len(timestamps))) + 2.1

    # Maré com filtro fraco - aplicação de suavização com menor intensidade
    maré_filtro_fraco = maré_observada + np.random.normal(0, 0.2, len(timestamps))  # Suavização leve

    # Maré com filtro médio - mais suavizado com um valor mais constante
    maré_filtro_medio = maré_observada + np.random.normal(0, 0.1, len(timestamps))  # Suavização média

    # Simulação de Tide_level (nível da maré)
    Tide_level = maré_observada + np.random.normal(0, 0.3, len(timestamps))

    # Criando o DataFrame
    data = pd.DataFrame({
        'GMT-03:00': timestamps,
        "Tide_level": Tide_level,
        "maré_observada": maré_observada,
        "maré_prevista": maré_prevista,
        "maré_filtro_fraco": maré_filtro_fraco,
        "maré_filtro_medio": maré_filtro_medio,
        
        "Flag_Tide_level": [0 if i % 5 != 0 else 4 for i in range(100)],  # Flag: 0 válido, 4 inválido
        "Flag_maré_observada": [0 if i % 5 != 0 else 4 for i in range(100)],  # Flag: 0 válido, 4 inválido
        "Flag_maré_prevista": [0 if i % 5 != 0 else 4 for i in range(100)],  # Flag: 0 válido, 4 inválido
        "Flag_filtro_fraco": [0 if i % 5 != 0 else 4 for i in range(100)] , # Flag: 0 válido, 4 inválido
        "Flag_filtro_medio": [0 if i % 5 != 0 else 4 for i in range(100)]  # Flag: 0 válido, 4 inválido
        })
    return pd.DataFrame(data)

def importar_dados_onda_nao_direcional():
    data =  {
        'GMT-03:00': pd.date_range(start="2024-01-01", periods=100, freq="H"),
        "Tide_level": [1.0 + 0.5 * (i % 12) for i in range(100)],  # Simula variação de maré
        "Flag_Tide_level": [0 if i % 5 != 0 else 4 for i in range(100)],  # Flag para Tide_level
        "Wave_height": [0.8 + 0.2 * (i % 10) for i in range(100)],  # Altura de onda
        "Flag_Wave_height": [0 if i % 7 != 0 else 4 for i in range(100)],  # Flag para Wave_height
        "Wave_period": [5 + (i % 6) for i in range(100)],  # Período de onda
        "Flag_Wave_period": [0 if i % 6 != 0 else 4 for i in range(100)]  # Flag para Wave_period
    }
    return pd.DataFrame(data)

def importar_dados_ondas():
    data = {
    'GMT-03:00': pd.date_range(start="2024-01-01", periods=100, freq="H"),
    "Tide_level": [i * 0.1 for i in range(100)],
    "Flag_Tide_level": [0 if i % 5 != 0 else 4 for i in range(100)],  # Flag para Tide_level
    "Wave_height_sea": [1.2 + 0.1 * i for i in range(100)],
    "Flag_Wave_height_sea": [0 if i % 7 != 0 else 4 for i in range(100)],  # Flag para Wave_height_sea
    "Wave_height_swell": [0.5 + 0.05 * i for i in range(100)],
    "Flag_Wave_height_swell": [0 if i % 10 != 0 else 4 for i in range(100)],  # Flag para Wave_height_swell
    "Wave_period_sea": [10 + i % 5 for i in range(100)],
    "Flag_Wave_period_sea": [0 if i % 6 != 0 else 4 for i in range(100)],  # Flag para Wave_period_sea
    "Wave_period_swell": [12 + (i % 3) for i in range(100)],
    "Flag_Wave_period_swell": [0 if i % 8 != 0 else 4 for i in range(100)],  # Flag para Wave_period_swell
    }
    return pd.DataFrame(data)

def importar_dados_correntes():
    return pd.DataFrame({
        'GMT-03:00': pd.date_range(start="2024-01-01", periods=100, freq="H"),
        "Current_speed": [0.5 + 0.05 * i for i in range(100)],
        "Flag_Current_speed": [0 if i % 3 != 0 else 4 for i in range(100)],  # Flag para Current_speed
        "Current_direction": [i % 360 for i in range(100)],
        "Flag_Current_direction": [0 if i % 4 != 0 else 4 for i in range(100)],  # Flag para Current_direction
        "Heading": [0.5 + 0.05 * i for i in range(100)],
        "Pitch": [0.5 + 0.05 * i for i in range(100)],
        "Roll": [0.5 + 0.05 * i for i in range(100)],
        "Pressure(dbar)": [0.5 + 0.05 * i for i in range(100)],
        "Temperature(C)": [0.5 + 0.05 * i for i in range(100)],
        "Flag_Heading": [0 if i % 4 != 0 else 4 for i in range(100)],
        "Flag_Pitch": [0 if i % 4 != 0 else 4 for i in range(100)],
        "Flag_Roll": [0 if i % 4 != 0 else 4 for i in range(100)],
        "Flag_Pressure(dbar)": [0 if i % 4 != 0 else 4 for i in range(100)],
        "Flag_Temperature(C)": [0 if i % 4 != 0 else 4 for i in range(100)]
    })

def importar_dados_meteorologia():
    return pd.DataFrame({
        'GMT-03:00': pd.date_range(start="2024-01-01", periods=100, freq="H"),
        "Wind_speed": [2 + 0.1 * i for i in range(100)],
        "Gust_speed": [3 + 0.1 * i for i in range(100)],
        "Flag_Gust_speed":  [0 if i % 2 != 0 else 4 for i in range(100)],
        "Flag_Wind_speed": [0 if i % 3 != 0 else 4 for i in range(100)],  # Flag para Wind_speed
        "Wind Direction(*)": [i % 360 for i in range(100)],
        "Flag_Wind Direction(*)": [0 if i % 4 != 0 else 4 for i in range(100)],  # Flag para Wind_direction
        "Temperature(*C)": [25 + 0.05 * i for i in range(100)],
        "Flag_Temperature(*C)": [0 if i % 5 != 0 else 4 for i in range(100)],  # Flag para Temperature
        'Pressure(hPa)': [1015 - (i % 10) for i in range(100)],
        'Flag_Pressure(hPa)': [0 if i % 6 != 0 else 4 for i in range(100)],  # Flag para Pressure
        "Rain": [0.5 * (i % 3) for i in range(100)],  # Chuva simulada
        "Flag_Rain": [0 if i % 2 != 0 else 4 for i in range(100)],  # Flag para Rainfall
        "RH": [50 + (i % 50) for i in range(100)],  # Umidade Relativa simulada
        "Flag_RH": [0 if i % 3 != 0 else 4 for i in range(100)],  # Flag para RH
        'Dew_Point':[50 + (i % 50) for i in range(100)],
        "Flag_Dew_Point": [0 if i % 3 != 0 else 4 for i in range(100)],  # Flag para RH


        
    })
def grau_para_pontos_cardinais(graus):
    direcoes = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = int((graus + 22.5) // 45) % 8  # Para garantir que o valor esteja entre 0 e 7
    return direcoes[index]

# Carregar dados de Ondas Não Direcionais
df_mare = importar_dados_mare()
df_ondas=importar_dados_ondas()
df_correntes=importar_dados_correntes()
df_meteorologia=importar_dados_meteorologia()
df_ondas_nao_direcionais=importar_dados_onda_nao_direcional()


# parametro_para_teste = 'ONDAS' # 'CORRENTES','METEOROLOGIA','MARE','ONDAS'
# df_ondas=importar_e_aplicar_QC('ONDAS')
# df_mare=importar_e_aplicar_QC('MARE')
# df_correntes=importar_e_aplicar_QC('CORRENTES')
# df_meteorologia=importar_e_aplicar_QC('METEOROLOGIA')


# Função para exibir gráfico
def exibir_grafico(df):
    st.subheader("Gráficos Dinâmicos - Iterando sobre Colunas")
    
    # Lista de colunas que queremos visualizar (excluindo TIMESTAMP e colunas que terminam com 'flag')
    colunas_para_graficos = [col for col in df.columns if col != 'GMT-03:00' and not col.startswith('Flag') ]
    print(colunas_para_graficos)
    # Criando um dicionário para as cores e suas respectivas legendas
    cores_legenda = {4: 'red', 0: 'blue'}
    
    for coluna in colunas_para_graficos:
        # Gerar um gráfico com linha e pontos
        fig = go.Figure()


        # Adicionar linha ao gráfico
        fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df[coluna], mode='lines', 
                                 name=coluna, line=dict(color='blue'), showlegend=False))  # Linha sem legenda

        # Adicionar pontos com cores baseadas no valor de 'flag'
        for flag_value, color in cores_legenda.items(): 
            mask = df[f'Flag_{coluna}'] == flag_value
            fig.add_trace(go.Scatter(x=df['GMT-03:00'][mask], y=df[coluna][mask], mode='markers',
                                     name=f'Flag {flag_value}', 
                                     marker=dict(color=color, size=8),visible='legendonly'))
        
        # Atualizar título, eixos e adicionar legenda
        
        fig.update_layout(
            title=f"Série Temporal de {coluna}",
            # xaxis_title='GMT-03:00',
            yaxis_title=coluna,
            legend_title="Flag",
            showlegend=True,  # Exibir a legenda
            xaxis=dict(
                rangeslider=dict(visible=False),  # Ativar o slider
                type='date'  # Configuração para dados de data/hora no eixo X
            )
        )

        # Exibir gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)

def exibir_grafico_mare(df):
    st.subheader("Gráficos de Maré - Observada, Filtro e Prevista")
    cores_legenda = {4: 'red', 0: 'blue'}

    # Verifique se as colunas necessárias estão no DataFrame
    if 'maré_observada' not in df.columns or 'maré_prevista' not in df.columns:
        st.error("O DataFrame precisa conter as colunas 'maré_observada' e 'maré_prevista'.")
        return

    # Adicionar linhas para cada tipo de maré
    fig = go.Figure()
    colunas_para_graficos = [col for col in df.columns if col == "maré_observada" and not col.startswith('Flag')]
    for coluna in colunas_para_graficos:
        
        # Linha da maré observada (linha contínua)
        fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_observada'], mode='lines', 
                                 name='Maré Observada', line=dict(color='blue')))
        for flag_value, color in cores_legenda.items():
            mask = df[f'Flag_{coluna}'] == flag_value
            fig.add_trace(go.Scatter(x=df['GMT-03:00'][mask], y=df[coluna][mask], mode='markers',
                                     name=f'Flag {flag_value}', 
                                     marker=dict(color=color, size=8)))

    # Linha da maré com filtro fraco (linha tracejada)
    fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_filtro_fraco'], mode='lines', 
                             name='Maré com Filtro Fraco', line=dict(color='green'),visible='legendonly'))

    # Linha da maré com filtro médio (linha pontilhada)
    fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_filtro_medio'], mode='lines', 
                             name='Maré com Filtro Médio', line=dict(color='orange'),visible='legendonly'))

    # Linha da maré prevista (linha sólida e cor distinta)
    fig.add_trace(go.Scatter(x=df['GMT-03:00'], y=df['maré_prevista'], mode='lines', 
                             name='Maré Prevista', line=dict(color='red'),visible='legendonly'))

    # Atualizar layout
    fig.update_layout(
        title="Série Temporal de Maré",
        # xaxis_title='GMT-03:00',
        yaxis_title="Altura da Maré (m)",
        legend_title="Tipos de Maré",
        showlegend=True,  # Exibir a legenda
        xaxis=dict(
            rangeslider=dict(visible=False),  # Ativar o slider
            type='date'  # Usar formato de data para o eixo X
        )
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)


def exibir_grafico_velocidade_vento(df):
    st.subheader("Gráfico de Velocidade do Vento e Rajada")
    


    # Criar gráfico de barras sobrepostas
    fig = go.Figure()
    # Adicionar barras para a rajada
    fig.add_trace(go.Bar(x=df['GMT-03:00'], y=df['Gust_speed'], name='Rajada',
                         marker=dict(color='orange', opacity=1)))
    # Adicionar barras para a velocidade do vento
    fig.add_trace(go.Bar(x=df['GMT-03:00'], y=df['Wind_speed'], name='Velocidade do Vento', 
                         marker=dict(color='yellow', opacity=1)))

    intervalo_6h = df[df['GMT-03:00'].dt.minute == 0].iloc[::6]  # Seleciona a cada 6 horas (em minutos)

    for i in intervalo_6h.index:
        direcao_vento = grau_para_pontos_cardinais(df['Wind Direction(*)'][i])
        fig.add_annotation(
            x=df['GMT-03:00'][i],
            y=-0.05 * max(df['Wind_speed'].max(), df['Gust_speed'].max()),  # Posiciona abaixo da barra
            text=direcao_vento,
            showarrow=False,
            font=dict(size=10, color="white"),
            align="center"
        )

    # Atualizar layout do gráfico
    fig.update_layout(
        barmode='overlay',  # Coloca as barras sobrepostas
        title="Velocidade do Vento e Rajada",
        xaxis_title='GMT-03:00',
        yaxis_title="Velocidade (m/s)",
        showlegend=True,  # Exibir legenda
        xaxis=dict(
            rangeslider=dict(visible=False),  # Desativa o range slider se não necessário
            type='date'  # Formato de data para o eixo X
        )
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Função para exibir a tabela
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
# Função principal
menu = criar_menu()

# Exibição de páginas com base no menu selecionado
if menu == "Início":
    exibir_inicio()
elif menu == "Sobre":
    exibir_sobre()
elif menu == "Cases":
    exibir_cases()
elif menu == "Serviços":
    exibir_servicos()
elif menu == "Produtos":
    exibir_produtos()
elif menu == "Contato":
    exibir_contato()
elif menu == "Login":
    exibir_login()


