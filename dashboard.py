import streamlit as st
import pandas as pd
import plotly.express as px
import ssl

# --- SOLUÇÃO PARA O ERRO DE SSL NO MAC ---
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="Dashboard - Sta Casa", layout="wide")
st.title("🏠 Dashboard: Sta Casa")

@st.cache_data(ttl=300)
def carregar_dados():
    # ATENÇÃO: Cole o seu link CSV aqui dentro das aspas!
    url_planilha = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1nxMbp7kGhc7G4IqTSE_MIvam5aWEjGWtlTp81jaTefcRynbjJLI8ZaMalRFBcdPobO9Y1QDdC_b8/pub?output=csv"
    
    try:
        # Lê os dados ignorando linhas com erro de digitação fora da tabela
        df = pd.read_csv(url_planilha, on_bad_lines='skip')
        
        # Limpa espaços em branco invisíveis no início ou fim dos nomes das colunas
        df.columns = df.columns.str.strip()
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    
    # --- NOMES EXATOS DAS SUAS COLUNAS ---
    col_status = 'Status'
    col_resp = 'Responsavel'       # Sem acento, conforme você confirmou!
    col_pub = 'Resp. Publicação'   # Com acento e ponto
    
    # Verifica se o Python encontrou essas 3 colunas na sua planilha
    if col_status in df.columns and col_resp in df.columns and col_pub in df.columns:
        
        # Remove apenas as linhas que estiverem totalmente vazias nessas 3 colunas
        df_limpo = df.dropna(subset=[col_status, col_resp, col_pub], how='all')

        st.markdown(f"### Resumo Geral (Total de registros válidos: {len(df_limpo)})")
        st.divider()
        
        # --- 3 GRÁFICOS LADO A LADO ---
        c1, c2, c3 = st.columns(3)
        
        with c1:
            ds = df_limpo[col_status].value_counts().reset_index()
            ds.columns = ['Status', 'Quantidade']
            fig1 = px.pie(ds, names='Status', values='Quantidade', title="1. Distribuição de Status (%)", hole=0.4)
            fig1.update_traces(textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            dr = df_limpo[col_resp].value_counts().reset_index()
            dr.columns = ['Responsavel', 'Quantidade']
            fig2 = px.bar(dr, x='Responsavel', y='Quantidade', title="2. Tarefas por Responsavel", color='Responsavel')
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)

        with c3:
            dp = df_limpo[col_pub].value_counts().reset_index()
            dp.columns = ['Resp. Publicação', 'Quantidade']
            fig3 = px.bar(dp, x='Resp. Publicação', y='Quantidade', title="3. Por Resp. Publicação", color='Resp. Publicação')
            fig3.update_traces(textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)

        # --- TABELA DE DADOS ---
        st.divider()
        st.markdown("### Detalhamento dos Registros")
        
        # Mostra as 3 colunas do processo na tabela final
        st.dataframe(df_limpo[[col_resp, col_pub, col_status]], use_container_width=True)

    else:
        # Se alguma coluna ainda estiver com nome diferente, ele te avisa qual é
        st.error("⚠️ Ops! O Python não encontrou os nomes exatos das colunas.")
        st.warning("Verifique se na sua planilha do Google os nomes estão escritos EXATAMENTE como aparecem abaixo:")
        st.write("Lista de todas as colunas que o Python conseguiu ler da sua planilha:")
        st.write(list(df.columns))

else:
    st.warning("Aguardando carregamento da planilha...")