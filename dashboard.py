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
        df = pd.read_csv(url_planilha, on_bad_lines='skip', dtype=str)
        df.columns = df.columns.str.strip()
        
        # Normalização de Status e Responsáveis
        df['Status_Clean'] = df['Status'].astype(str).str.strip().str.upper()
        df['Resp_Clean'] = df['Resp. Publicação'].fillna("Não Informado").astype(str).str.strip()
        
        # Tratamento da Data
        if 'DATA PUBLICAÇÃO NO CLIENTE' in df.columns:
            df['Data_Formatada'] = pd.to_datetime(df['DATA PUBLICAÇÃO NO CLIENTE'], errors='coerce', dayfirst=True)
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    STATUS_PUB = "PUBLICADO NO CLIENTE"
    STATUS_IMP = "IMPORTADO"

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
        df_ranking = df_pub['Resp_Clean'].value_counts().reset_index()
        df_ranking.columns = ['Responsável', 'Qtd']
        fig_barras = px.bar(df_ranking, x='Responsável', y='Qtd', text='Qtd', color='Responsável', title="Total Acumulado por Responsável")
        st.plotly_chart(fig_barras, use_container_width=True)

    # --- TABELA COM QUEBRA E TOTALIZADOR POR DIA ---
    st.divider()
    st.markdown("### 📋 Resumo Consolidado por Dia e Responsável")
    
    if not df_pub.empty and 'Data_Formatada' in df_pub.columns:
        # 1. Filtra registros com data válida
        df_base = df_pub.dropna(subset=['Data_Formatada']).copy()
        
        # 2. Agrupa por Data Real e Responsável
        df_agrupado = df_base.groupby([df_base['Data_Formatada'].dt.date, 'Resp_Clean']).size().reset_index(name='Quantidade Publicada')
        df_agrupado = df_agrupado.rename(columns={'Data_Formatada': 'Data_Real'})
        
        # 3. Ordena (Dias mais recentes primeiro, e dentro do dia quem produziu mais)
        df_agrupado = df_agrupado.sort_values(by=['Data_Real', 'Quantidade Publicada'], ascending=[False, False])
        
        # 4. Injeta as linhas de "TOTAL DO DIA"
        linhas_tabela = []
        
        for data_real, grupo in df_agrupado.groupby('Data_Real', sort=False):
            # Adiciona as pessoas daquele dia
            linhas_tabela.append(grupo)
            
            # Adiciona a linha de Subtotal no final do dia
            total_dia = grupo['Quantidade Publicada'].sum()
            linha_total = pd.DataFrame({
                'Data_Real': [data_real],
                'Resp_Clean': ['↳ TOTAL DO DIA'], # Setinha para destacar
                'Quantidade Publicada': [total_dia]
            })
            linhas_tabela.append(linha_total)
            
        # Junta todas as linhas na tabela final
        df_final = pd.concat(linhas_tabela, ignore_index=True)
        
        # 5. Ajustes Visuais (Formata a data para DD/MM/AAAA)
        df_final['Data'] = pd.to_datetime(df_final['Data_Real']).dt.strftime('%d/%m/%Y')
        
        # Renomeia e organiza as colunas para exibição
        df_final = df_final[['Data', 'Resp_Clean', 'Quantidade Publicada']]
        df_final = df_final.rename(columns={'Resp_Clean': 'Responsável da Publicação'})
        
        # Exibe a tabela
        st.dataframe(df_final, use_container_width=True, hide_index=True)
    else:
        st.info("Aguardando preenchimento das datas na planilha para gerar o resumo diário.")

else:
    st.info("Aguardando sincronização...")