import streamlit as st
import pandas as pd
from notion_client import Client
from babel.numbers import format_currency

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

st.set_page_config(layout='wide')

st.session_state.ntn_token = 'ntn_v1788076170b9OMfJeP6zHSAlPk4Gw8jryN0ujcV0KyfSc'

st.session_state.id_contratos = 'c344260990624865b81b5d3686262cdd'

st.session_state.id_ficha_clientes = 'e9bc3962a56b410483dd2a9fb19368ee'

if not 'df_contratos' in st.session_state:

    with st.spinner('Puxando dados do Notion...'):

        st.session_state.df_contratos = puxar_dados_contratos()

        st.session_state.df_contratos = st.session_state.df_contratos[~pd.isna(st.session_state.df_contratos[' '])].reset_index(drop=True)

        st.session_state.df_ficha_clientes = puxar_dados_ficha_clientes()

st.title('Acompanhamento de Vendas | RN Atelier - OMIE')

st.divider()    

row1 = st.columns(3) 

row2 = st.columns(3)

st.divider()  

row_2_5 = st.columns(1)

row3 = st.columns(3)

with row1[0]:

    atualizar_notion = st.button('Atualizar Dados Notion')

if atualizar_notion:

    with st.spinner('Puxando dados do Notion...'):

        st.session_state.df_contratos = puxar_dados_contratos()

        st.session_state.df_contratos = st.session_state.df_contratos[~pd.isna(st.session_state.df_contratos['Cliente'])].reset_index(drop=True)

        st.session_state.df_contratos['Cliente'] = st.session_state.df_contratos['Cliente'].str.strip()

        st.session_state.df_ficha_clientes = puxar_dados_ficha_clientes()

        st.session_state.df_ficha_clientes['Cliente'] = st.session_state.df_ficha_clientes['Cliente'].str.strip()

    df_contratos_fc = pd.merge(st.session_state.df_contratos[['Valor de Venda', 'Mês', 'Status', 'Cliente']], st.session_state.df_ficha_clientes, on='Cliente', how='left')

    # Filtrar Mês

    with row2[0]:

        filtro_mes = st.multiselect('Filtrar Mês', sorted(df_contratos_fc['Mês'].dropna().unique()), default=None)

        if filtro_mes:

            df_contratos_fc = df_contratos_fc[df_contratos_fc['Mês'].isin(filtro_mes)].reset_index(drop=True)

    # Filtrar Status

    with row2[1]:

        filtro_status = st.multiselect('Filtrar Status', sorted(df_contratos_fc['Status'].dropna().unique()), default=None)

        if filtro_status:

            df_contratos_fc = df_contratos_fc[df_contratos_fc['Status'].isin(filtro_status)].reset_index(drop=True)

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

