import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página (mantendo o layout expandido para caber tudo)
st.set_page_config(page_title="HSJ Indicadores", layout="wide")

# Título Principal adaptado para ficar parecido com a sua imagem
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
        
        # Cálculos para as métricas da imagem
        total_geral = len(df_filtrado)
        
        # Aqui, estamos filtrando para contar apenas os documentos que têm "Publicado" no status.
        # (Se na sua planilha a palavra for um pouco diferente, você pode alterar aqui abaixo)
        qtd_publicados = df_filtrado[df_filtrado['STATUS'].str.contains('Publicado', case=False, na=False)].shape[0]
        
        # Como não sei qual status define "Importados", deixei como 0 (pode ser ajustado depois)
        qtd_importados = 0 

        # Desenhando os números grandes na tela
        col1.metric("Publicados no Cliente", qtd_publicados)
        col2.metric("Total Importados", qtd_importados)
        col3.metric("Total Geral da Base", total_geral)

        st.divider()

        # ==========================================
        # 2. LINHA INFERIOR: GRÁFICOS LADO A LADO
        # ==========================================
        # Criamos duas colunas. O [1, 2] significa que a coluna da direita é mais larga que a da esquerda
        col_esq, col_dir = st.columns([1, 2])

        # --- Gráfico da Esquerda: ROSCA (Status Geral) ---
        with col_esq:
            st.markdown("**Status Geral**")
            # Conta a quantidade de cada status
            df_status = df_filtrado['STATUS'].value_counts().reset_index()
            df_status.columns = ['STATUS', 'Quantidade']
            
            fig_rosca = px.pie(
                df_status, 
                names='STATUS', 
                values='Quantidade',
                hole=0.5 # É isso que transforma o gráfico de pizza num gráfico de rosca
            )
            # Ajusta para mostrar a porcentagem dentro do gráfico igual à sua imagem
            fig_rosca.update_traces(textposition='inside', textinfo='percent')
            fig_rosca.update_layout(margin=dict(t=0, b=0, l=0, r=0)) # Remove margens extras
            
            st.plotly_chart(fig_rosca, use_container_width=True)

        # --- Gráfico da Direita: BARRAS (Total por Responsável) ---
        with col_dir:
            st.markdown("**Total Acumulado por Responsável**")
            # Conta a quantidade total de documentos por pessoa (sem separar por status)
            df_resp = df_filtrado['RESPONSAVEL'].value_counts().reset_index()
            df_resp.columns = ['RESPONSAVEL', 'Qtd']
            
            fig_bar = px.bar(
                df_resp, 
                x='RESPONSAVEL', 
                y='Qtd',
                text_auto=True, # Coloca o número no topo da barra igual à sua imagem
                color='RESPONSAVEL' # Dá uma cor diferente para cada barra
            )
            
            # Limpa o design do gráfico (tira a legenda lateral e define os rótulos)
            fig_bar.update_layout(
                showlegend=False,
                xaxis_title="Responsável",
                yaxis_title="Qtd",
                margin=dict(t=0, b=0, l=0, r=0)
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()
        
        # --- DADOS BRUTOS (Opcional, minimizado por padrão) ---
        with st.expander("Visualizar Base de Dados Completa"):
            st.dataframe(df_filtrado)

    else:
        st.error("As colunas 'RESPONSAVEL' e/ou 'STATUS' não foram encontradas.")

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")