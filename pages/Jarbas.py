import pandas as pd
import streamlit as st
from notion_client import Client
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import date, timedelta

def puxar_feriados():
    notion = Client(auth=st.session_state.ntn_token)
    database_id = st.session_state.id_agenda_feriados
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
            row["Feriados"] = (
                properties["Feriados"]["date"]["start"]
                if properties["Feriados"]["date"] else None
            )
            row["Local"] = (
                properties["Local"]["select"]["name"]
                if properties["Local"]["select"] else None
            )
            row["Descrição"] = (
                properties["Descrição"]["title"][0]["text"]["content"]
                if properties["Descrição"]["title"] else None
            )

            data.append(row)

        # Controle de paginação
        next_cursor = response.get("next_cursor", None)
        if not next_cursor:
            break

    # Converte a lista de dicionários para um DataFrame
    df = pd.DataFrame(data)

    return df

def criar_df_feriados():

    st.session_state.df_feriados = puxar_feriados()

    st.session_state.df_feriados['Feriados'] = pd.to_datetime(st.session_state.df_feriados['Feriados']).dt.date

def puxar_ferias_pessoal():
    notion = Client(auth=st.session_state.ntn_token)
    database_id = st.session_state.id_agenda_ferias_pessoal
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
            row["Colaborador"] = (
                properties["Colaborador"]["title"][0]["text"]["content"]
                if properties["Colaborador"]["title"] else None
            )
            row["Data Inicial"] = (
                properties["Data Inicial"]["date"]["start"]
                if properties["Data Inicial"]["date"] else None
            )
            row["Data Final"] = (
                properties["Data Final"]["date"]["start"]
                if properties["Data Final"]["date"] else None
            )

            data.append(row)

        # Controle de paginação
        next_cursor = response.get("next_cursor", None)
        if not next_cursor:
            break

    # Converte a lista de dicionários para um DataFrame
    df = pd.DataFrame(data)

    return df

def criar_df_ferias_pessoal():

    st.session_state.df_ferias_pessoal = puxar_ferias_pessoal()

    for coluna in ['Data Inicial', 'Data Final']:

        st.session_state.df_ferias_pessoal[coluna] = pd.to_datetime(st.session_state.df_ferias_pessoal[coluna]).dt.date

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

def puxar_esqueletos_padroes():
    notion = Client(auth=st.session_state.ntn_token)
    database_id = st.session_state.id_esqueletos_padroes
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
            row["Tipo de Vestido"] = (
                properties["Tipo de Vestido"]["title"][0]["text"]["content"]
                if properties["Tipo de Vestido"]["title"] else None
            )
            row["S.M. | P.P."] = (
                properties["S.M. | P.P."]["select"]["name"]
                if properties["S.M. | P.P."]["select"] else None
            )
            row["Etapa"] = (
                properties["Etapa"]["select"]["name"]
                if properties["Etapa"]["select"] else None
            )
            row["Unidade SP ou JP"] = (
                properties["Unidade SP ou JP"]["select"]["name"]
                if properties["Unidade SP ou JP"]["select"] else None
            )
            row["Colaborador"] = (
                properties["Colaborador"]["select"]["name"]
                if properties["Colaborador"]["select"] else None
            )
            row["Data Esp"] = (
                properties["Data Esp"]["date"]["start"]
                if properties["Data Esp"]["date"] else None
            )
            row["Duração"] = properties["Duração"]["number"]

            data.append(row)

        # Controle de paginação
        next_cursor = response.get("next_cursor", None)
        if not next_cursor:
            break

    # Converte a lista de dicionários para um DataFrame
    df = pd.DataFrame(data)

    return df

def criar_df_esqueletos_padroes():

    st.session_state.df_esqueletos_padroes = puxar_esqueletos_padroes()

    st.session_state.df_esqueletos_padroes['Data Esp'] = pd.to_datetime(st.session_state.df_esqueletos_padroes['Data Esp']).dt.date

def puxar_colaboradores_producao():
    notion = Client(auth=st.session_state.ntn_token)
    database_id = st.session_state.id_colaboradores_producao
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
            row["Colaborador"] = (
                properties["Colaborador"]["title"][0]["text"]["content"]
                if properties["Colaborador"]["title"] else None
            )

            data.append(row)

        # Controle de paginação
        next_cursor = response.get("next_cursor", None)
        if not next_cursor:
            break

    # Converte a lista de dicionários para um DataFrame
    df = pd.DataFrame(data)

    return df

def gerar_df_sugestao_agenda(data_entrega):

    lista_datas = pd.date_range(start=date.today()+timedelta(days=1), end=data_entrega)

    df_sugestao_agenda = pd.DataFrame(data=lista_datas, columns=['Data da Atividade'])

    df_sugestao_agenda['Data da Atividade'] = df_sugestao_agenda['Data da Atividade'].dt.date

    return df_sugestao_agenda

def identificar_finais_de_semana(df_sugestao_agenda):

    df_sugestao_agenda['Dia da Semana'] = pd.to_datetime(df_sugestao_agenda['Data da Atividade']).dt.day_name(locale='pt_BR')

    df_sugestao_agenda['Dia da Semana'] = df_sugestao_agenda['Dia da Semana'].apply(lambda x: '' if x not in ['Sábado', 'Domingo'] else x)

    return df_sugestao_agenda

def identificar_disponibilidade_colaboradores(df_sugestao_agenda):

    for colaborador in st.session_state.df_esqueleto_escolhido['Colaborador'].unique():

        if colaborador in st.session_state.df_colaboradores['Colaborador'].unique():

            df_agenda_colaborador = st.session_state.df_agenda_producao[st.session_state.df_agenda_producao['Colaborador']==colaborador][['Data da Atividade', 'Atividade']].reset_index(drop=True)

            df_agenda_colaborador = df_agenda_colaborador.groupby('Data da Atividade')['Atividade'].count().reset_index()

            df_sugestao_agenda = pd.merge(df_sugestao_agenda, df_agenda_colaborador, on='Data da Atividade', how='left')

            df_sugestao_agenda = df_sugestao_agenda.rename(columns={'Atividade': colaborador})

            df_sugestao_agenda[colaborador] = df_sugestao_agenda[colaborador].fillna(0)

    return df_sugestao_agenda

def identificar_ferias_colaboradores(df_sugestao_agenda):

    for colaborador in st.session_state.df_esqueleto_escolhido['Colaborador'].unique():

        if colaborador!='':

            df_ferias_colaborador = st.session_state.df_ferias_pessoal[st.session_state.df_ferias_pessoal['Colaborador']==colaborador]

            if len(df_ferias_colaborador)>0:

                data_inicial = df_ferias_colaborador['Data Inicial'].iloc[0]

                data_final = df_ferias_colaborador['Data Final'].iloc[0]

                lista_datas = [d.date() for d in pd.date_range(start=data_inicial, end=data_final)]

                df_sugestao_agenda.loc[df_sugestao_agenda['Data da Atividade'].isin(lista_datas), f'Férias {colaborador}'] = 'X'

                df_sugestao_agenda[f'Férias {colaborador}'] = df_sugestao_agenda[f'Férias {colaborador}'].fillna('')

    return df_sugestao_agenda

def determinar_data_primeira_etapa(df_esqueleto_sugestao, index, data_entrega, df_sugestao_agenda, etapa, unidade):

    df_esqueleto_sugestao.at[index, 'Data da Atividade'] = data_entrega

    data_etapa = data_entrega

    df_data_etapa = df_sugestao_agenda[(df_sugestao_agenda['Data da Atividade']==data_etapa)]

    dia_da_semana = df_data_etapa['Dia da Semana'].iloc[0]

    dia_feriado = df_data_etapa['Feriados'].iloc[0]

    local_feriado = df_data_etapa['Local'].iloc[0]

    if dia_da_semana=='Domingo' or (not pd.isna(dia_feriado) and local_feriado==unidade):

        st.warning(f'A etapa {etapa} vai acontecer em um domingo e/ou feriado.')

    return df_esqueleto_sugestao, data_etapa

def coletar_infos(df_esqueleto_sugestao, index):

    etapa = df_esqueleto_sugestao.at[index, 'Etapa']

    colaborador = df_esqueleto_sugestao.at[index, 'Colaborador']

    duracao = int(df_esqueleto_sugestao.at[index, 'Duração'])

    data_especifica = df_esqueleto_sugestao.at[index, 'Data Esp']

    unidade =  df_esqueleto_sugestao.at[index, 'Unidade SP ou JP']

    return etapa, colaborador, duracao, data_especifica, unidade

def colher_parametros_verificacao(df_sugestao_agenda, data_etapa, colaborador):

    df_data_etapa = df_sugestao_agenda[(df_sugestao_agenda['Data da Atividade']==data_etapa)]

    if colaborador in df_sugestao_agenda.columns:

        disponibilidade_colaborador = df_data_etapa[colaborador].iloc[0]

    else:
        
        disponibilidade_colaborador = 0

    dia_da_semana = df_data_etapa['Dia da Semana'].iloc[0]

    feriado = df_data_etapa['Feriados'].iloc[0]

    local_feriado = df_data_etapa['Local'].iloc[0]

    if f'Férias {colaborador}' in df_sugestao_agenda.columns:

        ferias_colaborador = df_data_etapa[f'Férias {colaborador}'].iloc[0]

    else:

        ferias_colaborador = ''

    return disponibilidade_colaborador, dia_da_semana, feriado, local_feriado, ferias_colaborador

def atribuir_data_especifica_colaborador_producao(disponibilidade_colaborador, ferias_colaborador, df_esqueleto_sugestao, index, data_especifica, data_etapa):

    if disponibilidade_colaborador<1 and ferias_colaborador=='':

        df_esqueleto_sugestao.at[index, 'Data da Atividade'] = data_especifica

        data_etapa = data_especifica

        return data_etapa, df_esqueleto_sugestao

    else:

        st.error(f"O colaborador {colaborador} está de férias ou não tem disponibilidade na agenda em {data_especifica.strftime('%d/%m/%Y')}")

        st.stop()

def atribuir_data_especifica_colaborador_adm(ferias_colaborador, df_esqueleto_sugestao, index, data_especifica, data_etapa):

    if ferias_colaborador=='':

        df_esqueleto_sugestao.at[index, 'Data da Atividade'] = data_especifica

        data_etapa = data_especifica

        return data_etapa, df_esqueleto_sugestao

    else:

        st.error(f"O colaborador {colaborador} está de férias em {data_especifica.strftime('%d/%m/%Y')}")

        st.stop()

def atribuir_data_etapa_colaborador_adm(ferias_colaborador, df_esqueleto_sugestao, index, data_etapa):

    if ferias_colaborador=='':

        df_esqueleto_sugestao.at[index, 'Data da Atividade'] = data_etapa

        return data_etapa, df_esqueleto_sugestao

    else:

        st.error(f"O colaborador {colaborador} está de férias em {data_etapa.strftime('%d/%m/%Y')}")

        st.stop()

def atribuir_data_etapa_duracao_maior_que_1_colaborador_producao(duracao, data_etapa, df_sugestao_agenda, colaborador, df_esqueleto_sugestao, index):

    loops = duracao-1

    while data_etapa>=date.today()+timedelta(days=1) and loops>0:

        data_etapa -= timedelta(days=1)

        disponibilidade_colaborador, dia_da_semana, feriado, local_feriado, ferias_colaborador = colher_parametros_verificacao(df_sugestao_agenda, data_etapa, colaborador)      

        if disponibilidade_colaborador<1 and not dia_da_semana in ['Sábado', 'Domingo'] and ((pd.isna(feriado)) or (pd.notna(feriado) and local_feriado!=unidade)) and ferias_colaborador=='':

            lista_datas = [str(df_esqueleto_sugestao.at[index, 'Data da Atividade'])]

            lista_datas.append(str(data_etapa))

            df_esqueleto_sugestao.at[index, 'Data da Atividade'] = ', '.join(sorted(lista_datas))

            loops-=1

    if data_etapa<date.today()+timedelta(days=1):

        st.error(f'Não consegui encontrar datas disponíveis para o colaborador {colaborador} executar a etapa {etapa} completamente')

        st.stop()

    else:

        return data_etapa, df_esqueleto_sugestao

def atribuir_data_etapa_1_colaborador_producao(data_etapa, df_sugestao_agenda, colaborador, df_esqueleto_sugestao, index):

    while data_etapa>=date.today()+timedelta(days=1):

        data_etapa-=timedelta(days=1)

        disponibilidade_colaborador, dia_da_semana, feriado, local_feriado, ferias_colaborador = colher_parametros_verificacao(df_sugestao_agenda, data_etapa, colaborador)

        if disponibilidade_colaborador<1 and not dia_da_semana in ['Sábado', 'Domingo'] and ((pd.isna(feriado)) or (pd.notna(feriado) and local_feriado!=unidade)) and ferias_colaborador=='':

            df_esqueleto_sugestao.at[index, 'Data da Atividade'] = data_etapa

            break

    if data_etapa<date.today()+timedelta(days=1):

        st.error(f'Não consegui encontrar datas disponíveis para o colaborador {colaborador} executar a etapa {etapa} completamente')

        st.stop()

    else:

        return data_etapa, df_esqueleto_sugestao

def inserir_dataframe_no_notion(dataframe, database_id, notion_token):
    
    notion = Client(auth=notion_token)

    for _, row in dataframe.iterrows():
        properties = {}

        for column, value in row.items():
            # Mapeia os campos do DataFrame para os tipos correspondentes no Notion
            if pd.isna(value):
                continue  # Ignora valores nulos
            elif column == "Cliente":
                properties[column] = {"title": [{"text": {"content": value}}]}
            elif column in ["Atividade", "Unidade SP ou JP", "Colaborador", "Status", "S.M. | P.P."]:
                properties[column] = {"select": {"name": value}}
            elif column == "Data da Atividade":
                properties[column] = {"date": {"start": pd.Timestamp(value).strftime("%Y-%m-%d")}}
            elif column in ["Etapa Atual", "Etapas Totais"]:
                properties[column] = {"number": value}
            else:
                # Caso existam outras colunas, coloca como rich_text genérico
                properties[column] = {"rich_text": [{"text": {"content": str(value)}}]}

        # Cria a nova página no Notion
        notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )

def expandir_datas(df, coluna_datas):

    df[coluna_datas] = df[coluna_datas].apply(lambda x: x.split(", ") if isinstance(x, str) else [x])

    df_expanded = df.explode(coluna_datas, ignore_index=True)
    
    return df_expanded

def gerar_df_insercao():

    df_insercao = st.session_state.df_esqueleto_sugestao[pd.notna(st.session_state.df_esqueleto_sugestao['Data da Atividade'])].sort_index(ascending=False).reset_index(drop=True)

    df_insercao = expandir_datas(df_insercao, "Data da Atividade")

    df_insercao['Etapa Atual'] = 1

    df_insercao['Etapas Totais'] = df_insercao['Duração']

    for index in range(1, len(df_insercao)):

        duracao_1 = df_insercao.at[index-1, 'Duração']

        duracao_2 = df_insercao.at[index, 'Duração']

        colaborador_1 = df_insercao.at[index-1, 'Colaborador']

        colaborador_2 = df_insercao.at[index, 'Colaborador']

        etapa_1 = df_insercao.at[index-1, 'Etapa']

        etapa_2 = df_insercao.at[index, 'Etapa']

        if duracao_2>1 and duracao_1==duracao_2 and etapa_1==etapa_2 and colaborador_1==colaborador_2:

            df_insercao.at[index, 'Etapa Atual'] = df_insercao.at[index-1, 'Etapa Atual']+1

    df_insercao = df_insercao.rename(columns={'Etapa': 'Atividade'})

    df_insercao['Cliente'] = cliente

    df_insercao['Status'] = None

    return df_insercao[['Cliente', 'Atividade', 'Data da Atividade', 'Unidade SP ou JP', 'Colaborador', 'Status', 'S.M. | P.P.', 'Etapa Atual', 'Etapas Totais']]

st.set_page_config(layout='wide')

# Criando token notion e ids das tabelas do notion

if not 'id_agenda_producao' in st.session_state:

    st.session_state.ntn_token = 'ntn_v1788076170b9OMfJeP6zHSAlPk4Gw8jryN0ujcV0KyfSc'

    st.session_state.id_agenda_producao = '14906a93e08a80348597e10090d82912'

    st.session_state.id_agenda_feriados = '18106a93e08a806582e6e555764fe4f5'

    st.session_state.id_agenda_ferias_pessoal = '18106a93e08a80399032f23bc9281676'

    st.session_state.id_esqueletos_padroes = '18106a93e08a80e4b530f6396c1d1428'

    st.session_state.id_colaboradores_producao = '18106a93e08a80c383a9cd4970aa36bb'

# Puxando feriados, férias do pessoal, agenda produção, esqueletos padrões, colaboradores

if not 'df_colaboradores' in st.session_state:

    with st.spinner('Puxando feriados, férias do pessoal, agenda produção, esqueletos padrões, colaboradores...'):

        criar_df_feriados()

        criar_df_ferias_pessoal()

        criar_df_agenda_producao()

        criar_df_esqueletos_padroes()

        st.session_state.df_colaboradores = puxar_colaboradores_producao()

# Criando variáveis que fazem o esqueleto da agenda aparecer ou sumir

if not 'esqueleto_escolhido' in st.session_state:

    st.session_state.esqueleto_escolhido = ''

    st.session_state.sugestao_gerada = False

st.title('Jarbas 2.0')

st.divider()

st.header('Esqueleto Agenda')

esqueleto_padrao = st.selectbox('Esqueleto Padrão', sorted(st.session_state.df_esqueletos_padroes['Tipo de Vestido'].unique()), index=None)

cliente = st.text_input('Cliente', value=None)

data_entrega = st.date_input('Data de Entrega', value=None, format='DD/MM/YYYY')

# Gerando um novo esqueleto se o usuário escolher um esqueleto ou se ele mudar o esqueleto selecionado

if esqueleto_padrao and esqueleto_padrao!=st.session_state.esqueleto_escolhido:

    st.session_state.esqueleto_escolhido = esqueleto_padrao

    st.session_state.sugestao_gerada = False

    st.session_state.df_esqueleto_escolhido = st.session_state.df_esqueletos_padroes[st.session_state.df_esqueletos_padroes['Tipo de Vestido']==esqueleto_padrao].reset_index(drop=True)

row1 = st.columns(5)

# Mostrando esqueleto

if st.session_state.esqueleto_escolhido!='':

    # Opção p/ alterar Colaborador de etapa

    with row1[0]:

        colaborador = st.selectbox('Colaborador', sorted(st.session_state.df_colaboradores['Colaborador'].unique()), index=None)

        alterar_colaborador = st.button('Alterar Colaborador')

        if alterar_colaborador and st.session_state.lista_index_escolhido:

            st.session_state.df_esqueleto_escolhido.loc[st.session_state.lista_index_escolhido, 'Colaborador'] = colaborador

    # Opção p/ alterar Data Específica de etapa

    with row1[1]:

        data_esp = st.date_input('Data Específica', value=None, format='DD/MM/YYYY')

        alterar_data_esp = st.button('Alterar Data Específica')

        if alterar_data_esp and st.session_state.lista_index_escolhido:

            st.session_state.df_esqueleto_escolhido.loc[st.session_state.lista_index_escolhido, 'Data Esp'] = data_esp

    # Opção p/ alterar Duração de etapa

    with row1[2]:

        duracao = st.number_input('Duração', value=None)

        alterar_duracao = st.button('Alterar Duração')

        if alterar_duracao and st.session_state.lista_index_escolhido:

            st.session_state.df_esqueleto_escolhido.loc[st.session_state.lista_index_escolhido, 'Duração'] = duracao

    # Opção p/ visualizar esqueleto caso precise alterar algo nele depois de já ter gerado a sugestão da agenda

    with row1[3]:

        visualizar_esqueleto = st.button('Visualizar Esqueleto')

    if visualizar_esqueleto:

        st.session_state.sugestao_gerada = False

    # Botão de sugerir agenda já aqui porque se o usuário apertar nele, é pra desaparecer o esqueleto

    with row1[4]:

        sugerir_agenda = st.button('Sugerir Agenda')

    if sugerir_agenda and cliente and data_entrega:

        st.session_state.sugestao_gerada = True

    # Plotagem de tabela de esqueleto

    if st.session_state.sugestao_gerada == False:

        row_height = 32
        header_height = 56  
        num_rows = len(st.session_state.df_esqueleto_escolhido)
        height = header_height + (row_height * num_rows)  

        gb_in = GridOptionsBuilder.from_dataframe(st.session_state.df_esqueleto_escolhido)
        gb_in.configure_selection('multiple', use_checkbox=True)
        gb_in.configure_grid_options(domLayout='autoHeight')
        gridOptions = gb_in.build()

        grid_response = AgGrid(st.session_state.df_esqueleto_escolhido, gridOptions=gridOptions, enable_enterprise_modules=False, fit_columns_on_grid_load=True, height=height)

        if not grid_response['selected_rows'] is None:

            st.session_state.lista_index_escolhido = grid_response['selected_rows'].reset_index()['index'].astype(int).tolist()

        else:

            st.session_state.lista_index_escolhido = None

    # Gerando sugestao de agenda

    if sugerir_agenda and cliente and data_entrega:

        # Gerdando data frame com todas as datas de amanhã até a data da entrega

        df_sugestao_agenda = gerar_df_sugestao_agenda(data_entrega)

        # Incluindo Feriados e Local de feriado

        df_sugestao_agenda = pd.merge(df_sugestao_agenda, st.session_state.df_feriados[['Feriados', 'Local']], left_on='Data da Atividade', right_on='Feriados', how='left')

        df_sugestao_agenda['Local'] = df_sugestao_agenda['Local'].fillna('')

        # Identificando finais de semana

        df_sugestao_agenda = identificar_finais_de_semana(df_sugestao_agenda)

        # Criando colunas com disponibilidade de colaboradores do esqueleto

        df_sugestao_agenda = identificar_disponibilidade_colaboradores(df_sugestao_agenda)

        # Identificar férias de pessoal dentro do período

        df_sugestao_agenda = identificar_ferias_colaboradores(df_sugestao_agenda)

        # Gerando sugestão de agenda

        df_esqueleto_sugestao = st.session_state.df_esqueleto_escolhido.sort_index(ascending=False).reset_index(drop=True)

        for index in range(len(df_esqueleto_sugestao)):

            etapa, colaborador, duracao, data_especifica, unidade = coletar_infos(df_esqueleto_sugestao, index)

            if index==0:

                df_esqueleto_sugestao, data_etapa = determinar_data_primeira_etapa(df_esqueleto_sugestao, index, data_entrega, df_sugestao_agenda, etapa, unidade)

            elif etapa=='Intervalo':

                data_etapa -= timedelta(days=duracao)

            else:

                # Quando tem data específica pra etapa, mas ela é posterior à data necessária p/ próxima etapa

                if data_especifica!='' and pd.notna(data_especifica) and data_especifica > data_etapa:

                    st.error(f"Não foi possível criar uma agenda em que a etapa {etapa} termine na data {data_especifica.strftime('%d/%m/%Y')}")

                    st.stop()

                # Quando tem data específica possível pra etapa e o colaborador é da produção

                if data_especifica!='' and pd.notna(data_especifica) and data_especifica <= data_etapa and colaborador in st.session_state.df_colaboradores['Colaborador'].unique():

                    disponibilidade_colaborador, dia_da_semana, feriado, local_feriado, ferias_colaborador = colher_parametros_verificacao(df_sugestao_agenda, data_especifica, colaborador)

                    data_etapa, df_esqueleto_sugestao = atribuir_data_especifica_colaborador_producao(disponibilidade_colaborador, ferias_colaborador, df_esqueleto_sugestao, index, data_especifica, 
                                                                                                    data_etapa)

                    # Preenchimento de datas quando a duração é maior que 1

                    if duracao>1:

                        data_etapa, df_esqueleto_sugestao = atribuir_data_etapa_duracao_maior_que_1_colaborador_producao(duracao, data_etapa, df_sugestao_agenda, colaborador, df_esqueleto_sugestao, index)

                # Quando tem data específica possível pra etapa e o colaborador não é da produção

                elif data_especifica!='' and pd.notna(data_especifica) and data_especifica <= data_etapa and not colaborador in st.session_state.df_colaboradores['Colaborador'].unique():

                    disponibilidade_colaborador, dia_da_semana, feriado, local_feriado, ferias_colaborador = colher_parametros_verificacao(df_sugestao_agenda, data_especifica, colaborador)

                    data_etapa, df_esqueleto_sugestao = atribuir_data_especifica_colaborador_adm(ferias_colaborador, df_esqueleto_sugestao, index, data_especifica, data_etapa)

                else:

                    # Quando não tem data específica e o colaborador não é da produção

                    if not colaborador in st.session_state.df_colaboradores['Colaborador'].unique():

                        disponibilidade_colaborador, dia_da_semana, feriado, local_feriado, ferias_colaborador = colher_parametros_verificacao(df_sugestao_agenda, data_etapa, colaborador)

                        data_etapa, df_esqueleto_sugestao = atribuir_data_etapa_colaborador_adm(ferias_colaborador, df_esqueleto_sugestao, index, data_etapa)

                    else:

                        data_etapa, df_esqueleto_sugestao = atribuir_data_etapa_1_colaborador_producao(data_etapa, df_sugestao_agenda, colaborador, df_esqueleto_sugestao, index)

                        if duracao>1:

                            data_etapa, df_esqueleto_sugestao = atribuir_data_etapa_duracao_maior_que_1_colaborador_producao(duracao, data_etapa, df_sugestao_agenda, colaborador, df_esqueleto_sugestao, index)

        st.session_state.df_esqueleto_sugestao = df_esqueleto_sugestao.reset_index(drop=True)

if 'df_esqueleto_sugestao' in st.session_state and len(st.session_state.df_esqueleto_sugestao)>0 and st.session_state.sugestao_gerada == True:

    df_esqueleto_final = st.session_state.df_esqueleto_sugestao[pd.notna(st.session_state.df_esqueleto_sugestao['Data da Atividade'])]\
        [['Data da Atividade', 'Data Esp', 'Duração', 'Colaborador', 'Etapa', 'Unidade SP ou JP']].sort_index(ascending=False).reset_index(drop=True)

    container_dataframe = st.container()

    container_dataframe.dataframe(df_esqueleto_final, hide_index=True, use_container_width=True)

    inserir_agenda = st.button('Inserir Agenda')

    if inserir_agenda:

        with st.spinner('Inserindo agenda no Notion...'):

            df_insercao = gerar_df_insercao()

            inserir_dataframe_no_notion(df_insercao, st.session_state.id_agenda_producao, st.session_state.ntn_token)

        with st.spinner('Puxando agenda produção atualizada...'):

            criar_df_agenda_producao()
