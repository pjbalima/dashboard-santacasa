import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="HSJ Indicadores", layout="wide")
st.title("📊 Indicadores de Entrega")

# 2. Carregar os dados
sheet_url = "https://docs.google.com/spreadsheets/d/1g_WofAvtoEyWQbOb2h-Kg93nRFSzr31g3ITu5O1gSjA/export?format=csv&gid=2067311371"

@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    if 'RESPONSAVEL' in df.columns and 'STATUS' in df.columns:
        
        # --- FILTROS NO MENU LATERAL ---
        st.sidebar.header("Filtros")
        responsaveis = df['RESPONSAVEL'].dropna().unique().tolist()
        
        filtro_responsavel = st.sidebar.multiselect(
            "Filtrar por Responsável:", 
            options=responsaveis, 
            default=responsaveis
        )
        
        if filtro_responsavel:
            df_filtrado = df[df['RESPONSAVEL'].isin(filtro_responsavel)]
        else:
            df_filtrado = df

        # ==========================================
        # 1. LINHA SUPERIOR: CARDS DE MÉTRICAS
        # ==========================================
        col1, col2, col3 = st.columns(3)
        
        total_geral = len(df_filtrado)
        qtd_publicados = df_filtrado[df_filtrado['STATUS'].str.contains('Publicado', case=False, na=False)].shape[0] if 'STATUS' in df_filtrado.columns else 0
        qtd_importados = 0 

        col1.metric("Publicados no Cliente", qtd_publicados)
        col2.metric("Total Importados", qtd_importados)
        col3.metric("Total Geral da Base", total_geral)

        st.divider()

        # ==========================================
        # 2. LINHA DO MEIO: GRÁFICOS LADO A LADO
        # ==========================================
        col_esq, col_dir = st.columns([1, 2])

        # --- Gráfico da Esquerda: ROSCA ---
        with col_esq:
            st.markdown("**Status Geral**")
            df_status = df_filtrado['STATUS'].value_counts().reset_index()
            df_status.columns = ['STATUS', 'Quantidade']
            
            fig_rosca = px.pie(df_status, names='STATUS', values='Quantidade', hole=0.5)
            fig_rosca.update_traces(textposition='inside', textinfo='percent')
            fig_rosca.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig_rosca, use_container_width=True)

        # --- Gráfico da Direita: BARRAS ---
        with col_dir:
            st.markdown("**Total Acumulado por Responsável**")
            df_resp = df_filtrado['RESPONSAVEL'].value_counts().reset_index()
            df_resp.columns = ['RESPONSAVEL', 'Qtd']
            
            fig_bar = px.bar(df_resp, x='RESPONSAVEL', y='Qtd', text_auto=True, color='RESPONSAVEL')
            fig_bar.update_layout(showlegend=False, xaxis_title="Responsável", yaxis_title="Qtd", margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ==========================================
        # 3. LINHA INFERIOR: RESUMO CONSOLIDADO POR DIA
        # ==========================================
        st.subheader("📋 Resumo Consolidado por Dia e Responsável")

        if 'DT PUBLICADO' in df_filtrado.columns:
            df_pub = df_filtrado.dropna(subset=['DT PUBLICADO']).copy()
            df_pub['DT_REAL'] = pd.to_datetime(df_pub['DT PUBLICADO'], dayfirst=True, errors='coerce')
            df_pub = df_pub.dropna(subset=['DT_REAL'])
            
            df_detalhe = df_pub.groupby(['DT_REAL', 'RESPONSAVEL']).size().reset_index(name='Quantidade Publicada')
            
            df_total_dia = df_pub.groupby(['DT_REAL']).size().reset_index(name='Quantidade Publicada')
            df_total_dia['RESPONSAVEL'] = '↳ TOTAL DO DIA'
            
            df_consolidado = pd.concat([df_detalhe, df_total_dia], ignore_index=True)
            df_consolidado['ordem_linha'] = df_consolidado['RESPONSAVEL'].apply(lambda x: 1 if x == '↳ TOTAL DO DIA' else 0)
            df_consolidado = df_consolidado.sort_values(by=['DT_REAL', 'ordem_linha', 'RESPONSAVEL'], ascending=[False, True, True])
            df_consolidado['Data'] = df_consolidado['DT_REAL'].dt.strftime('%d/%m/%Y')
            
            df_display = df_consolidado[['Data', 'RESPONSAVEL', 'Quantidade Publicada']]
            # O nome da coluna final ajustado para a visualização desejada
            df_display.columns = ['Data', 'Resp. Publicação', 'Quantidade Publicada']
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
        else:
            st.warning("A coluna 'DT PUBLICADO' não foi encontrada para gerar o resumo.")

        st.divider()
        
        # --- DADOS BRUTOS ---
        with st.expander("Visualizar Base de Dados Completa"):
            st.dataframe(df_filtrado)

    else:
        st.error("As colunas 'RESPONSAVEL' e/ou 'STATUS' não foram encontradas.")

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")