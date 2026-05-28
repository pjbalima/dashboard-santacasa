import ssl
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="Dashboard de Controle", layout="wide")
st.title("📊 Dashboard de Acompanhamento-PORTLET")

# 2. Função para carregar os dados diretamente do Google Sheets
@st.cache_data(ttl=10) # O cache evita ler a planilha o tempo todo (atualiza a cada 10 min)
def carregar_dados():
    # Extraímos o ID da sua planilha e usamos a URL de exportação para CSV
    sheet_id = "14jjxpnxQjTnzuXwNl7fpoMwbyxCeB7ZJS_25FbCaSNU"
    url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vSUjyIe8OpYAJfJ9eKYEgYen0iwMFLUKn89WHuSVbZCDqNDQCbDcZCOzGIgRjkqWQ8uGXlvIrTvwQcd/pub?output=csv"
    
    try:
        df = pd.read_csv(url)
        # Padronizando os nomes das colunas para maiúsculo para evitar erros no código
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error("Erro ao carregar a planilha. Verifique se o link está definido como 'Qualquer pessoa com o link' pode ver.")
        st.error(f"Detalhe do erro: {e}")
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    st.markdown("---")
    
    # =====================================================================
    # DEMANDA 1: Total da situação (STATUS) associado à coluna RESPONSAVEL
    # =====================================================================
    st.subheader("👤 Status por Responsável")
    
    if 'STATUS' in df.columns and 'RESPONSAVEL' in df.columns:
        # Conta a quantidade de cada status por responsável
        df_status_resp = df.groupby(['RESPONSAVEL', 'STATUS']).size().reset_index(name='Total')
        
        col1, col2 = st.columns([2, 1])
        with col1:
            # Gráfico de barras agrupadas
            fig1 = px.bar(
                df_status_resp, 
                x='RESPONSAVEL', 
                y='Total', 
                color='STATUS', 
                barmode='group',
                text_auto=True,
                title="Distribuição de Status por Responsável"
            )
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.dataframe(df_status_resp, use_container_width=True, hide_index=True)
    else:
        st.warning("Colunas 'STATUS' ou 'RESPONSAVEL' não foram encontradas. Verifique a grafia.")

    st.markdown("---")
    
    # =====================================================================
    # DEMANDA 2: Total de TEM FILTRO DATA (SIM vs Outros Preenchidos)
    # =====================================================================
    st.subheader("📅 Coluna: TEM_FILTRO_DATA")
    
    if 'TEM_FILTRO_DATA' in df.columns:
        # Remove linhas vazias (onde não há nada preenchido)
        df_filtro = df[df['TEM_FILTRO_DATA'].notna()].copy()
        
        # Cria uma nova coluna separando em 'SIM' e 'Outros'
        df_filtro['Categoria'] = df_filtro['TEM_FILTRO_DATA'].apply(
            lambda x: 'SIM' if str(x).strip().upper() == 'SIM' else 'Outros'
        )
        
        total_sim = len(df_filtro[df_filtro['Categoria'] == 'SIM'])
        total_outros = len(df_filtro[df_filtro['Categoria'] == 'Outros'])
        
        col3, col4, col5 = st.columns(3)
        col3.metric("🟢 Total 'SIM'", total_sim)
        col4.metric("🟡 Total 'Outros' (Preenchidos)", total_outros)
        
        # Gráfico de pizza
        df_pizza = pd.DataFrame({'Categoria': ['SIM', 'Outros'], 'Total': [total_sim, total_outros]})
        fig2 = px.pie(df_pizza, names='Categoria', values='Total', hole=0.4, color='Categoria',
                      color_discrete_map={'SIM': '#00CC96', 'Outros': '#FFA15A'})
        with col5:
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Coluna 'TEM_FILTRO_DATA' não encontrada.")

    st.markdown("---")

# =====================================================================
    # DEMANDA 3: LEVANTAMENTO NUM DOC (Ajustado com os novos cabeçalhos)
    # =====================================================================
    st.subheader("📄 Coluna: LEVANTAMENTO NUM DOC")
    
    if 'LEVANTAMENTO NUM DOC' in df.columns:
        # Identifica quais linhas têm 'X' (seja maiúsculo ou minúsculo)
        condicao_x = df['LEVANTAMENTO NUM DOC'].apply(lambda x: str(x).strip().upper() == 'X')
        
        total_com_x = condicao_x.sum()
        total_sem_x = len(df) - total_com_x # Total de linhas menos as que têm X
        
        col6, col7 = st.columns(2)
        # Alteração dos cabeçalhos das métricas conforme solicitado
        col6.metric("📄 Sem referencia a docs", total_com_x)
        col7.metric("📄 Com referencia a docs", total_sem_x)
        
        # Ajuste das legendas e nomes das barras no gráfico
        df_x = pd.DataFrame({
            'Situação': ['Sem referencia a docs', 'Com referencia a docs'], 
            'Quantidade': [total_com_x, total_sem_x]
        })
        
        fig3 = px.bar(
            df_x, 
            x='Situação', 
            y='Quantidade', 
            color='Situação', 
            text_auto=True,
            color_discrete_map={'Sem referencia a docs': '#636EFA', 'Com referencia a docs': '#EF553B'}
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Coluna 'LEVANTAMENTO NUM DOC' não encontrada.")

   