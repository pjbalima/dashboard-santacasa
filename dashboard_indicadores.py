import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard de Indicadores")

def load_data(url):
    csv_url = url.replace('/edit?gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url)

urls = {
    "HSJ": "https://docs.google.com/spreadsheets/d/1g_WofAvtoEyWQbOb2h-Kg93nRFSzr31g3ITu5O1gSjA/edit?gid=2067311371",
    "Portlets": "https://docs.google.com/spreadsheets/d/14jjxpnxQjTnzuXwNl7fpoMwbyxCeB7ZJS_25FbCaSNU/edit?gid=0",
    "SantaC": "https://docs.google.com/spreadsheets/d/1ZSMt6EoEVoi4Wxc-pzdXs5ksorpnOzENOPdSUWniy1g/edit?gid=0"
}

st.title("Dashboard Consolidado de Indicadores")

col1, col2, col3 = st.columns(3)

# --- PLANILHA 1 ---
with col1:
    st.subheader("HSJ-Indicadores (DOCs)")
    try:
        df1 = load_data(urls["HSJ"])
        fig1 = px.pie(df1, names='STATUS', title='Distribuição por Status')
        fig1.update_traces(textinfo='percent+value')
        st.plotly_chart(fig1, use_container_width=True)
        
        df1_filter = df1[df1['STATUS'] == 'Publicado no Cliente'].copy()
        if not df1_filter.empty:
            df1_filter['DT PUBLICADO'] = pd.to_datetime(df1_filter['DT PUBLICADO'], dayfirst=True, errors='coerce')
            df1_filter['DT_FORMATADA'] = df1_filter['DT PUBLICADO'].dt.strftime('%d/%m/%Y').fillna('Sem data')
            df1_grouped = df1_filter.groupby(['RESPONSAVEL', 'DT_FORMATADA']).size().reset_index(name='Total')
            pivot_df1 = df1_grouped.pivot_table(index='RESPONSAVEL', columns='DT_FORMATADA', values='Total', aggfunc='sum', fill_value=0, margins=True, margins_name='TOTAL GERAL')
            st.write("Publicados por Responsável e Data:")
            st.dataframe(pivot_df1, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na Planilha 1: {e}")

# --- PLANILHA 2 ---
with col2:
    st.subheader("SANTA C BAHIA Portlets")
    try:
        df2 = load_data(urls["Portlets"])
        fig2 = px.pie(df2, names='STATUS', title='Distribuição por Status')
        fig2.update_traces(textinfo='percent+value')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Filtro robusto: remove espaços em branco, padroniza para maiúsculo e garante que ache o "CONCLUIDO"
        df2_filter = df2[df2['STATUS'].astype(str).str.strip().str.upper() == 'CONCLUIDO'].copy()
        
        st.write("Concluídos por Responsável e Data:")
        if not df2_filter.empty:
            # Força a formatação de data
            df2_filter['DATA FIM'] = pd.to_datetime(df2_filter['DATA FIM'], dayfirst=True, errors='coerce')
            
            # O fillna garante que dados sem data não desapareçam do groupby
            df2_filter['DT_FORMATADA'] = df2_filter['DATA FIM'].dt.strftime('%d/%m/%Y').fillna('Sem data')
            
            df2_grouped = df2_filter.groupby(['RESPONSAVEL', 'DT_FORMATADA']).size().reset_index(name='Total')
            pivot_df2 = df2_grouped.pivot_table(index='RESPONSAVEL', columns='DT_FORMATADA', values='Total', aggfunc='sum', fill_value=0, margins=True, margins_name='TOTAL GERAL')
            
            st.dataframe(pivot_df2, use_container_width=True)
        else:
            st.info("Nenhum dado concluído encontrado para gerar o detalhamento.")
            
    except Exception as e:
        st.error(f"Erro na Planilha 2: {e}")

# --- PLANILHA 3 ---
with col3:
    st.subheader("SANTA C BAHIA (DOCs)")
    try:
        df3 = load_data(urls["SantaC"])
        fig3 = px.pie(df3, names='Status', title='Distribuição por Status')
        fig3.update_traces(textinfo='percent+value')
        st.plotly_chart(fig3, use_container_width=True)
        
        df3_filter = df3[df3['Status'] == 'Publicado no Cliente'].copy()
        if not df3_filter.empty:
            df3_filter['Data final'] = pd.to_datetime(df3_filter['Data final'], dayfirst=True, errors='coerce')
            df3_filter['DT_FORMATADA'] = df3_filter['Data final'].dt.strftime('%d/%m/%Y').fillna('Sem data')
            df3_grouped = df3_filter.groupby(['Responsavel', 'DT_FORMATADA']).size().reset_index(name='Total')
            pivot_df3 = df3_grouped.pivot_table(index='Responsavel', columns='DT_FORMATADA', values='Total', aggfunc='sum', fill_value=0, margins=True, margins_name='TOTAL GERAL')
            st.write("Publicados por Responsável e Data:")
            st.dataframe(pivot_df3, use_container_width=True)
        else:
            st.write("Publicados por Responsável e Data:")
            st.info("Nenhum dado com status 'Publicado no Cliente' encontrado.")
    except Exception as e:
        st.error(f"Erro na Planilha 3: {e}")
