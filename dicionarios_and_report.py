import json
import streamlit as st

# Função para carregar o dicionário de um arquivo JSON
def carregar_dicionario():
    try:
        with open('todos_dicionarios.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Arquivo não encontrado!")
        return {}

# Função para salvar o dicionário em um arquivo JSON
def salvar_dicionario(dicionario):
    with open('todos_dicionarios.json', 'w') as f:
        json.dump(dicionario, f, indent=4)

# Função para editar o dicionário 'limites_range_check' com agrupamento
def editar_limites_range_check(limites_range_check):
    for parametro, valores in limites_range_check.items():
        with st.expander(f"Editar Limites de {parametro}"):
            col1, col2 = st.columns(2)

            with col1:
                min_ambiental = st.number_input(f"Limite Ambiental Mínimo para {parametro}", value=valores['ambiental'][0])
                max_ambiental = st.number_input(f"Limite Ambiental Máximo para {parametro}", value=valores['ambiental'][1])

            with col2:
                min_sensores = st.number_input(f"Limite Sensor Mínimo para {parametro}", value=valores['sensores'][0])
                max_sensores = st.number_input(f"Limite Sensor Máximo para {parametro}", value=valores['sensores'][1])

            # Atualiza os valores no dicionário
            limites_range_check[parametro]['ambiental'] = [min_ambiental, max_ambiental]
            limites_range_check[parametro]['sensores'] = [min_sensores, max_sensores]

    return limites_range_check

# Função para editar os outros dicionários
def editar_outros_dicionarios(dicionario):
    for chave, valor in dicionario.items():
        if chave != "limites_range_check":
            with st.expander(f"Editar Dicionário: {chave}"):
                if isinstance(valor, dict):  # Se o valor for um dicionário
                    for sub_chave, sub_valor in valor.items():
                        if isinstance(sub_valor, list):  # Se o valor for uma lista
                            if all(isinstance(i, (int, float)) for i in sub_valor):  # Verifica se todos os itens da lista são numéricos
                                for i, v in enumerate(sub_valor):
                                    novo_valor = st.number_input(f"{sub_chave} - Índice {i} de {chave}", value=v)
                                    valor[sub_chave][i] = novo_valor
                        elif isinstance(sub_valor, (int, float)):  # Se o valor for numérico
                            novo_valor = st.number_input(f"{sub_chave} de {chave}", value=sub_valor)
                            valor[sub_chave] = novo_valor
                        else:
                            st.write(f"Não é possível editar {sub_chave} de {chave}, pois o valor não é numérico.")
                
                elif isinstance(valor, list):  # Se o valor for uma lista
                    if all(isinstance(i, (int, float)) for i in valor):  # Verifica se todos os itens da lista são numéricos
                        for i, v in enumerate(valor):
                            novo_valor = st.number_input(f"Índice {i} de {chave}", value=v)
                            dicionario[chave][i] = novo_valor
                    else:
                        st.write(f"Não é possível editar {chave}, pois a lista contém valores não numéricos.")
    
    return dicionario

# Interface no Streamlit
st.title("Edição de Dicionários - Monitoramento de Qualidade")

# Carregar o dicionário de dados do arquivo JSON
dados_json = carregar_dicionario()

# Edição do 'limites_range_check' de forma separada
if "limites_range_check" in dados_json:
    dados_json["limites_range_check"] = editar_limites_range_check(dados_json["limites_range_check"])

# Edição dos outros dicionários
dados_json = editar_outros_dicionarios(dados_json)

# Salvar os novos dicionários no arquivo JSON
if st.button("Salvar Alterações"):
    salvar_dicionario(dados_json)
    st.success("Alterações salvas com sucesso!")

    # Exibir o JSON atualizado
    st.subheader("Dicionários Atualizados")
    st.json(dados_json)
