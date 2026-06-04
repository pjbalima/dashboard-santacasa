import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="HSJ controle documentos", layout="wide")
st.title("📊 HSJ controle documentos")
st.markdown("Dashboard interativo para acompanhamento de status de documentos por responsável.")

# 2. Carregar os dados
sheet_url = "https://docs.google.com/spreadsheets/d/1g_WofAvtoEyWQbOb2h-Kg93nRFSzr31g3ITu5O1gSjA/export?format=csv&gid=2067311371"

@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(sheet_url)
    # Remove espaços em branco do nome das colunas para evitar erros de digitação
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # Verifica se as colunas requisitadas existem na planilha
    if 'RESPONSAVEL' in df.columns and 'STATUS' in df.columns:
        
        # --- FILTROS NO MENU LATERAL ---
        st.sidebar.header("Filtros")
        
        # Obter lista de responsáveis (removendo valores vazios)
        responsaveis = df['RESPONSAVEL'].dropna().unique().tolist()
        
        # Criar filtro múltiplo
        filtro_responsavel = st.sidebar.multiselect(
            "Filtrar por Responsável:", 
            options=responsaveis, 
            default=responsaveis # Por padrão, todos vêm selecionados
        )
        
        # Aplicar o filtro aos dados
        if filtro_responsavel:
            df_filtrado = df[df['RESPONSAVEL'].isin(filtro_responsavel)]
        else:
            df_filtrado = df

        st.divider()

        # --- VISÃO ANALÍTICA (TABELA CONSOLIDADA) ---
        st.subheader("📋 Visão Analítica: Status por Responsável")
        st.markdown("Tabela sumarizando a quantidade de documentos em cada status, separada por responsável.")
        
        # pd.crosstab cruza as linhas (Responsável) com as colunas (Status) contando as ocorrências
        tabela_analitica = pd.crosstab(
            df_filtrado['RESPONSAVEL'], 
            df_filtrado['STATUS'], 
            margins=True, 
            margins_name="TOTAL GERAL"
        )
        st.dataframe(tabela_analitica, use_container_width=True)

        st.divider()

        # --- VISÃO GRÁFICA ---
        st.subheader("📈 Visão Gráfica: Status por Responsável")
        
        # Preparando os dados para o gráfico de barras
        df_grafico = df_filtrado.groupby(['RESPONSAVEL', 'STATUS']).size().reset_index(name='Quantidade')
        
        # Criando o gráfico (Barras empilhadas)
        fig = px.bar(
            df_grafico, 
            x='RESPONSAVEL', 
            y='Quantidade', 
            color='STATUS',
            title="Quantidade de Documentos por Status e Responsável",
            labels={'RESPONSAVEL': 'Responsável', 'Quantidade': 'Nº de Documentos', 'STATUS': 'Status'},
            text_auto=True,      # Mostra os números dentro das barras
            barmode='stack'      # Empilha as barras de status no mesmo responsável
        )
        
        # Melhorando a aparência do gráfico
        fig.update_layout(xaxis_tickangle=-45)
        
        # Exibindo o gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # --- DADOS BRUTOS (Opcional) ---
        with st.expander("Visualizar Base de Dados Completa"):
            st.dataframe(df)

    else:
        st.error("As colunas 'RESPONSAVEL' e/ou 'STATUS' não foram encontradas na planilha. "
                 f"As colunas identificadas foram: {', '.join(df.columns)}")

except Exception as e:
    st.error(f"Erro ao carregar ou processar os dados: {e}")