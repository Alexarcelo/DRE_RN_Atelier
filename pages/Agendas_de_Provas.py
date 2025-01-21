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

st.set_page_config(layout='wide')

# Criando token notion e id da tabela do notion

if not 'id_agenda_producao' in st.session_state:

    st.session_state.ntn_token = 'ntn_v1788076170b9OMfJeP6zHSAlPk4Gw8jryN0ujcV0KyfSc'

    st.session_state.id_agenda_producao = '14906a93e08a80348597e10090d82912'

    st.session_state.id_agenda_feriados = '18106a93e08a806582e6e555764fe4f5'

    st.session_state.id_agenda_ferias_pessoal = '18106a93e08a80399032f23bc9281676'

    st.session_state.id_esqueletos_padroes = '18106a93e08a80e4b530f6396c1d1428'

    st.session_state.id_colaboradores_producao = '18106a93e08a80c383a9cd4970aa36bb'

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

st.title('Agendas de Provas')

st.divider()

cliente = st.multiselect('Cliente', sorted(st.session_state.df_agenda_producao['Cliente'].unique()), default=None)

if len(cliente)==1:

    df_cliente = st.session_state.df_agenda_producao[st.session_state.df_agenda_producao['Cliente'].isin(cliente)].reset_index(drop=True)

    atividades =  st.multiselect('Atividades', sorted(df_cliente['Atividade'].unique()), default=None)

    if len(atividades)>0:

        df_atividades = df_cliente[df_cliente['Atividade'].isin(atividades)][['Data da Atividade', 'Atividade']].reset_index(drop=True)

    else:

        df_atividades = df_cliente[df_cliente['Atividade'].isin(['Revisão de Croqui', 'Tirar Medidas', 'Prova 1', 'Prova 2', 'Prova 3', 'Prova Final', 'Entrega de Vestido'])]\
            [['Data da Atividade', 'Atividade']].reset_index(drop=True)
        
    df_atividades['Dia da Semana'] = pd.to_datetime(df_atividades['Data da Atividade']).dt.day_name()
    df_atividades['Dia da Semana'] = df_atividades['Dia da Semana'].map(dias_da_semana)

    df_atividades = df_atividades.sort_values(by='Data da Atividade').reset_index(drop=True)

    df_atividades['Data da Atividade'] = pd.to_datetime(df_atividades['Data da Atividade']).dt.strftime('%d/%m/%Y')

    header_css = """
        <style>
            .custom-header {
                font-size: 40px;
                font-family: 'Monaco', sans-serif;
            }
            .custom-subheader {
                font-size: 30px;
                font-family: 'Georgia', monospace;
            }
        </style>
    """

    st.markdown(header_css, unsafe_allow_html=True)

    st.markdown(f'<p class="custom-header">{cliente[0].upper()}</p>', unsafe_allow_html=True)

    for index in range(len(df_atividades)):

        data_atv = df_atividades.at[index, 'Data da Atividade']

        atividade_ref = df_atividades.at[index, 'Atividade']

        dia_da_semana = df_atividades.at[index, 'Dia da Semana']

        st.markdown(f'<p class="custom-subheader">{data_atv} – {dia_da_semana} | {atividade_ref}</p>', unsafe_allow_html=True)

    
