from ftplib import FTP, error_perm, error_temp, error_proto, error_reply
import socket
import pandas as pd
from io import StringIO
from datetime import datetime
import matplotlib.pyplot as plt
# Configurações do servidor FTP
host = "cloud10.mmitecnologia.com.br"
port = 1322
user = "umi"
password = "MeteoceanUmi123"
directory = "/Estacao03/Processados"
delimiter = ","
column_names = ["TIMESTAMP", "Tide_Level", "Battery", "Sensor_Velki",
 "CutOff_Freq_High", "Peak_Period", "Mean_Period",
 "Max_Height", "Sign_Height", 
  "Sea_Level_filtered",
 "Residual", "Cutoff", "HS_256Hz", "TP_256Hz",
 "Tmean_calc_256Hz", "Hmax_calc_256Hz"
   
]
def fetch_dat_as_csv(host, port, user, password, directory, delimiter=",", column_names=None):
    """
    Conecta-se a um servidor FTP, acessa um diretório, baixa arquivos .dat, 
    e os converte em um DataFrame.
    """
    try:
        print(f"Tentando conectar ao servidor FTP em {host}:{port}...")
        ftp = FTP()
        ftp.connect(host=host, port=port, timeout=30)
        print(f"Conexão estabelecida com {host}:{port}. Tentando login...")
        
        ftp.login(user=user, passwd=password)
        print("Login bem-sucedido.")
        
        # Acessar o diretório especificado
        print(f"Acessando o diretório: {directory}")
        ftp.cwd(directory)
        
        # Listar arquivos no diretório
        print("Listando arquivos no diretório...")
        files = ftp.nlst()
        
        # Filtrar apenas arquivos .dat
        dat_files = [file for file in files if file.endswith('.csv')]
        
        print(f"Arquivos .dat encontrados: {dat_files}")
        
        # Lista para armazenar DataFrames
        all_dataframes = []
        
        for file in dat_files:
            print(f"Lendo conteúdo do arquivo como CSV: {file}")
            content = []
            
            def handle_binary(data):
                """Função para armazenar o conteúdo do arquivo."""
                content.append(data.decode('utf-8'))
            
            # Recuperar o arquivo diretamente como string
            ftp.retrbinary(f"RETR {file}", handle_binary)
            
            # Converter conteúdo para DataFrame (tratando como CSV, ignorando as 3 primeiras linhas)
            csv_content = "".join(content)
            df = pd.read_csv(StringIO(csv_content), delimiter=delimiter, names=column_names, skiprows=4, on_bad_lines='skip')
            all_dataframes.append(df)
        
        # Concatenar todos os DataFrames em um só
        final_df = pd.concat(all_dataframes, ignore_index=True)
        print("DataFrame final criado com sucesso.")
        
        # Encerrar a conexão
        ftp.quit()
        print("Conexão FTP encerrada com sucesso.")
        
        return final_df
    except socket.timeout:
        print("Erro: Timeout ao tentar conectar. O servidor pode estar inativo ou indisponível.")
    except socket.gaierror as e:
        print(f"Erro de DNS/Hostname: {e}. Verifique se o endereço do servidor está correto.")
    except ConnectionRefusedError:
        print("Erro: A conexão foi recusada. A porta pode estar fechada ou o servidor não está aceitando conexões.")
    except error_perm as e:
        print(f"Erro de permissão: {e}. Verifique usuário/senha ou se seu IP está bloqueado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

def verificar_tipos(dataframe, tipos_esperados):
    """
    Verifica os tipos de cada coluna no DataFrame.
    """
    problemas = {}

    for coluna, tipo_esperado in tipos_esperados.items():
        if coluna in dataframe.columns:
            # Filtrar valores que não correspondem ao tipo esperado
            valores_invalidos = dataframe[coluna][~dataframe[coluna].apply(lambda x: isinstance(x, tipo_esperado))]
            
            if not valores_invalidos.empty:
                problemas[coluna] = {
                    "tipo_esperado": tipo_esperado.__name__,
                    "valores_invalidos": valores_invalidos.tolist()[:5],  # Lista de exemplos (máximo 5)
                }
        else:
            problemas[coluna] = {"erro": "Coluna não encontrada no DataFrame"}
    
    return problemas

def plotar_serie_temporal(dataframe, columns):
    """
    Plota a série temporal para cada coluna especificada.
    """
    for col in columns:
        plt.figure(figsize=(10, 6))
        plt.plot(dataframe['TIMESTAMP'], dataframe[col], label=col)
        plt.xlabel('Data e Hora')
        plt.ylabel(col)
        plt.title(f'Série Temporal de {col}')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
def filtrar_por_horario(df, inicio,fim):
    """
    Filtra o DataFrame para manter apenas os dados dentro do intervalo de tempo especificado.
    
    :param dataframe: DataFrame com os dados
    :param inicio: Data e hora de início (formato: 'YYYY-MM-DD HH:MM:SS')
    :param fim: Data e hora de fim (formato: 'YYYY-MM-DD HH:MM:SS')
    :return: DataFrame filtrado
    """
    # Garantir que a coluna 'TIMESTAMP' está no formato datetime
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format="%Y-%m-%d %H:%M:%S", errors='coerce')

    # Filtrar os dados dentro do intervalo especificado
    filtro = (df['TIMESTAMP'] >= inicio) & (df['TIMESTAMP'] <= fim)
    return df[filtro]

def exibir_ultimo_horario(dataframe):
    """
    Exibe o último horário de dado no DataFrame.
    """
    if not dataframe['TIMESTAMP'].dropna().empty:
        ultimo_horario = dataframe['TIMESTAMP'].max()
        print(f"Horário do último dado: {ultimo_horario}")
    else:
        print("A coluna 'TIMESTAMP' não contém valores válidos.")



def importar_dados_servidor_ftp():
    
    # Baixar dados via FTP
    df = fetch_dat_as_csv(host, port, user, password, directory, delimiter, column_names)
    
    # Garantir que a coluna 'TIMESTAMP' está no formato datetime
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
    inicio = "2025-01-29 10:00:00"
    # fim="2024-12-21 10:00:00"
    fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Hora atual como string

    # Filtrar o DataFrame
    df= filtrar_por_horario(df, inicio,fim)
    
    # Exibir o DataFrame filtrado
    # Definição dos tipos esperados

    
    # Lista das colunas de interesse
    # columns = [
    #     "BattV_Min", 
    #     # "Sensor_radar",
    #     # "Distancia_radar",
    #     "Sensor_Velki", 
    #     # "Pressure",
    #     # "Tide_Temperature",
    #     # "Tide_Pressure",
    #     "Tide_Level",
    #     "Sign_Height", 
    #     "Max_Height",
    #     "Mean_Period",
    #     "Peak_Period",
    #     "CutOff_Freq_High"
    # ]

# Ler o arquivo como DataFrame

# Filtrar linhas com o número correto de colunas
    # Verificar tipos e problemas
    # for coluna in columns:
    #     df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
    
    # Verificar tipos no DataFrame
    # problemas_de_tipos = verificar_tipos(df, tipos_esperados)
    
    # Exibir problemas encontrados
    # if problemas_de_tipos:
    #     print("Problemas de tipos encontrados:")
    #     for coluna, problema in problemas_de_tipos.items():
    #         print(f"\nColuna: {coluna}")
    #         for key, value in problema.items():
    #             print(f"  {key}: {value}")
    # else:
        # print("Todos os tipos estão corretos.")
    
    # Plotando séries temporais
    # zplotar_serie_temporal(df, columns)
    
    # Exibir horário do último dado
    exibir_ultimo_horario(df)
    return df
df=importar_dados_servidor_ftp()
