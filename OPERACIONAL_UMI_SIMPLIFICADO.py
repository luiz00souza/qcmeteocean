import sys
from QC_FLAGS_UMISAN import *
import json
import requests
numero_de_celulas= 20
alert_window_size= 100 #Tamanho da janela de dados para ativar o sistema de alerta
sampling_frequency = 30 # em minutos 
coluna_tempo = 'GMT-03:00'
# parametro_para_teste = 'MARE' # 'CORRENTES','METEOROLOGIA','MARE','ONDAS'

input_file_meteo = r"21663137___Over_the_last_week_2024_07_26_07_56_08_ART_1.xlsx"
input_file_ADCP = r'DEMO_AWAC_UmiSan.txt'
input_file_mare = r"PP_227_22_VALE_TUBARO_2024_04_28_16_06_59_ART_1.csv"
input_file_ondas_nao_direcionais=r"wave_parameters.csv"
parameter_columns_PNORC= ['GMT-03:00','Identifier','Data','Time','Cell number','v1', 'v2', 'v3','Speed(m/s)','Direction','Amplitude unit', 'Amplitude','A2','A3','A4','Correlation','Checksum']
parameter_columns_PNORW= ['GMT-03:00','Identifier','date','time','Spectrum basis type','Processing method','Hm0','H3','H10','Hmax','Tm02','Tp','Tz','DirTp','SprTp','Main Direction','Unidirectivity index','Mean pressure','Number of no detects','Number of bad detects','Near surface current speed','Near surface current Direction','error code']
parameter_columns_PNORB= ['GMT-03:00', 'Identifier','Date','Time','Spectrum basis type','Processing method','Frequency low','Frequency high','Hm0','Tm02','Tp','DirTp', 'SprTp','Main Direction','Error code']
parameter_columns_PNORI= ['GMT-03:00','Identifier','Instrument type','Head ID','Number of beams','Number of cells','Blanking(m)','Cell size(m)','Checksum']
parameter_columns_PNORS= ['GMT-03:00','Identifier','Date','Time','Error code','Status Code','Battery','Sound Speed','Heading','Pitch','Roll','Pressure(dbar)','Temperature(C)','Analog Input 1','Checksum']

parameter_columns_mare = [
    'GMT-03:00', 
    'Pressure_S1',
    'Pressure_S2'
    ]
parameter_columns_meteo= [
    'GMT-03:00',
    'Pressure(hPa)', 
    'Rain', 
    'Wind Direction(*)',
    'Gust Speed(m/s)',
    'Wind Speed(m/s)', 
    'Dew Point',
    'RH(%)',
    'Temperature(*C)'
    ]
parameter_columns_correntes=[
    'GMT-03:00',
    'Battery',
    'Heading',
    'Pitch',
    'Roll',
    'Pressure(dbar)',
    'Temperature(C)',
    ]

parameter_columns_ondas = [
    'GMT-03:00',  # Data e hora no fuso horário GMT-03:00 (horário de Brasília ou outro fuso horário local),
    'Hm0',  # Altura significativa das ondas (m), média das maiores 1/3 das ondas em um período de tempo
    'Hmax',  # Altura máxima das ondas (m), a maior altura registrada das ondas em um período de tempo
    'Hm0_sea',  # Altura significativa das ondas no mar (m)
    'Hm0_swell',  # Altura significativa das ondas na ondulação (m),
    'Tm02',  # Período médio de onda (s), tempo médio entre duas ondas consecutivas
    'Tp',  # Período de pico das ondas (s), o período associado à maior energia no espectro de ondas
    'Tp_sea',  # Período de pico das ondas no mar (s)
    'Tp_swell',  # Período de pico das ondas na ondulação (s),
    'DirTp',  # Direção do período de pico das ondas (graus), direção de propagação das ondas associadas ao Tp
    'DirTp_sea',  # Direção do período de pico das ondas no mar (graus)
    'DirTp_swell',  # Direção do período de pico das ondas na ondulação (graus)
    'Main Direction',  # Direção principal das ondas (graus), direção predominante das ondas
    'Main Direction_sea',  # Direção principal das ondas no mar (graus)
    'Main Direction_swell',  # Direção principal das ondas na ondulação (graus)
    'Mean pressure',  # Pressão média (não especificada)
    # 'Blanking(m)',
    # 'Cell size(m)',
    'Battery',  # Nível da bateria do sensor
    # 'Sound Speed',  # Velocidade do som na água (m/s)
    'Heading',  # Rumo ou direção da embarcação/sensor (graus)
    'Pitch',  # Inclinação do sensor em relação ao eixo horizontal (graus)
    'Roll',  # Inclinação lateral do sensor (graus)
    'Pressure(dbar)',  # Pressão medida (dbar)
    'Temperature(C)',  # Temperatura da água (°C)
]
threshold_mudanca_abrupta = {
    "amplitude": {"threshold": 50, "window": 3},
    "speed": {"threshold": 20, "window": 3},
    "direction": {"threshold": 100, "window": 4}
}
threshold_plato = {
    "amplitude": {"threshold": 1, "window": 3},
    "speed": {"threshold": 0.5, "window": 3},
    "direction": {"threshold": 3, "window": 3}
}
parameter_columns_ondas_nao_direcionais = [
    'GMT-03:00',
    'Tide_Level',

    'Battery',
    "Sensor_Velki", 
    'CutOff_Freq_High',
    'Peak_Period',
    'Mean_Period',
    'Max_Height',
    'Sign_Height',
    'Sea_Level_filtered',
    'Residual',
    'Cutoff',
    'HS_256Hz',
    'TP_256Hz',
    'Tmean_calc_256Hz',
    'Hmax_calc_256Hz'
]

dict_offset = {
    "GMT-03:00": {
        "limite_futuro_segundos": 600,   # Limite para dados futuros, em segundos
        "limite_passado_segundos": 86400 # Limite para dados passados, em segundos (86400 segundos = 1 dia)
    }
}
func_names = [
    "time_offset",
    "range_check_sensors",
    "range_check_enviroment",
    "identificar_gaps",
    "identificar_dados_nulos",
    "spike_test",
    "lt_time_series_rate_of_change",
    "teste_continuidade_tempo",
    "identificar_duplicatas_tempo",
    "verifica_dados_repetidos",
    "st_time_series_segment_shift",
    "max_min_test",
    "verificar_temperatura_vs_ponto_de_orvalho",
    "verificar_velocidade_vs_rajada",
    "verificar_altura_max_vs_sig",
    "gradiente_de_amplitude_do_sinal"
]

# Carregar o arquivo JSON
# with open(r"dicionarios.json", 'r') as file:
 #   config_data = json.load(file)
# Substitua pelo link do seu JSON no GitHub
url = "https://raw.githubusercontent.com/luiz00souza/qcmeteocean/refs/heads/luiz00souza-dashqaqc/dicionarios.json"

response = requests.get(url)

if response.status_code == 200:
    config_data = response.json()  # Carrega o JSON diretamente da resposta
else:
    print(f"Erro ao baixar o JSON: {response.status_code}")
#%%FILTRAR AS STRINGS DE CORRENTE SIG
prefix_dfs = process_txt_to_multiple_dfs(input_file_ADCP)
df_PNORI = prefix_dfs['$PNORI']
df_PNORS = prefix_dfs['$PNORS']
df_PNORC = prefix_dfs['$PNORC']
df_PNORE = prefix_dfs['$PNORE']
df_PNORW = prefix_dfs['$PNORW']
df_PNORB = prefix_dfs['$PNORB']

def aplicar_filtros(df,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao,):
    resultados = []    
    # TESTE 1: Time Offset
    df, func_name = time_offset(df,dict_offset)
    print_confiaveis(df, func_name, parameter_columns,resultados)

    #TESTE 2: Range Check Sensors
    df, func_name = range_check_sensors(df, limites_range_check,alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    #TESTE 3: Range Check Enviroment
    df, func_name = range_check_enviroment(df, limites_range_check,alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    # TESTE 4: Identificar Gaps
    df, func_name = identificar_gaps(df, sampling_frequency, parameter_columns, coluna_tempo, alert_window_size, limite_segurança=59)
    print_confiaveis(df, func_name, parameter_columns,resultados)

    #TESTE 5: Identificar dados nulos
    df, func_name = identificar_dados_nulos(df,parameter_columns,alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    # Teste 6: Spike Test
    df, func_name = spike_test(df, dict_spike,alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    # #Teste 7: LT Time series rate of change	
    df, func_name = lt_time_series_rate_of_change(df, dict_lt_time_and_regressao, alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
   
    # #Teste 8: Continuidade tempo
    df, func_name = teste_continuidade_tempo(df, limite_sigma_aceitavel_and_dict_delta_site,alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    #Teste 9: Identificar duplicatas	
    df, func_name = identificar_duplicatas_tempo(df,parameter_columns,alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    #Teste 10: Verificar dados repetidos
    df, func_name = verifica_dados_repetidos(df, limite_repeticao_dados, alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    # # # Teste 11: ST Time series segment
    df, func_name = st_time_series_segment_shift(df, st_time_series_dict,alert_window_size)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    
    # # # # Teste 12: Max Min
    df, func_name = max_min_test(df, dict_max_min_test)
    print_confiaveis(df, func_name, parameter_columns,resultados)
    if parametro_para_teste == 'METEOROLOGIA':

        #TESTE 13: Temperatura vs Ponto de orvalho	ok, substituir o ponto de orvalho caso seja maior que a temperatura, ou null,  = 0, etc.
        df, func_name = verificar_temperatura_vs_ponto_de_orvalho(df,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns,resultados)
    
        #TESTE 14: Velocidade vs rajada
        df, func_name = verificar_velocidade_vs_rajada(df,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns,resultados)
    if parametro_para_teste == 'ONDAS':    
    #     # TESTE 15: Verificar altura max vs sig	
        df, func_name =verificar_altura_max_vs_sig(df,Hs='Hm0',Hmax='Hmax')
        print_confiaveis(df, func_name, parameter_columns,resultados)
    if parametro_para_teste == 'ONDAS_NAO_DIRECIONAIS':    
        # TESTE 15: Verificar altura max vs sig	
        df, func_name =verificar_altura_max_vs_sig(df,Hs='HS_256Hz',Hmax='Hmax_calc_256Hz')
        print_confiaveis(df, func_name, parameter_columns,resultados)    
    
    if parametro_para_teste == 'CORRENTES':
    
        #TESTE 16: SIGNAL ADCP GRADIENT
        df, func_name =gradiente_de_amplitude_do_sinal(df)
        print_confiaveis(df, func_name, parameter_columns,resultados)
        # 
        #Teste 17: Detectar platos verticais
        df, func_name = detectar_platos(df, threshold_plato, categorias=["amplitude", "speed", "direction"])
        print_confiaveis(df, func_name, parameter_columns,resultados)
        
        # #Teste 18: Taxa de mudanca vertical
        df, func_name = taxa_de_mudanca_vertical(df, threshold_mudanca_abrupta, categorias=["amplitude", "speed", "direction"])
        print_confiaveis(df, func_name, parameter_columns,resultados)
    df_resultados = pd.DataFrame(resultados)

    return df,df_resultados

  

lista_sensores = [
    'CORRENTES', 
    'METEOROLOGIA',
    'MARE',
    'ONDAS',
    'ONDAS_NAO_DIRECIONAIS'
    ]
todos_os_resultados = []

for parametro_para_teste in lista_sensores:
    limites_range_check = config_data[parametro_para_teste]["limites_range_check"]
    dict_spike = config_data[parametro_para_teste]["dict_spike"]
    limite_sigma_aceitavel_and_dict_delta_site = config_data[parametro_para_teste]["limite_sigma_aceitavel_and_dict_delta_site"]
    limite_repeticao_dados = config_data[parametro_para_teste]["limite_repeticao_dados"]
    dict_lt_time_and_regressao = config_data[parametro_para_teste]["dict_lt_time_and_regressao"]
    st_time_series_dict = config_data[parametro_para_teste]["st_time_series_dict"]
    dict_max_min_test = config_data[parametro_para_teste]["dict_max_min_test"]
    limites_range_check = config_data[parametro_para_teste]["limites_range_check"]

        #%% IMPORTAR DADOS DE CORRENTE
    if parametro_para_teste == 'CORRENTES':
        sampling_frequency = 30 # em minutos 
        parameter_columns=parameter_columns_correntes
        df_correntes,parameter_columns=importar_dados_corrente_string_ADCP(df_PNORC,df_PNORI,df_PNORS,parameter_columns_PNORC,parameter_columns_PNORI,parameter_columns_PNORS,parameter_columns)
        df_correntes,resultados= aplicar_filtros(df_correntes,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_correntes
    #%% IMPORTAR DADOS METEO
    if parametro_para_teste == 'METEOROLOGIA':
        sampling_frequency = 10 # em minutos 
        parameter_columns=parameter_columns_meteo
        df_meteo, nomes_colunas = import_df_meteo(input_file_meteo, nomes_colunas=parameter_columns_meteo)
        df_meteo,resultados= aplicar_filtros(df_meteo,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_meteo
    #%% IMPORTAR DADOS MARE
    if parametro_para_teste == 'MARE':
        sampling_frequency = 5 # em minutos 
        parameter_columns=parameter_columns_mare
        df_tide,nomes_colunas= import_df_mare(input_file_mare, nomes_colunas=parameter_columns_mare)
        df_tide,resultados= aplicar_filtros(df_tide,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_tide
    #%%IMPORTAR DADOS ONDAS
    if parametro_para_teste == 'ONDAS':
        sampling_frequency = 30 # em minutos 
        parameter_columns=parameter_columns_ondas
        df_ondas = process_wave_data(df_PNORW, df_PNORB, df_PNORI, df_PNORS,parameter_columns_PNORW, parameter_columns_PNORB, parameter_columns_PNORI, parameter_columns_PNORS, parameter_columns_ondas)
        df_ondas,resultados= aplicar_filtros(df_ondas,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_ondas
    #%%IMPORTAR DADOS ONDAS NAO DIRECIONAIS
    if parametro_para_teste== 'ONDAS_NAO_DIRECIONAIS':
        sampling_frequency = 30 # em minutos 
        parameter_columns=parameter_columns_ondas_nao_direcionais
        df_ondas_nao_direcionais = pd.read_csv(input_file_ondas_nao_direcionais,header=1,sep=',',names=parameter_columns_ondas_nao_direcionais)
        df_ondas_nao_direcionais.rename(columns={"TIMESTAMP": "GMT-03:00"}, inplace=True)
        for coluna in df_ondas_nao_direcionais.columns:
            df_ondas_nao_direcionais[f'Flag_{coluna}'] = 0
        df_ondas_nao_direcionais,resultados=aplicar_filtros(df_ondas_nao_direcionais, parameter_columns, dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike, dict_lt_time_and_regressao)
        df=df_ondas_nao_direcionais
        
    df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'], errors='coerce')
    
    # plot_historical_series(df, parameter_columns) 
    # if parametro_para_teste=='CORRENTES': 
    #     gerar_grafico_gradiente_vertical(df, linha_escolhida=0, coluna_escolhida='speed(m/s)')
    #     gerar_grafico_gradiente_vertical(df, linha_escolhida=0, coluna_escolhida='amplitude')
    resultados["parameter_column"] = parametro_para_teste  

    todos_os_resultados.append(resultados)
todos_os_resultados = pd.concat(todos_os_resultados, ignore_index=True)
# todos_os_resultados.to_csv(r"C:\Users\campo\Desktop\matriz.csv", index=False,sep=",")
#%%







