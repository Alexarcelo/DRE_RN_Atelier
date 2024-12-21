import streamlit as st
import pandas as pd
from notion_client import Client
from babel.numbers import format_currency
import gspread
import matplotlib.pyplot as plt
from google.cloud import secretmanager 
import json
from google.oauth2.service_account import Credentials

def puxar_dados_contratos():
    notion = Client(auth=st.session_state.ntn_token)
    database_id = st.session_state.id_contratos

    # Lista para armazenar os dados de todas as páginas
    data = []

    # Inicializando o cursor como None, para começar pela primeira página
    next_cursor = None

    while True:
        # Fazendo a requisição para o Notion, incluindo o cursor (se houver)
        if next_cursor:
            response = notion.databases.query(database_id=database_id, start_cursor=next_cursor)
        else:
            response = notion.databases.query(database_id=database_id)

        results = response["results"]

        # Processando os resultados da página atual
        for result in results:
            row = {}
            properties = result["properties"]
            for key, value in properties.items():
                if value["type"] == "title":
                    row[key] = value["title"][0]["text"]["content"] if value["title"] else None
                elif value["type"] == "rich_text":
                    row[key] = value["rich_text"][0]["text"]["content"] if value["rich_text"] else None
                elif value["type"] == "number":
                    row[key] = value["number"]
                elif value["type"] == "checkbox":
                    row[key] = value["checkbox"]
                elif value["type"] == "select":
                    row[key] = value["select"]["name"] if value["select"] else None
                elif value["type"] == "multi_select":
                    row[key] = ", ".join([item["name"] for item in value["multi_select"]])
                elif value["type"] == "date":
                    row[key] = value["date"]["start"] if value["date"] else None
                elif value["type"] == "url":
                    row[key] = value["url"]
                elif value["type"] == "email":
                    row[key] = value["email"]
                elif value["type"] == "phone_number":
                    row[key] = value["phone_number"]
                elif value["type"] == "formula":
                    row[key] = value["formula"]["string"] if value["formula"] else None
                elif value["type"] == "relation":
                    row[key] = ", ".join([rel["id"] for rel in value["relation"]])
                elif value["type"] == "people":
                    row[key] = ", ".join([person["name"] for person in value["people"]])
                else:
                    row[key] = None

            # Adicionando os dados da linha à lista
            data.append(row)

        # Verificando se existe uma próxima página
        next_cursor = response.get("next_cursor", None)

        # Se não houver mais próxima página, sair do loop
        if not next_cursor:
            break

    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(data)

    return df

def puxar_dados_ficha_clientes():
    notion = Client(auth=st.session_state.ntn_token)
    database_id = st.session_state.id_ficha_clientes

    # Lista para armazenar os dados de todas as páginas
    data = []

    # Inicializando o cursor como None, para começar pela primeira página
    next_cursor = None

    while True:
        # Fazendo a requisição para o Notion, incluindo o cursor (se houver)
        if next_cursor:
            response = notion.databases.query(database_id=database_id, start_cursor=next_cursor)
        else:
            response = notion.databases.query(database_id=database_id)

        results = response["results"]

        # Processando os resultados da página atual
        for result in results:
            row = {}
            properties = result["properties"]
            for key, value in properties.items():
                if key in ["Cliente", "Data do Contato", "Data do atendimento", "Orçamento Final", "Fonte"]:
                    if value["type"] == "title":
                        row[key] = value["title"][0]["text"]["content"] if value["title"] else None
                    elif value["type"] == "rich_text":
                        row[key] = value["rich_text"][0]["text"]["content"] if value["rich_text"] else None
                    elif value["type"] == "number":
                        row[key] = value["number"]
                    elif value["type"] == "date":
                        row[key] = value["date"]["start"] if value["date"] else None
                    elif value["type"] == "select":
                        row[key] = value["select"]["name"] if value["select"] else None
                    elif value["type"] == "multi_select":
                        row[key] = ", ".join([item["name"] for item in value["multi_select"]]) if value["multi_select"] else None
                    elif value["type"] == "people":
                        row[key] = ", ".join([person["name"] for person in value["people"]]) if value["people"] else None
                    elif value["type"] == "relation":
                        row[key] = ", ".join([rel["id"] for rel in value["relation"]]) if value["relation"] else None
                    else:
                        row[key] = None

            # Verificando se a linha tem dados válidos para as colunas desejadas
            if any(row.get(col) is not None for col in ["Cliente", "Data do Contato", "Data do atendimento", "Orçamento Final", "Fonte"]):
                data.append(row)

        # Verificando se existe uma próxima página
        next_cursor = response.get("next_cursor", None)

        # Se não houver mais próxima página, sair do loop
        if not next_cursor:
            break

    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(data)

    # Selecionando apenas as colunas desejadas
    colunas_desejadas = ["Cliente", "Data do Contato", "Data do atendimento", "Orçamento Final", "Fonte"]
    df = df[colunas_desejadas]

    return df

def puxar_aba_simples(id_gsheet, nome_aba, nome_df):

    project_id = "atelie-445321"
    secret_id = "cred-luck-aracaju"
    secret_client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})
    secret_payload = response.payload.data.decode("UTF-8")
    credentials_info = json.loads(secret_payload)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(id_gsheet)
    
    sheet = spreadsheet.worksheet(nome_aba)

    sheet_data = sheet.get_all_values()

    st.session_state[nome_df] = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

def grafico_duas_barras(referencia, eixo_x, eixo_y_1, ref_1_label, eixo_y_2, ref_2_label, titulo):

    referencia[eixo_x] = referencia[eixo_x].astype(str)
    
    fig, ax = plt.subplots(figsize=(15, 8))

    width = 0.6
    
    plt.bar(referencia[eixo_x], referencia[eixo_y_1], width, label = ref_1_label, alpha = 0.3, color = 'red', edgecolor='black')
    ax.bar(referencia[eixo_x], referencia[eixo_y_2], width, label = ref_2_label, alpha = 1, color = 'gray', edgecolor='black')
    
    for i in range(len(referencia[eixo_x])):
        texto = format_currency(referencia[eixo_y_1][i], 'BRL', locale='pt_BR')
        plt.text(referencia[eixo_x][i], referencia[eixo_y_1][i], texto, ha='center', va='bottom')
    for i in range(len(referencia[eixo_x])):
        texto_2 = format_currency(referencia[eixo_y_2][i], 'BRL', locale='pt_BR')
        plt.text(referencia[eixo_x][i], referencia[eixo_y_2][i], texto_2, ha='center', va='bottom')

    plt.title(titulo, fontsize=30)
    plt.xlabel('Mês/Ano')
    ax.legend(loc='lower right', bbox_to_anchor=(1.2, 1))
    st.pyplot(fig)
    plt.close(fig)

st.set_page_config(layout='wide')

st.session_state.ntn_token = 'ntn_v1788076170b9OMfJeP6zHSAlPk4Gw8jryN0ujcV0KyfSc'

st.session_state.id_contratos = 'c344260990624865b81b5d3686262cdd'

st.session_state.id_ficha_clientes = 'e9bc3962a56b410483dd2a9fb19368ee'

st.session_state.id_gsheet = '1P9g1KZKJ2h2SbWliHB1FEzf1KmST7Q-EKr3TLICVJK8'

st.session_state.patamar_comissoes_virgilio = [300000, 330000, 400000, 450000]

st.session_state.patamar_comissoes_perc_virgilio = [0.010, 0.011, 0.015, 0.018]

# Puxando dados do Notion

if not 'df_contratos' in st.session_state:

    with st.spinner('Puxando dados do Notion...'):

        st.session_state.df_contratos = puxar_dados_contratos()

        st.session_state.df_contratos = st.session_state.df_contratos[~pd.isna(st.session_state.df_contratos['Cliente'])].reset_index(drop=True)

        st.session_state.df_contratos['Cliente'] = st.session_state.df_contratos['Cliente'].str.strip()

        st.session_state.df_contratos['ano'] = pd.to_datetime(st.session_state.df_contratos['Data de Contrato']).dt.year

        st.session_state.df_contratos['ano'] = st.session_state.df_contratos['ano'].fillna(0).astype(int)

        st.session_state.df_ficha_clientes = puxar_dados_ficha_clientes()

        st.session_state.df_ficha_clientes['Cliente'] = st.session_state.df_ficha_clientes['Cliente'].str.strip()

# Puxando dados do Drive

if not 'df_metas' in st.session_state:

    with st.spinner('Puxando metas do Google Drive...'):

        puxar_aba_simples(st.session_state.id_gsheet, 'BD - Metas', 'df_metas')

        lista_colunas_numero = ['ano', 'mes', 'Virgílio']

        for coluna in lista_colunas_numero:

            st.session_state.df_metas[coluna] = pd.to_numeric(st.session_state.df_metas[coluna])

st.title('Acompanhamento de Vendas | RN Atelier - OMIE')

st.divider()    

row1 = st.columns(3) 

row1_2 = st.columns(1)

row2 = st.columns(3)

st.divider()  

row_2_5 = st.columns(1)

row3 = st.columns(3)

st.divider()

row4 = st.columns(1)

# Botão Atualizar Dados Notion

with row1[0]:

    atualizar_notion = st.button('Atualizar Dados Notion')

    if atualizar_notion:

        with st.spinner('Puxando dados do Notion...'):

            st.session_state.df_contratos = puxar_dados_contratos()

            st.session_state.df_contratos = st.session_state.df_contratos[~pd.isna(st.session_state.df_contratos['Cliente'])].reset_index(drop=True)

            st.session_state.df_contratos['Cliente'] = st.session_state.df_contratos['Cliente'].str.strip()

            st.session_state.df_contratos['ano'] = pd.to_datetime(st.session_state.df_contratos['Data de Contrato']).dt.year

            st.session_state.df_contratos['ano'] = st.session_state.df_contratos['ano'].fillna(0).astype(int)

            st.session_state.df_ficha_clientes = puxar_dados_ficha_clientes()

            st.session_state.df_ficha_clientes['Cliente'] = st.session_state.df_ficha_clientes['Cliente'].str.strip()

# Botão Atualizar Dados Drive

with row1[1]:

    atualizar_gsheet = st.button('Atualizar Metas Google Drive')

    if atualizar_gsheet:

        with st.spinner('Puxando metas do Google Drive...'):

            puxar_aba_simples(st.session_state.id_gsheet, 'BD - Metas', 'df_metas')

            lista_colunas_numero = ['ano', 'mes', 'Virgílio']

            for coluna in lista_colunas_numero:

                st.session_state.df_metas[coluna] = pd.to_numeric(st.session_state.df_metas[coluna])

with row1_2[0]:

    analise = st.radio('Análise', ['Vendas por Status', 'Meta Faturamento'], index=None)

df_contratos_fc = pd.merge(st.session_state.df_contratos[['Valor de Venda', 'Mês', 'Status', 'Cliente', 'ano', 'Unidade']], st.session_state.df_ficha_clientes, on='Cliente', how='left')

# Filtrar Mês

with row2[0]:

    filtro_mes = st.multiselect('Filtrar Mês', ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'], default=None)

    if filtro_mes:

        df_contratos_fc = df_contratos_fc[df_contratos_fc['Mês'].isin(filtro_mes)].reset_index(drop=True)

    filtro_ano = st.multiselect('Filtrar Ano', sorted(st.session_state.df_contratos[st.session_state.df_contratos['ano']!=0]['ano'].dropna().unique()), default=None)

    if filtro_ano:

        df_contratos_fc = df_contratos_fc[df_contratos_fc['ano'].isin(filtro_ano)].reset_index(drop=True)

# Filtrar Status

with row2[1]:

    filtro_status = st.multiselect('Filtrar Status', sorted(st.session_state.df_contratos['Status'].dropna().unique()), default=None)

    if filtro_status:

        df_contratos_fc = df_contratos_fc[df_contratos_fc['Status'].isin(filtro_status)].reset_index(drop=True)

if analise == 'Vendas por Status':

    df_contratos_fc['Valor de Venda'] = df_contratos_fc['Valor de Venda'].fillna(0)

    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    with row_2_5[0]:

        valor_total = format_currency(df_contratos_fc['Valor de Venda'].sum(), 'BRL', locale='pt_BR')

        st.markdown(
            f"""
            <h1 style="text-align: center;">Valor Total Geral = {valor_total}</h1>
            """,
            unsafe_allow_html=True
        )

    coluna = 0

    if filtro_status:

        for status in filtro_status:

            with row3[coluna]:

                container_dataframe = st.container(border=True)

                container_dataframe.subheader(status)

                valor_total = format_currency(df_contratos_fc[df_contratos_fc['Status']==status]['Valor de Venda'].sum(), 'BRL', locale='pt_BR')

                container_dataframe.subheader(f'Valor Total = {valor_total}')

                df_contratos_fc['Mês'] = pd.Categorical(df_contratos_fc['Mês'], categories=ordem_meses, ordered=True)

                df_tabela = df_contratos_fc.copy()

                df_tabela['Valor de Venda'] = df_tabela['Valor de Venda'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))

                container_dataframe.dataframe(df_tabela[df_tabela['Status']==status][['Cliente', 'Mês', 'Valor de Venda']].sort_values(by='Mês'), hide_index=True)

            if coluna != 2:

                coluna+=1

            else:

                coluna = 0

    else:

        for status in sorted(df_contratos_fc['Status'].dropna().unique()):

            with row3[coluna]:

                container_dataframe = st.container(border=True)

                container_dataframe.subheader(status)

                valor_total = format_currency(df_contratos_fc[df_contratos_fc['Status']==status]['Valor de Venda'].sum(), 'BRL', locale='pt_BR')

                container_dataframe.subheader(f'Valor Total = {valor_total}')

                df_contratos_fc['Mês'] = pd.Categorical(df_contratos_fc['Mês'], categories=ordem_meses, ordered=True)

                df_tabela = df_contratos_fc.copy()

                df_tabela['Valor de Venda'] = df_tabela['Valor de Venda'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))

                container_dataframe.dataframe(df_tabela[df_tabela['Status']==status][['Cliente', 'Mês', 'Valor de Venda']].sort_values(by='Mês'), hide_index=True)

            if coluna != 2:

                coluna+=1

            else:

                coluna = 0

elif analise == 'Meta Faturamento':

    df_metas = st.session_state.df_metas.copy()

    dict_mes = {1:'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    df_metas['Mês'] = df_metas['mes'].apply(lambda x: dict_mes[x])

    df_metas['mes/ano'] = pd.to_datetime(df_metas['ano'].astype(str) + '-' + df_metas['mes'].astype(str)).dt.to_period('M')

    df_vendas_mensal = df_contratos_fc.groupby(['ano', 'Mês'])['Valor de Venda'].sum().reset_index()

    df_metas = pd.merge(df_metas, df_vendas_mensal, on=['ano', 'Mês'], how='left')

    df_metas = df_metas[~pd.isna(df_metas['Valor de Venda'])].reset_index(drop=True)

    df_metas['Virgílio'] = df_metas['Valor de Venda'].apply(lambda x: st.session_state.patamar_comissoes_virgilio[0] if x<st.session_state.patamar_comissoes_virgilio[0]
                                                            else st.session_state.patamar_comissoes_virgilio[1] if x<st.session_state.patamar_comissoes_virgilio[1]
                                                            else st.session_state.patamar_comissoes_virgilio[2] if x<st.session_state.patamar_comissoes_virgilio[2]
                                                            else st.session_state.patamar_comissoes_virgilio[3])

    with row4[0]:

        grafico_duas_barras(df_metas, 'mes/ano', 'Virgílio', 'Meta', 'Valor de Venda', 'Venda Atual', 'Meta vs Vendas')

    st.header('Comissiômetro - Virgílio')

    df_metas['Comissão % Virgílio'] = df_metas['Valor de Venda'].apply(lambda x: st.session_state.patamar_comissoes_perc_virgilio[3] if x>=st.session_state.patamar_comissoes_virgilio[3] 
                                                                       else st.session_state.patamar_comissoes_perc_virgilio[2] if x>=st.session_state.patamar_comissoes_virgilio[2] 
                                                                       else st.session_state.patamar_comissoes_perc_virgilio[1] if x>=st.session_state.patamar_comissoes_virgilio[1] 
                                                                       else st.session_state.patamar_comissoes_perc_virgilio[0] if x>=st.session_state.patamar_comissoes_virgilio[0] else 0)
    
    df_metas['Comissão R$ Virgílio'] = df_metas['Comissão % Virgílio'] * df_metas['Valor de Venda']

    df_comissão_atual = df_metas[['ano', 'Mês', 'Comissão R$ Virgílio']]

    df_comissão_atual['Comissão R$ Virgílio'] = df_comissão_atual['Comissão R$ Virgílio'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))

    if filtro_mes:

        with row4[1]:

            st.subheader(f"*Sua comissão atual é {df_comissão_atual['Comissão R$ Virgílio'].iloc[0]}*")

            venda_atual = df_metas['Valor de Venda'].iloc[0]

            if venda_atual>=st.session_state.patamar_comissoes_virgilio[3]:

                st.subheader('Você atingiu o patamar máximo de comissionamento!!')

            elif venda_atual>=st.session_state.patamar_comissoes_virgilio[2]:

                valor_ate_proxima_meta = st.session_state.patamar_comissoes_virgilio[3] - venda_atual

                st.subheader(f"*Ta faltando {format_currency(valor_ate_proxima_meta, 'BRL', locale='pt_BR')} pra atingir o próximo patamar de comissionamento!*")

                valor_proxima_comissao = st.session_state.patamar_comissoes_virgilio[3]*st.session_state.patamar_comissoes_perc_virgilio[3]

                st.subheader(f"*Quando bater esse valor, a comissão sobe pra {format_currency(valor_proxima_comissao, 'BRL', locale='pt_BR')}!*")

            elif venda_atual>=st.session_state.patamar_comissoes_virgilio[1]:

                valor_ate_proxima_meta = st.session_state.patamar_comissoes_virgilio[2] - venda_atual

                st.subheader(f"*Ta faltando {format_currency(valor_ate_proxima_meta, 'BRL', locale='pt_BR')} pra atingir o próximo patamar de comissionamento!*")

                valor_proxima_comissao = st.session_state.patamar_comissoes_virgilio[2]*st.session_state.patamar_comissoes_perc_virgilio[2]

                st.subheader(f"*Quando bater esse valor, a comissão sobe pra {format_currency(valor_proxima_comissao, 'BRL', locale='pt_BR')}!*")

            elif venda_atual>=st.session_state.patamar_comissoes_virgilio[0]:

                valor_ate_proxima_meta = st.session_state.patamar_comissoes_virgilio[1] - venda_atual

                st.subheader(f"*Ta faltando {format_currency(valor_ate_proxima_meta, 'BRL', locale='pt_BR')} pra atingir o próximo patamar de comissionamento!*")

                valor_proxima_comissao = st.session_state.patamar_comissoes_virgilio[1]*st.session_state.patamar_comissoes_perc_virgilio[1]

                st.subheader(f"*Quando bater esse valor, a comissão sobe pra {format_currency(valor_proxima_comissao, 'BRL', locale='pt_BR')}!*")

            else:

                valor_ate_proxima_meta = st.session_state.patamar_comissoes_virgilio[0] - venda_atual

                st.subheader(f"*Ta faltando {format_currency(valor_ate_proxima_meta, 'BRL', locale='pt_BR')} pra atingir o próximo patamar de comissionamento!*")

                valor_proxima_comissao = st.session_state.patamar_comissoes_virgilio[0]*st.session_state.patamar_comissoes_perc_virgilio[0]

                st.subheader(f"*Quando bater esse valor, a comissão sobe pra {format_currency(valor_proxima_comissao, 'BRL', locale='pt_BR')}!*")
