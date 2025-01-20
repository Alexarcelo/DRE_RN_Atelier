import pandas as pd
import streamlit as st
from notion_client import Client

def puxar_agenda_producao():
    notion = Client(auth=st.session_state.ntn_token)
    database_id = st.session_state.id_agenda_producao
    data = []
    next_cursor = None

    while True:
        # Consulta a base de dados do Notion
        if next_cursor:
            response = notion.databases.query(database_id=database_id, start_cursor=next_cursor)
        else:
            response = notion.databases.query(database_id=database_id)

        results = response["results"]

        # Processa cada resultado
        for result in results:
            row = {}
            properties = result["properties"]

            # Mapear colunas específicas
            row["Cliente"] = (
                properties["Cliente"]["title"][0]["text"]["content"]
                if properties["Cliente"]["title"] else None
            )
            row["Atividade"] = (
                properties["Atividade"]["select"]["name"]
                if properties["Atividade"]["select"] else None
            )
            row["Data da Atividade"] = (
                properties["Data da Atividade"]["date"]["start"]
                if properties["Data da Atividade"]["date"] else None
            )
            row["Unidade SP ou JP"] = (
                properties["Unidade SP ou JP"]["select"]["name"]
                if properties["Unidade SP ou JP"]["select"] else None
            )
            row["Colaborador"] = (
                properties["Colaborador"]["select"]["name"]
                if properties["Colaborador"]["select"] else None
            )
            row["Status"] = (
                properties["Status"]["select"]["name"]
                if properties["Status"]["select"] else None
            )
            row["S.M. | P.P."] = (
                properties["S.M. | P.P."]["select"]["name"]
                if properties["S.M. | P.P."]["select"] else None
            )
            row["Etapa Atual"] = properties["Etapa Atual"]["number"]
            row["Etapas Totais"] = properties["Etapas Totais"]["number"]

            data.append(row)

        # Controle de paginação
        next_cursor = response.get("next_cursor", None)
        if not next_cursor:
            break

    # Converte a lista de dicionários para um DataFrame
    df = pd.DataFrame(data)

    return df

def criar_df_agenda_producao():

    st.session_state.df_agenda_producao = puxar_agenda_producao()

    st.session_state.df_agenda_producao = st.session_state.df_agenda_producao[pd.notna(st.session_state.df_agenda_producao['Cliente'])].reset_index(drop=True)

    st.session_state.df_agenda_producao['Data da Atividade'] = pd.to_datetime(st.session_state.df_agenda_producao['Data da Atividade']).dt.date

def gerar_df_agendas_livres(data_inicial, data_final):

    lista_datas = pd.date_range(start=data_inicial, end=data_final)

    df_sugestao_agenda = pd.DataFrame(data=lista_datas, columns=['Data da Atividade'])

    df_sugestao_agenda['Data da Atividade'] = df_sugestao_agenda['Data da Atividade'].dt.date

    return df_sugestao_agenda

def style_livre(val):

    color = 'background-color: #90EE90; color: black' if val == 'Livre' else ''

    return color

st.set_page_config(layout='wide')

# Criando token notion e id da tabela do notion

if not 'id_agenda_producao' in st.session_state:

    st.session_state.ntn_token = 'ntn_v1788076170b9OMfJeP6zHSAlPk4Gw8jryN0ujcV0KyfSc'

    st.session_state.id_agenda_producao = '14906a93e08a80348597e10090d82912'

    st.session_state.id_agenda_feriados = '18106a93e08a806582e6e555764fe4f5'

    st.session_state.id_agenda_ferias_pessoal = '18106a93e08a80399032f23bc9281676'

    st.session_state.id_esqueletos_padroes = '18106a93e08a80e4b530f6396c1d1428'

    st.session_state.id_colaboradores_producao = '18106a93e08a80c383a9cd4970aa36bb'

# Puxando feriados, férias do pessoal, agenda produção, esqueletos padrões, colaboradores

if not 'df_agenda_producao' in st.session_state:

    with st.spinner('Puxando agenda produção...'):

        criar_df_agenda_producao()

dias_da_semana = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

st.title('Agendas Livres')

st.divider()

row1 = st.columns(3)

with row1[0]:

    container_datas = st.container(border=True)

    data_inicial = container_datas.date_input('Data Inicial', value=None, format='DD/MM/YYYY')

    data_final = container_datas.date_input('Data Final', value=None, format='DD/MM/YYYY')

with row1[1]:

    container_visualizar = st.container(border=True)

    colaboradores = container_visualizar.multiselect('Visualizar Colaboradores', sorted(st.session_state.df_agenda_producao['Colaborador'].unique()), default=None)

    if len(colaboradores)==1:

        apenas_livres = container_visualizar.multiselect('Visualizar Apenas Dias Livres', ['Sim'], default=None)

    else:

        apenas_livres = None

with row1[2]:

    container_filtros = st.container(border=True)

    filtrar_dias_da_semana = container_filtros.multiselect('Excluir Dias da Semana', ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo'], default=None)

if data_inicial and data_final and len(colaboradores) > 0:

    df_agendas_livres = gerar_df_agendas_livres(data_inicial, data_final)

    for colaborador in colaboradores:

        df_colaborador = st.session_state.df_agenda_producao[st.session_state.df_agenda_producao['Colaborador'] == colaborador].reset_index(drop=True)

        df_colaborador = df_colaborador.groupby('Data da Atividade')['Colaborador'].count().reset_index()

        df_agendas_livres = pd.merge(df_agendas_livres, df_colaborador, on='Data da Atividade', how='left')

        df_agendas_livres = df_agendas_livres.rename(columns={'Colaborador': colaborador})

        df_agendas_livres[colaborador] = df_agendas_livres[colaborador].fillna('Livre')

        if apenas_livres and len(apenas_livres) > 0:

            df_agendas_livres = df_agendas_livres[df_agendas_livres[colaborador] == 'Livre']

        for coluna in df_agendas_livres.columns:

            if coluna!='Data da Atividade':

                df_agendas_livres[coluna] = df_agendas_livres[coluna].apply(lambda x: str(x)[:1] if x!='Livre' else x)

    df_agendas_livres['Dia da Semana'] = pd.to_datetime(df_agendas_livres['Data da Atividade']).dt.day_name()
    df_agendas_livres['Dia da Semana'] = df_agendas_livres['Dia da Semana'].map(dias_da_semana)

    lista_colunas = ['Data da Atividade', 'Dia da Semana']

    lista_colunas.extend(colaboradores)

    df_agendas_livres = df_agendas_livres[lista_colunas]

    if len(filtrar_dias_da_semana)>0:

        df_agendas_livres = df_agendas_livres[~df_agendas_livres['Dia da Semana'].isin(filtrar_dias_da_semana)]

    styled_df = df_agendas_livres.style.applymap(style_livre)

    container_dataframe = st.container()

    container_dataframe.dataframe(styled_df, hide_index=True, use_container_width=True, height=1000)

elif data_inicial and len(colaboradores) > 0:

    data_final = st.session_state.df_agenda_producao['Data da Atividade'].max()

    df_agendas_livres = gerar_df_agendas_livres(data_inicial, data_final)

    for colaborador in colaboradores:

        df_colaborador = st.session_state.df_agenda_producao[st.session_state.df_agenda_producao['Colaborador'] == colaborador].reset_index(drop=True)

        df_colaborador = df_colaborador.groupby('Data da Atividade')['Colaborador'].count().reset_index()

        df_agendas_livres = pd.merge(df_agendas_livres, df_colaborador, on='Data da Atividade', how='left')

        df_agendas_livres = df_agendas_livres.rename(columns={'Colaborador': colaborador})

        df_agendas_livres[colaborador] = df_agendas_livres[colaborador].fillna('Livre')

        if apenas_livres and len(apenas_livres) > 0:

            df_agendas_livres = df_agendas_livres[df_agendas_livres[colaborador] == 'Livre']

        for coluna in df_agendas_livres.columns:

            if coluna!='Data da Atividade':

                df_agendas_livres[coluna] = df_agendas_livres[coluna].apply(lambda x: str(x)[:1] if x!='Livre' else x)

    df_agendas_livres['Dia da Semana'] = pd.to_datetime(df_agendas_livres['Data da Atividade']).dt.day_name()
    df_agendas_livres['Dia da Semana'] = df_agendas_livres['Dia da Semana'].map(dias_da_semana)

    lista_colunas = ['Data da Atividade', 'Dia da Semana']

    lista_colunas.extend(colaboradores)

    df_agendas_livres = df_agendas_livres[lista_colunas]

    if len(filtrar_dias_da_semana)>0:

        df_agendas_livres = df_agendas_livres[~df_agendas_livres['Dia da Semana'].isin(filtrar_dias_da_semana)]

    styled_df = df_agendas_livres.style.applymap(style_livre)

    container_dataframe = st.container()

    container_dataframe.dataframe(styled_df, hide_index=True, use_container_width=True, height=1000)

elif len(colaboradores) > 0:

    data_inicial = st.session_state.df_agenda_producao['Data da Atividade'].min()

    data_final = st.session_state.df_agenda_producao['Data da Atividade'].max()

    df_agendas_livres = gerar_df_agendas_livres(data_inicial, data_final)

    for colaborador in colaboradores:

        df_colaborador = st.session_state.df_agenda_producao[st.session_state.df_agenda_producao['Colaborador'] == colaborador].reset_index(drop=True)

        df_colaborador = df_colaborador.groupby('Data da Atividade')['Colaborador'].count().reset_index()

        df_agendas_livres = pd.merge(df_agendas_livres, df_colaborador, on='Data da Atividade', how='left')

        df_agendas_livres = df_agendas_livres.rename(columns={'Colaborador': colaborador})

        df_agendas_livres[colaborador] = df_agendas_livres[colaborador].fillna('Livre')

        if apenas_livres and len(apenas_livres) > 0:

            df_agendas_livres = df_agendas_livres[df_agendas_livres[colaborador] == 'Livre']

        for coluna in df_agendas_livres.columns:

            if coluna!='Data da Atividade':

                df_agendas_livres[coluna] = df_agendas_livres[coluna].apply(lambda x: str(x)[:1] if x!='Livre' else x)

    df_agendas_livres['Dia da Semana'] = pd.to_datetime(df_agendas_livres['Data da Atividade']).dt.day_name()
    df_agendas_livres['Dia da Semana'] = df_agendas_livres['Dia da Semana'].map(dias_da_semana)

    lista_colunas = ['Data da Atividade', 'Dia da Semana']

    lista_colunas.extend(colaboradores)

    df_agendas_livres = df_agendas_livres[lista_colunas]

    if len(filtrar_dias_da_semana)>0:

        df_agendas_livres = df_agendas_livres[~df_agendas_livres['Dia da Semana'].isin(filtrar_dias_da_semana)]

    styled_df = df_agendas_livres.style.applymap(style_livre)

    container_dataframe = st.container()

    container_dataframe.dataframe(styled_df, hide_index=True, use_container_width=True, height=1000)
