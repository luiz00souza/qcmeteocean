#%%IMPORTAÇÃO DAS BIBLIOTECAS

import sys
# sys.path.append(r'G:\Drives compartilhados\DHE_REPASSE\2024\ID00_PD_MITR-QCMO\01_Scripts\20241206_Version_008')  # Caminho onde o arquivo .py está
from QC_FLAGS_UMISAN import *


#%% CONFIGURAÇÕES INICIAIS

numero_de_celulas= 20
alert_window_size= 100 #Tamanho da janela de dados para ativar o sistema de alerta
sampling_frequency = 30 # em minutos 
coluna_tempo = 'GMT-03:00'
parametro_para_teste = 'ONDAS_NAO_DIRECIONAIS' # 'CORRENTES','METEOROLOGIA','MARE','ONDAS'



# input_file_meteo = r"G:\Drives compartilhados\DHE_REPASSE\2024\ID00_PD_MITR-QCMO\00_Brutos\Meteo\21663137___Over_the_last_week_2024_07_26_07_56_08_ART_1.xlsx"
#input_file_ADCP = r'G:\Drives compartilhados\DHE_REPASSE\2024\ID00_PD_MITR-QCMO\00_Brutos\DEMO_AWAC_UmiSan.txt'
# input_file_mare = r"G:\Drives compartilhados\DHE_REPASSE\2024\ID00_PD_MITR-QCMO\00_Brutos\Mare\PP_227_22_VALE_TUBARO_2024_04_28_16_06_59_ART_1.csv"
#input_file_ondas_nao_direcionais=r"C:\Users\campo\Desktop\wave_parameters.csv"



#%% IDENTIFICAÇÃO DAS STRINGS
#1_Strings do adcp sig1000
parameter_columns_PNORC= ['GMT-03:00','Identifier','Data','Time','Cell number','v1', 'v2', 'v3','Speed(m/s)','Direction','Amplitude unit', 'Amplitude','A2','A3','A4','Correlation','Checksum']
parameter_columns_PNORW= ['GMT-03:00','Identifier','date','time','Spectrum basis type','Processing method','Hm0','H3','H10','Hmax','Tm02','Tp','Tz','DirTp','SprTp','Main Direction','Unidirectivity index','Mean pressure','Number of no detects','Number of bad detects','Near surface current speed','Near surface current Direction','error code']
parameter_columns_PNORB= ['GMT-03:00', 'Identifier','Date','Time','Spectrum basis type','Processing method','Frequency low','Frequency high','Hm0','Tm02','Tp','DirTp', 'SprTp','Main Direction','Error code']
parameter_columns_PNORI= ['GMT-03:00','Identifier','Instrument type','Head ID','Number of beams','Number of cells','Blanking(m)','Cell size(m)','Checksum']
parameter_columns_PNORS= ['GMT-03:00','Identifier','Date','Time','Error code','Status Code','Battery','Sound Speed','Heading','Pitch','Roll','Pressure(dbar)','Temperature(C)','Analog Input 1','Checksum']

# Parametros de interesse dados maré
parameter_columns_mare = [
    'GMT-03:00', 
    'Pressure_S1',
    'Pressure_S2', 
    # 'EstacaoID',
    # 'Logger_SN',
    # 'Battery',
    # 'Sensor_SN_S1', 
    # 'Sensor_SN_S2'
    ]
# Parametros de interesse dados meteorologicos
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

# Parametros de interesse dados correntes
parameter_columns_correntes=[
    'GMT-03:00',
    # 'Number of beams',
    # 'Number of cells',
    # 'Blanking(m)',
    # 'Cell size(m)',
    'Battery',
    # 'Sound Speed',
    'Heading',
    'Pitch',
    'Roll',
    'Pressure(dbar)',
    'Temperature(C)',
    # 'Analog Input 1'wi
    ]

# Parametros de interesse dados ondas
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

    # 'date',  # Data da medição (não especificada)
    # 'time',  # Hora da medição (não especificada)

    # 'Identifier',  # Identificador do dado (não especificado, mas pode ser uma chave única para cada observação)
    # 'Identifier_sea',  # Identificador dos dados relacionados ao estado do mar
    # 'Identifier_swell',  # Identificador dos dados relacionados à ondulação

    # 'Frequency high_sea',  # Frequência das ondas de alta frequência no mar
    # 'Frequency high_swell',  # Frequência das ondas de alta frequência na ondulação
    # 'Frequency low_sea',  # Frequência das ondas de baixa frequência no mar
    # 'Frequency low_swell',  # Frequência das ondas de baixa frequência na ondulação
    
    # 'Number of no detects',  # Número de detecções ausentes, indicaria a quantidade de dados não registrados ou não detectados
    # 'Number of bad detects',  # Número de detecções ruins, indicaria falhas ou dados de qualidade baixa
    # 'error code',  # Código de erro, para indicar falhas na medição ou no processamento dos dados
    # 'checksum',  # Somatório de verificação, utilizado para garantir a integridade dos dados transmitidos ou registrados
    
    # 'Near surface current speed',  # Velocidade da corrente próxima à superfície (m/s)
    # 'Near surface current Direction',  # Direção da corrente próxima à superfície (graus)
    
    # 'Date_swell',  # Data do dado relacionado à ondulação de swell
    # 'Error code_swell',  # Código de erro para dados relacionados à ondulação de swell
    # 'SprTp_swell',  # Período de espalhamento (s) na ondulação de swell
    # 'Time_swell',  # Hora da medição na ondulação de swell
    # 'Tm02_swell',  # Período médio das ondas na ondulação (s) de swell
    
    # 'Date_sea',  # Data do dado relacionado a ondulacao de sea
    # 'Error code_sea',  # Código de erro para dados relacionados a ondulacao de sea
    # 'SprTp_sea',  # Período de espalhamento (s) na ondulacao de sea
    # 'Time_sea',  # Hora da medição na ondulacao de sea
    # 'Tm02_sea',  # Período médio das ondas na ondulacao de sea
    
    # 'Number of beams',
    # 'Number of cells',
    # 'Analog Input 1'  # Entrada analógica 1 (não especificada, poderia ser um parâmetro de sensor adicional)
    # 'Unidirectivity index',  # Índice de unidirecionalidade, utilizado para medir a dispersão direcional das ondas

]

# parameter_columns_ondas_nao_direcionais = [
#     'GMT-03:00',
#     'Tide_Level',
#     # "Distancia_radar",
#     "Sensor_Velki", 
#     'CutOff_Freq_High',
#     'Peak_Period',
#     'Mean_Period',
#     'Max_Height',
#     'Sign_Height',
#     # 'Cutoff',
#     # 'Tide_Level_filtered',
#     # 'Residual',
#     # 'HS_256Hz',
#     # 'TP_256Hz',
#     # 'Tmean_calc_256Hz',
#     # 'Hmax_calc_256Hz'
                       
    
    
#     ]
parameter_columns_ondas_nao_direcionais = [
    'GMT-03:00',
    'Battery',
    # "Distancia_radar",
    "Sensor_Velki", 
    'Pressure',
    # 'Tide_Temperature',
    'Tide Pressure',
    'Tide_Level',
    'Sign_Height',
    'Max_Height',
    'Mean_Period',
    'Peak_Period',
    'CutOff_Freq_High',
    'Cutoff',
    'HS_256Hz',
    'TP_256Hz',
    'Tmean_calc_256Hz',
    'Hmax_calc_256Hz'
]
parameter_columns_ondas_nao_direcionais = [

"GMT-03:00", "Tide_Level", "Battery", "Sensor_Velki",
 "CutOff_Freq_High", "Peak_Period", "Mean_Period",
 "Max_Height", "Sign_Height", 
 # "Sea_Level_filtered",
 "Residual", "Cutoff", "HS_256Hz", "TP_256Hz",
 "Tmean_calc_256Hz", "Hmax_calc_256Hz"
]

#%% DICIONARIO DE LIMITES DE CONTROLE DE QUALIDADE

dict_offset = {
    "GMT-03:00": {
        "limite_futuro_segundos": 600,   # Limite para dados futuros, em segundos
        "limite_passado_segundos": 86400 # Limite para dados passados, em segundos (86400 segundos = 1 dia)
    }
}
#%%  MARÉ - DICIONARIO DE LIMITES DE CONTROLE DE QUALIDADE -
def importar_e_aplicar_QC(df,parametro_para_teste):

    if parametro_para_teste == 'MARE':
        limites_range_check = {    
        # 'Battery': {'ambiental': (0, 30), 'sensores': (0, 30)},
        'Pressure_S1': {'ambiental': (0, 30), 'sensores': (0, 30)}, 
        'Pressure_S2': {'ambiental': (0, 30), 'sensores': (0, 30)},
        }
        dict_spike = {  
        # 'Battery': {"window": 5, "threshold_factor": 3},
        'Pressure_S1': {"window": 5, "threshold_factor": 3},
        'Pressure_S2': {"window": 5, "threshold_factor": 3},
        }
        limite_sigma_aceitavel_and_dict_delta_site= {
        # 'Battery': : {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Pressure_S1': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Pressure_S2': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        }
        limite_repeticao_dados = {    
        # 'Battery': {'ambiental': (0, 30), 'sensores': (0, 30)},
        'Pressure_S1': {'fail': 160},
        'Pressure_S2': {'fail': 160},
        } 
        dict_lt_time_and_regressao={    
            
        # 'Battery': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Pressure_S1': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Pressure_S2': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        }
        st_time_series_dict = {   
        # 'Battery': {'m_points': 8, 'mean_shift_threshold': 37},
        'Pressure_S1': {'m_points': 8, 'mean_shift_threshold': 37},
        'Pressure_S2': {'m_points': 8, 'mean_shift_threshold': 37},
        }
        dict_max_min_test = {     
        # 'Battery': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Pressure_S1': {"delta": 5.0, 'm_points': 807, 'window_size': 200}, 
        'Pressure_S2': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        }   
    
    
    #%% ONDAS NAO DIRECIONAIS
    if parametro_para_teste == 'ONDAS_NAO_DIRECIONAIS':
        limites_range_check = {
    'Tide_Level': {'ambiental': (1.6, 4), 'sensores': (0, 30)},
    # "Distancia_radar": {'ambiental': (1, 4), 'sensores': (0, 30)},
    "Sensor_Velki": {'ambiental': (1.5, 4), 'sensores': (0, 30)},
    'CutOff_Freq_High': {'ambiental': (0.46, 0.7), 'sensores': (0, 30)},
    'Peak_Period': {'ambiental': (1.99, 256), 'sensores': (1.99, 256)},
    'Mean_Period': {'ambiental': (1.99, 256), 'sensores': (1.99, 256)},
    'Max_Height': {'ambiental': (0, 10), 'sensores': (0, 30)},
    'Sign_Height': {'ambiental': (0, 30), 'sensores': (0, 30)},
    # 'Cutoff': {'ambiental': (0, 0.7), 'sensores': (0, 30)},
    # 'Tide_Level_filtered': {'ambiental': (-0.005, 0.005), 'sensores': (0, 30)},
    # 'Residual': {'ambiental': (1.6, 3.5), 'sensores': (0, 30)},
    # 'HS_256Hz': {'ambiental': (0, 10), 'sensores': (0, 30)},
    # 'TP_256Hz': {'ambiental': (1.99, 256), 'sensores': (0, 30)},
    # 'Tmean_calc_256Hz': {'ambiental': (0, 30), 'sensores': (0, 30)},
    # 'Hmax_calc_256Hz': {'ambiental': (0, 10), 'sensores': (0, 10)}
    }
    dict_spike = {
    # 'Battery': {"window": 5, "threshold_factor": 3},
    'Tide_Level':{"window": 5, "threshold_factor": 3},
    # "Distancia_radar":{"window": 5, "threshold_factor": 3},
    "Sensor_Velki":{"window": 5, "threshold_factor": 3},
    'CutOff_Freq_High':{"window": 5, "threshold_factor": 3},
    'Peak_Period':{"window": 5, "threshold_factor": 3},
    'Mean_Period':{"window": 5, "threshold_factor": 3},
    'Max_Height':{"window": 5, "threshold_factor": 3},
    'Sign_Height':{"window": 5, "threshold_factor": 3},
    # 'Cutoff':{"window": 5, "threshold_factor": 3},
    # 'Tide_Level_filtered':{"window": 5, "threshold_factor": 3},
    # 'Residual':{"window": 5, "threshold_factor": 3},
    # 'HS_256Hz':{"window": 5, "threshold_factor": 3},
    # 'TP_256Hz':{"window": 5, "threshold_factor": 3},
    # 'Tmean_calc_256Hz':{"window": 5, "threshold_factor": 3},
    # 'Hmax_calc_256Hz':{"window": 5, "threshold_factor": 3},
      }
    dict_lt_time_and_regressao={
    # 'Battery': {'delta_regressao': 0.3, 'delta_lt_time': 6},
    'Tide_Level':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # "Distancia_radar":{'delta_regressao': 0.3, 'delta_lt_time': 6},
    "Sensor_Velki":{'delta_regressao': 0.3, 'delta_lt_time': 6},
    'CutOff_Freq_High':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    'Peak_Period':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    'Mean_Period':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    'Max_Height':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    'Sign_Height':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # 'Cutoff':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # 'Tide_Level_filtered':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # 'Residual':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # 'HS_256Hz':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # 'TP_256Hz':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # 'Tmean_calc_256Hz':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    # 'Hmax_calc_256Hz':{'delta_regressao': 0.3, 'delta_lt_time': 6},
    }
    limite_sigma_aceitavel_and_dict_delta_site= {
    
    # 'Battery': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    'Tide_Level':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # "Distancia_radar":{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    "Sensor_Velki":{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    'CutOff_Freq_High':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    'Peak_Period':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    'Mean_Period':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    'Max_Height':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    'Sign_Height':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # 'Cutoff':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # 'Tide_Level_filtered':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # 'Residual':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # 'HS_256Hz':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # 'TP_256Hz':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # 'Tmean_calc_256Hz':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    # 'Hmax_calc_256Hz':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
    }
    limite_repeticao_dados = {
    # 'Battery': {'fail': 160},
    'Tide_Level': {'fail': 160},
    # "Distancia_radar": {'fail': 160},
    "Sensor_Velki": {'fail': 160},
    'CutOff_Freq_High': {'fail': 160},
    'Peak_Period': {'fail': 160},
    'Mean_Period': {'fail': 160},
    'Max_Height': {'fail': 160},
    'Sign_Height': {'fail': 160},
    # 'Cutoff': {'fail': 160},
    # 'Tide_Level_filtered': {'fail': 160},
    # 'Residual': {'fail': 160},
    # 'HS_256Hz': {'fail': 160},
    # 'TP_256Hz': {'fail': 160},
    # 'Tmean_calc_256Hz': {'fail': 160},
    # 'Hmax_calc_256Hz': {'fail': 160},
    } 
    st_time_series_dict = {
    # 'Battery':{'m_points': 8, 'mean_shift_threshold': 4},
    'Tide_Level':{'m_points': 8, 'mean_shift_threshold': 4},
    # "Distancia_radar":{'m_points': 8, 'mean_shift_threshold': 4},
    "Sensor_Velki":{'m_points': 8, 'mean_shift_threshold': 4},
    'CutOff_Freq_High':{'m_points': 8, 'mean_shift_threshold': 4},
    'Peak_Period':{'m_points': 8, 'mean_shift_threshold': 4},
    'Mean_Period':{'m_points': 8, 'mean_shift_threshold': 4},
    'Max_Height':{'m_points': 8, 'mean_shift_threshold': 4},
    'Sign_Height':{'m_points': 8, 'mean_shift_threshold': 4},
    # 'Cutoff':{'m_points': 8, 'mean_shift_threshold': 4},
    # 'Tide_Level_filtered':{'m_points': 8, 'mean_shift_threshold': 4},
    # 'Residual':{'m_points': 8, 'mean_shift_threshold': 4},
    # 'HS_256Hz':{'m_points': 8, 'mean_shift_threshold': 4},
    # 'TP_256Hz':{'m_points': 8, 'mean_shift_threshold': 4},
    # 'Tmean_calc_256Hz':{'m_points': 8, 'mean_shift_threshold': 4},
    # 'Hmax_calc_256Hz':{'m_points': 8, 'mean_shift_threshold': 4},
    }
    dict_max_min_test = { 
    # 'Battery':{"delta": 13, 'm_points': 4, 'window_size': 100},
    'Tide_Level':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # "Distancia_radar":{"delta": 13, 'm_points': 4, 'window_size': 100},
    "Sensor_Velki":{"delta": 13, 'm_points': 4, 'window_size': 100},
    'CutOff_Freq_High':{"delta": 13, 'm_points': 4, 'window_size': 100},
    'Peak_Period':{"delta": 13, 'm_points': 4, 'window_size': 100},
    'Mean_Period':{"delta": 13, 'm_points': 4, 'window_size': 100},
    'Max_Height':{"delta": 13, 'm_points': 4, 'window_size': 100},
    'Sign_Height':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # 'Cutoff':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # 'Tide_Level_filtered':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # 'Residual':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # 'HS_256Hz':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # 'TP_256Hz':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # 'Tmean_calc_256Hz':{"delta": 13, 'm_points': 4, 'window_size': 100},
    # 'Hmax_calc_256Hz':{"delta": 13, 'm_points': 4, 'window_size': 100},
    }
    
    #%%  CORRENTES - DICIONARIO DE LIMITES DE CONTROLE DE QUALIDADE -
    
    if parametro_para_teste == 'CORRENTES':
        limites_range_check = {
        'Battery': {'ambiental': (0, 30), 'sensores': (0, 30)},
        # 'Blanking(m)':{'ambiental': (0, 16), 'sensores': (0, 20)},
        # 'Cell size(m)':{'ambiental': (0, 16), 'sensores': (0, 20)},
        'Heading': {'ambiental': (0, 360), 'sensores': (0, 360)},
        'Pressure(dbar)': {'ambiental': (0, 1040), 'sensores': (0, 1035)},
        'Pitch': {'ambiental': (-10, 10), 'sensores': (-90, 90)},
        'Roll': {'ambiental': (-5, 5), 'sensores': (-90, 90)},
        # 'Sound Speed':{'ambiental': (0, 1600), 'sensores': (0, 1600)},
        'Temperature(C)':{'ambiental': (-50, 50), 'sensores': (-90, 90)},
        }
        dict_spike = {
        'Battery': {"window": 5, "threshold_factor": 3},
        # 'Blanking(m)': {"window": 5, "threshold_factor": 3},
        # 'Cell size(m)': {"window": 5, "threshold_factor": 3},
        'Heading': {"window": 5, "threshold_factor": 3},
        'Pressure(dbar)': {"window": 5, "threshold_factor": 3},
        'Pitch': {"window": 5, "threshold_factor": 3},
        'Roll': {"window": 5, "threshold_factor": 3},
        # 'Sound Speed': {"window": 5, "threshold_factor": 3},
        'Temperature(C)': {"window": 5, "threshold_factor": 3},
        }
        dict_lt_time_and_regressao={
        'Battery': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Blanking(m)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Cell size(m)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Heading': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Pressure(dbar)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Pitch': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Roll':{'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Sound Speed':{'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Temperature(C)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        }
        limite_sigma_aceitavel_and_dict_delta_site= {
        
        'Battery': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Blanking(m)':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Cell size(m)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Heading':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Pressure(dbar)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Pitch': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Roll':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Sound Speed':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Temperature(C)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},   
        }
        limite_repeticao_dados = {
        'Battery': {'fail': 160},
        # 'Blanking(m)': {'fail': 160},
        # 'Cell size(m)':  {'fail': 160},
        'Heading': {'fail': 160},
        'Pressure(dbar)':  {'fail': 160},
        'Pitch':  {'fail': 160},
        'Roll': {'fail': 160},
        # 'Sound Speed': {'fail': 160},
        'Temperature(C)':  {'fail': 160},
        } 
        st_time_series_dict = {
        'Battery':{'m_points': 8, 'mean_shift_threshold': 4},
        # 'Blanking(m)': {'m_points': 8, 'mean_shift_threshold': 4},
        # 'Cell size(m)': {'m_points': 8, 'mean_shift_threshold': 4},
        'Heading': {'m_points': 8, 'mean_shift_threshold': 4},
        'Pressure(dbar)': {'m_points': 8, 'mean_shift_threshold': 4},
        'Pitch':  {'m_points': 8, 'mean_shift_threshold': 4},
        'Roll':{'m_points': 8, 'mean_shift_threshold': 4},
        # 'Sound Speed':{'m_points': 8, 'mean_shift_threshold': 4},
        'Temperature(C)':  {'m_points': 8, 'mean_shift_threshold': 4},
        }
        dict_max_min_test = { 
        'Battery':{"delta": 13, 'm_points': 4, 'window_size': 100},
        # 'Blanking(m)': {"delta": 13, 'm_points': 4, 'window_size': 100},
        # 'Cell size(m)':{"delta": 13, 'm_points': 4, 'window_size': 100},
        'Heading': {"delta": 13, 'm_points': 4, 'window_size': 100},
        'Pressure(dbar)': {"delta": 13, 'm_points': 4, 'window_size': 100},
        'Pitch':  {"delta": 13, 'm_points': 4, 'window_size': 100},
        'Roll':{"delta": 13, 'm_points': 4, 'window_size': 100},
        # 'Sound Speed':{"delta": 13, 'm_points': 4, 'window_size': 100},
        'Temperature(C)': {"delta": 13, 'm_points': 4, 'window_size': 100},
        }
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
        for i in range(1, numero_de_celulas):
            dict_lt_time_and_regressao[f'Speed(m/s)_Cell#{i}'] = {'delta_regressao': 0.3, 'delta_lt_time': 200}
            dict_lt_time_and_regressao[f'Direction_Cell#{i}'] = {'delta_regressao': 0.3, 'delta_lt_time': 200}
            dict_lt_time_and_regressao[f'Amplitude_Cell#{i}'] = {'delta_regressao': 0.3, 'delta_lt_time': 200}
        
            st_time_series_dict[f'Speed(m/s)_Cell#{i}'] = {'m_points': 8, 'mean_shift_threshold': 4}
            st_time_series_dict[f'Direction_Cell#{i}'] = {'m_points': 8, 'mean_shift_threshold': 4}
            st_time_series_dict[f'Amplitude_Cell#{i}'] = {'m_points': 8, 'mean_shift_threshold': 4}
        
            limite_repeticao_dados[f'Speed(m/s)_Cell#{i}'] = {'fail': 160, 'suspect': 100}
            limite_repeticao_dados[f'Direction_Cell#{i}'] = {'fail': 160, 'suspect': 100}
            limite_repeticao_dados[f'Amplitude_Cell#{i}'] = {'fail': 160, 'suspect': 100}
        
            dict_spike[f'Speed(m/s)_Cell#{i}'] = {"window": 5, "threshold_factor": 3}
            dict_spike[f'Direction_Cell#{i}'] = {"window": 5, "threshold_factor": 3}
            dict_spike[f'Amplitude_Cell#{i}'] = {"window": 5, "threshold_factor": 3}
            
            limites_range_check[f'Speed(m/s)_Cell#{i}'] = {'ambiental': (0, 100), 'sensores': (0, 100)}
            limites_range_check[f'Direction_Cell#{i}'] = {'ambiental': (0, 360), 'sensores': (0, 360)}
            limites_range_check[f'Amplitude_Cell#{i}'] = {'ambiental': (0, 360), 'sensores': (0, 360)}
        
            limite_sigma_aceitavel_and_dict_delta_site[f'Speed(m/s)_Cell#{i}'] = {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5}
            limite_sigma_aceitavel_and_dict_delta_site[f'Direction_Cell#{i}'] = {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5}
            limite_sigma_aceitavel_and_dict_delta_site[f'Amplitude_Cell#{i}'] = {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5}
    
    #%%  METEOROLOGIA - DICIONARIO DE LIMITES DE CONTROLE DE QUALIDADE -
    if parametro_para_teste == 'METEOROLOGIA':
        limites_range_check = {
        'Wind Speed(m/s)': {'ambiental': (0, 30), 'sensores': (0, 30)},
        'Wind Direction(*)': {'ambiental': (0, 360), 'sensores': (0, 360)},
        'Gust Speed(m/s)': {'ambiental': (0, 59), 'sensores': (0, 100)},
        #'Gust Direction(*)': {'ambiental': (0, 360), 'sensores': (0, 360)},
        # 'Battery(V)': {'ambiental': (4, 10), 'sensores': (4, 10)},
        'Temperature(*C)': {'ambiental': (4, 40), 'sensores': (4, 40)},
        'RH(%)': {'ambiental': (0, 100), 'sensores': (0, 100)},
        'Pressure(hPa)': {'ambiental': (1010, 1040), 'sensores': (1010, 1040)},
        'Rain': {'ambiental': (0, 100), 'sensores': (0, 100)},
        'Dew Point': {'ambiental': (0, 100), 'sensores': (4, 100)},
        }
        dict_spike = {  
        "Wind Speed(m/s)": {"window": 5, "threshold_factor": 3},
        # "Wind Direction(*)": {"window": 5, "threshold_factor": 3},
        "Gust Speed(m/s)": {"window": 5, "threshold_factor": 3},
        # "Gust Direction(*)": {"window": 5, "threshold_factor": 3},
        # "Battery(V)": {"window": 5, "threshold_factor": 3},
        "Temperature(*C)": {"window": 5, "threshold_factor": 3},
        # "RH(%)": {"window": 5, "threshold_factor": 3},
        "Pressure(hPa)": {"window": 5, "threshold_factor": 3},
        "Rain": {"window": 5, "threshold_factor": 3},
        'Dew Point': {"window": 5, "threshold_factor": 3},
        }
        dict_lt_time_and_regressao={
        'Wind Speed(m/s)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Gust Speed(m/s)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Wind Direction(*)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        #'Gust Direction(*)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Battery(V)': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        "Temperature(*C)": {'delta_regressao': 0.3, 'delta_lt_time': 6},
        "RH(%)": {'delta_regressao': 0.3, 'delta_lt_time': 6},
        "Pressure(hPa)": {'delta_regressao': 0.3, 'delta_lt_time': 6},
        "Rain":{'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Dew Point':{'delta_regressao': 0.3, 'delta_lt_time': 6},
        }
        limite_sigma_aceitavel_and_dict_delta_site= {    
        'Wind Speed(m/s)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Gust Speed(m/s)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Wind Direction(*)':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        #'Gust Direction(*)':{"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Battery(V)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Temperature(*C)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'RH(%)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Pressure(hPa)': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Rain': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Dew Point': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        }
        limite_repeticao_dados = {   
        'Wind Speed(m/s)': {'fail': 160},
        'Gust Speed(m/s)': {'fail': 160},
        # 'Wind Direction(*)': {'fail': 160},
        #'Gust Direction(*)': {'fail': 160},
        # 'Battery(V)': {'fail': 160},
        'Temperature(*C)': {'fail': 160},
        'RH(%)': {'fail': 160},
        'Pressure(hPa)': {'fail': 300},
        'Rain': {'fail': 10060},
        'Dew Point': {'fail': 160},
        } 
        st_time_series_dict = {
        'Wind Speed(m/s)': {'m_points': 8, 'mean_shift_threshold': 4},
        'Gust Speed(m/s)': {'m_points': 8, 'mean_shift_threshold': 4},
        # 'Wind Direction(*)': {'m_points': 8, 'mean_shift_threshold': 37},
        #'Gust Direction(*)': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Battery(V)': {'m_points': 8, 'mean_shift_threshold': 4},
        'Temperature(*C)': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'RH(%)': {'m_points': 8, 'mean_shift_threshold': 37},
        'Pressure(hPa)': {'m_points': 8, 'mean_shift_threshold': 37},
        'Rain': {'m_points': 8, 'mean_shift_threshold': 37},
        'Dew Point': {'m_points': 8, 'mean_shift_threshold': 37},
         }
        dict_max_min_test = {     
        "Gust Speed(m/s)": {"delta": 13, 'm_points': 4, 'window_size': 100},
        "Wind Speed(m/s)": {"delta": 13, 'm_points': 4, 'window_size': 100},
        # 'Wind Direction(*)': {"delta": 5.0, 'm_points': 4, 'window_size': 50},
        #'Gust Direction(*)': {"delta": 5.0, 'm_points': 4, 'window_size': 50},
        # 'Battery(V)': {"delta": 5.0, 'm_points': 4, 'window_size': 50},
        "RH(%)": {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        "Pressure(hPa)": {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # "Rain": {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Dew Point': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        }
    #%% ONDAS - DICIONARIO DE LIMITES DE CONTROLE DE QUALIDADE
    if parametro_para_teste == 'ONDAS':
        limites_range_check = {   
        'Pitch': {'ambiental': (-10, 10), 'sensores': (-90, 90)},
        'Heading': {'ambiental': (-10, 10), 'sensores': (0, 360)},
        'Roll': {'ambiental': (-5, 5), 'sensores': (-90, 90)},
        'Pressure(dbar)': {'ambiental': (0, 18), 'sensores': (0, 30)},
        'Battery' : {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Mean pressure': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Hm0': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Tp': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'DirTp': {'ambiental': (0, 2), 'sensores': (0, 5)},
         'Hmax': {'ambiental': (0, 2), 'sensores': (0, 5)},
         'Tm02': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Main Direction': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Hm0_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'DirTp_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Tp_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Hm0_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'DirTp_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        'Tp_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'H3': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'H10': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Tz': {'ambiental': (0, 2), 'sensores': (0, 5)}, 
        # 'SprTp': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Unidirectivity index': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Number of no detects': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Number of bad detects': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Near surface current speed': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Near surface current Direction': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'error code': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'checksum': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Date_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Date_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Error code_sea': {'ambiental': (0, 2), 'sensores': (0, 5)}, 
        # 'Error code_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Frequency high_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Frequency high_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Frequency low_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Frequency low_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Identifier_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Identifier_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Main Direction_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Main Direction_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Processing method_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Processing method_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Spectrum basis type_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Spectrum basis type_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'SprTp_sea': {'ambiental': (0, 2), 'sensores': (0, 5)}, 
        # 'SprTp_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Time_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Time_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Tm02_sea': {'ambiental': (0, 2), 'sensores': (0, 5)},
        # 'Tm02_swell': {'ambiental': (0, 2), 'sensores': (0, 5)},
        }
        dict_spike = {
        'Mean pressure': {"window": 5, "threshold_factor": 3},
        'Hm0': {"window": 5, "threshold_factor": 3},
        'Tp': {"window": 5, "threshold_factor": 3},
        'DirTp': {"window": 5, "threshold_factor": 3},
        'Hmax': {"window": 5, "threshold_factor": 3},
        'Tm02': {"window": 5, "threshold_factor": 3},
        'Main Direction': {"window": 5, "threshold_factor": 3},
        'Hm0_sea': {"window": 5, "threshold_factor": 3},
        'DirTp_sea': {"window": 5, "threshold_factor": 3},
        'Tp_sea': {"window": 5, "threshold_factor": 3},
        'Hm0_swell': {"window": 5, "threshold_factor": 3},
        'DirTp_swell': {"window": 5, "threshold_factor": 3},
        'Tp_swell': {"window": 5, "threshold_factor": 3},
        # 'H3': {"window": 5, "threshold_factor": 3},
        # 'H10': {"window": 5, "threshold_factor": 3},
        # 'Tz': {"window": 5, "threshold_factor": 3}, 
        # 'SprTp': {"window": 5, "threshold_factor": 3},
        # 'Unidirectivity index': {"window": 5, "threshold_factor": 3},
        # 'Number of no detects': {"window": 5, "threshold_factor": 3},
        # 'Number of bad detects': {"window": 5, "threshold_factor": 3},
        # 'Near surface current speed': {"window": 5, "threshold_factor": 3},
        # 'Near surface current Direction': {"window": 5, "threshold_factor": 3},
        # 'error code': {"window": 5, "threshold_factor": 3},
        # 'checksum': {"window": 5, "threshold_factor": 3},
        # 'Date_sea': {"window": 5, "threshold_factor": 3},
        # 'Date_swell': {"window": 5, "threshold_factor": 3},
        # 'Error code_sea': {"window": 5, "threshold_factor": 3}, 
        # 'Error code_swell': {"window": 5, "threshold_factor": 3},
        # 'Frequency high_sea': {"window": 5, "threshold_factor": 3},
        # 'Frequency high_swell': {"window": 5, "threshold_factor": 3},
        # 'Frequency low_sea': {"window": 5, "threshold_factor": 3},
        # 'Frequency low_swell': {"window": 5, "threshold_factor": 3},
        # 'Identifier_sea': {"window": 5, "threshold_factor": 3},
        # 'Identifier_swell': {"window": 5, "threshold_factor": 3},
        # 'Main Direction_sea': {"window": 5, "threshold_factor": 3},
        # 'Main Direction_swell': {"window": 5, "threshold_factor": 3},
        # 'Processing method_sea': {"window": 5, "threshold_factor": 3},
        # 'Processing method_swell': {"window": 5, "threshold_factor": 3},
        # 'Spectrum basis type_sea': {"window": 5, "threshold_factor": 3},
        # 'Spectrum basis type_swell': {"window": 5, "threshold_factor": 3},
        # 'SprTp_sea': {"window": 5, "threshold_factor": 3}, 
        # 'SprTp_swell': {"window": 5, "threshold_factor": 3},
        # 'Time_sea': {"window": 5, "threshold_factor": 3},
        # 'Time_swell': {"window": 5, "threshold_factor": 3},
        # 'Tm02_sea': {"window": 5, "threshold_factor": 3},
        # 'Tm02_swell': {"window": 5, "threshold_factor": 3},
        }
        dict_lt_time_and_regressao={ 
        'Mean pressure': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Hm0': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Tp': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'DirTp': {'delta_regressao': 0.3, 'delta_lt_time': 6},
         'Hmax': {'delta_regressao': 0.3, 'delta_lt_time': 6},
         'Tm02': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Main Direction': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Hm0_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'DirTp_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Tp_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Hm0_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'DirTp_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        'Tp_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'H3': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'H10': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Tz': {'delta_regressao': 0.3, 'delta_lt_time': 6}, 
        # 'SprTp': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Unidirectivity index': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Number of no detects': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Number of bad detects': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Near surface current speed': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Near surface current Direction': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'error code': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'checksum': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Date_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Date_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Error code_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6}, 
        # 'Error code_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Frequency high_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Frequency high_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Frequency low_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Frequency low_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Identifier_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Identifier_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Main Direction_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Main Direction_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Processing method_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Processing method_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Spectrum basis type_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Spectrum basis type_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'SprTp_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6}, 
        # 'SprTp_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Time_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Time_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Tm02_sea': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        # 'Tm02_swell': {'delta_regressao': 0.3, 'delta_lt_time': 6},
        }
        limite_sigma_aceitavel_and_dict_delta_site= {  
        'Mean pressure': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Hm0': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Tp': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'DirTp': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
         'Hmax': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
         'Tm02': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Main Direction': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Hm0_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'DirTp_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Tp_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Hm0_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'DirTp_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        'Tp_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'H3': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'H10': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Tz': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5}, 
        # 'SprTp': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Unidirectivity index': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Number of no detects': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Number of bad detects': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Near surface current speed': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Near surface current Direction': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'error code': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'checksum': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Date_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Date_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Error code_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5}, 
        # 'Error code_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Frequency high_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Frequency high_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Frequency low_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Frequency low_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Identifier_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Identifier_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Main Direction_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Main Direction_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Processing method_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Processing method_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Spectrum basis type_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Spectrum basis type_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'SprTp_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5}, 
        # 'SprTp_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Time_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Time_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Tm02_sea': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        # 'Tm02_swell': {"delta": 4, 'window': 5,"delta_site": 4, 'window_site': 5},
        } 
        limite_repeticao_dados = {        
        'Mean pressure': {'fail': 160},
        'Hm0': {'fail': 160},
        'Tp': {'fail': 160},
        'DirTp': {'fail': 160},
         'Hmax': {'fail': 160},
         'Tm02': {'fail': 160},
        'Main Direction': {'fail': 160},
        'Hm0_sea': {'fail': 160},
        'DirTp_sea': {'fail': 160},
        'Tp_sea': {'fail': 160},
        'Hm0_swell': {'fail': 160},
        'DirTp_swell': {'fail': 160},
        'Tp_swell': {'fail': 160},
        # 'H3': {'fail': 160},
        # 'H10': {'fail': 160},
        # 'Tz': {'fail': 160}, 
        # 'SprTp': {'fail': 160},
        # 'Unidirectivity index': {'fail': 160},
        # 'Number of no detects': {'fail': 160},
        # 'Number of bad detects': {'fail': 160},
        # 'Near surface current speed': {'fail': 160},
        # 'Near surface current Direction': {'fail': 160},
        # 'error code': {'fail': 160},
        # 'checksum': {'fail': 160},
        # 'Date_sea': {'fail': 160},
        # 'Date_swell': {'fail': 160},
        # 'Error code_sea': {'fail': 160}, 
        # 'Error code_swell': {'fail': 160},
        # 'Frequency high_sea': {'fail': 160},
        # 'Frequency high_swell': {'fail': 160},
        # 'Frequency low_sea': {'fail': 160},
        # 'Frequency low_swell': {'fail': 160},
        # 'Identifier_sea': {'fail': 160},
        # 'Identifier_swell': {'fail': 160},
        # 'Main Direction_sea': {'fail': 160},
        # 'Main Direction_swell': {'fail': 160},
        # 'Processing method_sea': {'fail': 160},
        # 'Processing method_swell': {'fail': 160},
        # 'Spectrum basis type_sea': {'fail': 160},
        # 'Spectrum basis type_swell': {'fail': 160},
        # 'SprTp_sea': {'fail': 160}, 
        # 'SprTp_swell': {'fail': 160},
        # 'Time_sea': {'fail': 160},
        # 'Time_swell': {'fail': 160},
        # 'Tm02_sea': {'fail': 160},
        # 'Tm02_swell': {'fail': 160},
        }
        st_time_series_dict = {   
        'Mean pressure': {'m_points': 8, 'mean_shift_threshold': 37},
        'Hm0': {'m_points': 8, 'mean_shift_threshold': 37},
        'Tp': {'m_points': 8, 'mean_shift_threshold': 37},
        'DirTp': {'m_points': 8, 'mean_shift_threshold': 37},
         'Hmax': {'m_points': 8, 'mean_shift_threshold': 37},
         'Tm02': {'m_points': 8, 'mean_shift_threshold': 37},
        'Main Direction': {'m_points': 8, 'mean_shift_threshold': 37},
        'Hm0_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        'DirTp_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        'Tp_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        'Hm0_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        'DirTp_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        'Tp_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'H3': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'H10': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Tz': {'m_points': 8, 'mean_shift_threshold': 37}, 
        # 'SprTp': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Unidirectivity index': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Number of no detects': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Number of bad detects': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Near surface current speed': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Near surface current Direction': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'error code': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'checksum': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Date_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Date_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Error code_sea': {'m_points': 8, 'mean_shift_threshold': 37}, 
        # 'Error code_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Frequency high_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Frequency high_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Frequency low_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Frequency low_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Identifier_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Identifier_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Main Direction_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Main Direction_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Processing method_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Processing method_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Spectrum basis type_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Spectrum basis type_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'SprTp_sea': {'m_points': 8, 'mean_shift_threshold': 37}, 
        # 'SprTp_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Time_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Time_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Tm02_sea': {'m_points': 8, 'mean_shift_threshold': 37},
        # 'Tm02_swell': {'m_points': 8, 'mean_shift_threshold': 37},
        }   
        dict_max_min_test = { 
        'Mean pressure': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Hm0': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Tp': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'DirTp': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Hmax': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Tm02': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Main Direction': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Hm0_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'DirTp_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Tp_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Hm0_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'DirTp_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        'Tp_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'H3': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'H10': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Tz': {"delta": 5.0, 'm_points': 807, 'window_size': 200}, 
        # 'SprTp': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Unidirectivity index': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Number of no detects': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Number of bad detects': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Near surface current speed': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Near surface current Direction': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'error code': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'checksum': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Date_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Date_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Error code_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200}, 
        # 'Error code_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Frequency high_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Frequency high_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Frequency low_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Frequency low_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Identifier_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Identifier_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Main Direction_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Main Direction_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Processing method_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Processing method_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Spectrum basis type_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Spectrum basis type_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'SprTp_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200}, 
        # 'SprTp_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Time_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Time_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Tm02_sea': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        # 'Tm02_swell': {"delta": 5.0, 'm_points': 807, 'window_size': 200},
        }

    #%%FILTRAR AS STRINGS DE CORRENTE SIG
    # prefix_dfs = process_txt_to_multiple_dfs(input_file_ADCP)
    # df_PNORI = prefix_dfs['$PNORI']
    # df_PNORS = prefix_dfs['$PNORS']
    # df_PNORC = prefix_dfs['$PNORC']
    # df_PNORE = prefix_dfs['$PNORE']
    # df_PNORW = prefix_dfs['$PNORW']
    # df_PNORB = prefix_dfs['$PNORB']
    
    
    
    def aplicar_filtros(df,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao,):
        #TESTE 1: Time Offset
        df, func_name = time_offset(df,dict_offset)
        print_confiaveis(df, func_name, parameter_columns)
        
        #TESTE 2: Range Check Sensors
        df, func_name = range_check_sensors(df, limites_range_check,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
        
        #TESTE 3: Range Check Enviroment
        df, func_name = range_check_enviroment(df, limites_range_check,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
        
        #TESTE 4: Identificar Gaps
        # df, func_name = identificar_gaps(df, sampling_frequency, parameter_columns, coluna_tempo, alert_window_size, limite_segurança=59)
        # print_confiaveis(df, func_name, parameter_columns)
    
        # #TESTE 5: Identificar dados nulos
        df, func_name = identificar_dados_nulos(df,parameter_columns,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
        
        # #Teste 6: Spike Test
        df, func_name = spike_test(df, dict_spike,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
        
        # #Teste 7: LT Time series rate of change	
        df, func_name = lt_time_series_rate_of_change(df, dict_lt_time_and_regressao, alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
       
        # #Teste 8: Continuidade tempo
        df, func_name = teste_continuidade_tempo(df, limite_sigma_aceitavel_and_dict_delta_site,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
        
        # #Teste 9: Identificar duplicatas	
        df, func_name = identificar_duplicatas_tempo(df,parameter_columns,alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
        
        # #Teste 10: Verificar dados repetidos
        df, func_name = verifica_dados_repetidos(df, limite_repeticao_dados, alert_window_size)
        print_confiaveis(df, func_name, parameter_columns)
        
        # # Teste 11: ST Time series segment
        df, func_name = st_time_series_segment_shift(df, st_time_series_dict,alert_window_size)
        print_confiaveis(df, func_name, st_time_series_dict)
        
        # # Teste 12: Max Min
        df, func_name = max_min_test(df, dict_max_min_test)
        print_confiaveis(df, func_name, parameter_columns)
        if parametro_para_teste == 'METEOROLOGIA':
    
            #TESTE 13: Temperatura vs Ponto de orvalho	ok, substituir o ponto de orvalho caso seja maior que a temperatura, ou null,  = 0, etc.
            df, func_name = verificar_temperatura_vs_ponto_de_orvalho(df,alert_window_size)
            print_confiaveis(df, func_name, parameter_columns)
        
            #TESTE 14: Velocidade vs rajada
            df, func_name = verificar_velocidade_vs_rajada(df,alert_window_size)
            print_confiaveis(df, func_name, parameter_columns)
        # if parametro_para_teste == 'ONDAS' or parametro_para_teste == 'ONDAS_NAO_DIRECIONAIS':    
        #     #TESTE 15: Verificar altura max vs sig	
        #     df, func_name =verificar_altura_max_vs_sig(df,Hs=df['HS_256Hz'],Hmax=df['Hmax_calc_256Hz'])
        #     print_confiaveis(df, func_name, parameter_columns)
        
        if parametro_para_teste == 'CORRENTES':
        
            #TESTE 16: SIGNAL ADCP GRADIENT
            df, func_name =gradiente_de_amplitude_do_sinal(df)
            # print_confiaveis(df, func_name, parameter_columns)
            # 
            #Teste 17: Detectar platos verticais
            df, func_name = detectar_platos(df, threshold_plato, categorias=["amplitude", "speed", "direction"])
            # print_confiaveis(df, func_name, parameter_columns)
            
            # #Teste 18: Taxa de mudanca vertical
            df, func_name = taxa_de_mudanca_vertical(df, threshold_mudanca_abrupta, categorias=["amplitude", "speed", "direction"])
            # print_confiaveis(df, func_name, parameter_columns)
       
        # # Temperatura do bulbo umido x temperatura	pendente
    
        # # % de beams bom para cada profundidade	pendente 
        return df
        pass
    
    #%% IMPORTAR DADOS DE CORRENTE
    
    
    if parametro_para_teste == 'CORRENTES':
        parameter_columns=parameter_columns_correntes
        df_correntes,parameter_columns=importar_dados_corrente_string_ADCP(df_PNORC,df_PNORI,df_PNORS,parameter_columns_PNORC,parameter_columns_PNORI,parameter_columns_PNORS,parameter_columns)
        # df_correntes= aplicar_filtros(df_correntes,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_correntes
    #%% IMPORTAR DADOS METEO
    if parametro_para_teste == 'METEOROLOGIA':
        parameter_columns=parameter_columns_meteo
        df_meteo, nomes_colunas = import_df_meteo(input_file_meteo, nomes_colunas=parameter_columns_meteo)
        df_meteo= aplicar_filtros(df_meteo,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_meteo
    #%% IMPORTAR DADOS MARE
    if parametro_para_teste == 'MARE':
        parameter_columns=parameter_columns_mare
        df_tide,nomes_colunas= import_df_mare(input_file_mare, nomes_colunas=parameter_columns_mare)
        df_tide= aplicar_filtros(df_tide,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_tide
    #%%IMPORTAR DADOS ONDAS
    if parametro_para_teste == 'ONDAS':
        parameter_columns=parameter_columns_ondas
        df_ondas = process_wave_data(df_PNORW, df_PNORB, df_PNORI, df_PNORS,parameter_columns_PNORW, parameter_columns_PNORB, parameter_columns_PNORI, parameter_columns_PNORS, parameter_columns_ondas)
        df_ondas= aplicar_filtros(df_ondas,parameter_columns,dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike,dict_lt_time_and_regressao)
        df=df_ondas
    #%%IMPORTAR DADOS ONDAS NAO DIRECIONAIS

    if parametro_para_teste== 'ONDAS_NAO_DIRECIONAIS':
        parameter_columns=parameter_columns_ondas_nao_direcionais
        # df_ondas_nao_direcionais = pd.read_csv(input_file_ondas_nao_direcionais)
        # df_ondas_nao_direcionais.rename(columns={"TIMESTAMP": "GMT-03:00"}, inplace=True)
        # for coluna in df_ondas_nao_direcionais.columns:
        #     df_ondas_nao_direcionais[f'Flag_{coluna}'] = 0
        
        df=aplicar_filtros(df, parameter_columns, dict_offset, limites_range_check, dict_max_min_test, st_time_series_dict, limite_repeticao_dados, limite_sigma_aceitavel_and_dict_delta_site, sampling_frequency, coluna_tempo, alert_window_size, dict_spike, dict_lt_time_and_regressao)
        # df=df_ondas_nao_direcionais
    df['GMT-03:00'] = pd.to_datetime(df['GMT-03:00'], errors='coerce')
    return df

# df=importar_e_aplicar_QC(parametro_para_teste)
parameter_columns=parameter_columns_ondas_nao_direcionais
# df.to_csv(r"G:\Drives compartilhados\DHE_REPASSE\2024\ID00_PD_MITR-QCMO\df_resultado.csv")
#%% GRAFICOS SERIE TEMPORAL
# plot_historical_series(df, parameter_columns) 
#%% GRAFICOS PERFIL VERTICAL

# if parametro_para_teste=='CORRENTES': 
#     gerar_grafico_gradiente_vertical(df, linha_escolhida=0, coluna_escolhida='speed(m/s)')
#     gerar_grafico_gradiente_vertical(df, linha_escolhida=0, coluna_escolhida='amplitude')
