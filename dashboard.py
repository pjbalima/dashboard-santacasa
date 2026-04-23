import streamlit as st
import pandas as pd
import plotly.express as px
import ssl

# --- SOLUÇÃO PARA O ERRO DE SSL NO MAC ---
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="Dashboard - Santa Casa", layout="wide")
st.title("🏠 Dashboard: Produtividade Consolidada")

@st.cache_data(ttl=60)
def carregar_dados():
    url_planilha = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1nxMbp7kGhc7G4IqTSE_MIvam5aWEjGWtlTp81jaTefcRynbjJLI8ZaMalRFBcdPobO9Y1QDdC_b8/pub?output=csv"
    try:
        # Lê os dados da planilha
        df = pd.read_csv(url_planilha, on_bad_lines='skip', dtype=str)
        df.columns = df.columns.str.strip()
        
        # Normalização de Status e Responsáveis
        df['Status_Clean'] = df['Status'].astype(str).str.strip().str.upper()
        df['Resp_Clean'] = df['Resp. Publicação'].fillna("Não Informado").astype(str).str.strip()
        
        # Tratamento da Data de Publicação
        if 'DATA PUBLICAÇÃO NO CLIENTE' in df.columns:
            # Converte para formato de data (DD/MM/AAAA)
            df['Data_Formatada'] = pd.to_datetime(df['DATA PUBLICAÇÃO NO CLIENTE'], errors='coerce', dayfirst=True)
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    STATUS_PUB = "PUBLICADO NO CLIENTE"
    STATUS_IMP = "IMPORTADO"

    # Filtro focado nos publicados
    df_pub = df[df['Status_Clean'] == STATUS_PUB].copy()

    # --- MÉTRICAS GERAIS ---
    st.subheader("📊 Indicadores de Entrega")
    m1, m2, m3 = st.columns(3)
    m1.metric("Publicados no Cliente", len(df_pub))
    m2.metric("Total Importados", len(df[df['Status_Clean'] == STATUS_IMP]))
    m3.metric("Total Geral da Base", len(df))
    
    st.divider()

    # --- GRÁFICOS ---
    col_esq, col_dir = st.columns([1, 2])
    
    with col_esq:
        ds = df['Status'].value_counts().reset_index()
        ds.columns = ['Status', 'Quantidade']
        fig_pizza = px.pie(ds, names='Status', values='Quantidade', title="Status Geral", hole=0.4)
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col_dir:
        # Gráfico de barras: Ranking acumulado
        df_ranking = df_pub['Resp_Clean'].value_counts().reset_index()
        df_ranking.columns = ['Responsável', 'Qtd']
        fig_barras = px.bar(df_ranking, x='Responsável', y='Qtd', text='Qtd', color='Responsável', title="Total Acumulado por Responsável")
        st.plotly_chart(fig_barras, use_container_width=True)

    # --- TABELA DE RESUMO CONSOLIDADO POR DIA E RESPONSÁVEL ---
    st.divider()
    st.markdown("### 📋 Resumo Consolidado por Dia e Responsável")
    
    if not df_pub.empty and 'Data_Formatada' in df_pub.columns:
        # Criamos a visão consolidada
        # 1. Filtramos apenas quem tem data válida
        df_consolidado = df_pub.dropna(subset=['Data_Formatada']).copy()
        
        # 2. Criamos a coluna de texto para a data (DD/MM/AAAA)
        df_consolidado['Dia'] = df_consolidado['Data_Formatada'].dt.strftime('%d/%m/%Y')
        
        # 3. Agrupamos por Dia e Responsável para contar os registros
        tabela_resumo = df_consolidado.groupby(['Dia', 'Resp_Clean']).size().reset_index(name='Quantidade Publicada')
        
        # 4. Ordenamos para mostrar as datas mais recentes primeiro
        # Para ordenar corretamente, precisamos ordenar pela data real, não pelo texto formatado
        df_consolidado_sort = df_consolidado.groupby([df_consolidado['Data_Formatada'].dt.date, 'Resp_Clean']).size().reset_index(name='Quantidade Publicada')
        df_consolidado_sort = df_consolidado_sort.rename(columns={'Data_Formatada': 'Data'})
        df_consolidado_sort = df_consolidado_sort.sort_values(by=['Data', 'Quantidade Publicada'], ascending=[False, False])
        
        # Formatamos a data apenas para exibição final
        df_consolidado_sort['Data'] = pd.to_datetime(df_consolidado_sort['Data']).dt.strftime('%d/%m/%Y')
        df_consolidado_sort = df_consolidado_sort.rename(columns={'Resp_Clean': 'Responsável da Publicação'})
        
        st.dataframe(df_consolidado_sort, use_container_width=True, hide_index=True)
    else:
        st.info("Aguardando preenchimento das datas na planilha para gerar o resumo diário.")

else:
    st.info("Aguardando sincronização...")