import streamlit as st
import pandas as pd
import plotly.express as px
import ssl

# --- SOLUÇÃO PARA O ERRO DE SSL NO MAC ---
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="Dashboard - Santa Casa", layout="wide")
st.title("🏠 Dashboard: Santa Casa Bahia-Importação vs. Publicação")

@st.cache_data(ttl=60)
def carregar_dados():
    url_planilha = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1nxMbp7kGhc7G4IqTSE_MIvam5aWEjGWtlTp81jaTefcRynbjJLI8ZaMalRFBcdPobO9Y1QDdC_b8/pub?output=csv"
    try:
        # Lê a planilha tratando como texto para evitar erros
        df = pd.read_csv(url_planilha, on_bad_lines='skip', dtype=str)
        df.columns = df.columns.str.strip()
        
        # Limpeza e Normalização para evitar erros de espaços ou letras minúsculas
        df['Status_Clean'] = df['Status'].astype(str).str.strip().str.upper()
        df['Resp_Clean'] = df['Resp. Publicação'].fillna("Não Informado").astype(str).str.strip()
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    # Definição dos termos de busca
    STATUS_PUB = "PUBLICADO NO CLIENTE"
    STATUS_IMP = "IMPORTADO"

    # Filtragem dos dois status de interesse
    df_focado = df[df['Status_Clean'].isin([STATUS_PUB, STATUS_IMP])].copy()
    
    # --- MÉTRICAS DE TOPO ---
    qtd_pub = len(df[df['Status_Clean'] == STATUS_PUB])
    qtd_imp = len(df[df['Status_Clean'] == STATUS_IMP])
    
    st.subheader("📊 Resumo de Produtividade")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Importados", qtd_imp)
    c2.metric("Total Publicados no Cliente", qtd_pub)
    c3.metric("Soma (Imp + Pub)", qtd_imp + qtd_pub)
    
    st.divider()

    # --- GRÁFICO COMPARATIVO ---
    if not df_focado.empty:
        # Agrupamento para o gráfico
        df_grafico = df_focado.groupby(['Resp_Clean', 'Status']).size().reset_index(name='Quantidade')
        
        fig = px.bar(
            df_grafico, x='Resp_Clean', y='Quantidade', color='Status',
            title="Comparativo de Produção: Importado vs Publicado",
            text='Quantidade', barmode='group',
            color_discrete_map={"Importado": "#3366CC", "Publicado no Cliente": "#00CC96"}
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado com os status 'Importado' ou 'Publicado no Cliente'.")

    # --- TABELA DE DETALHAMENTO (A COLUNA SOLICITADA) ---
    st.divider()
    st.markdown("### 📋 Detalhamento por Responsável")
    
    if not df_focado.empty:
        # Criamos a tabela dinâmica (Pivot) para separar os status em colunas
        tabela_resumo = pd.crosstab(df_focado['Resp_Clean'], df_focado['Status']).reset_index()
        
        # Garante que as colunas existam na tabela mesmo que o valor seja zero
        for col_nome in ["Importado", "Publicado no Cliente"]:
            if col_nome not in tabela_resumo.columns:
                tabela_resumo[col_nome] = 0
        
        # Adiciona a soma das duas colunas
        tabela_resumo['TOTAL'] = tabela_resumo['Importado'] + tabela_resumo['Publicado no Cliente']
        
        # Renomeia e ordena
        tabela_resumo = tabela_resumo.rename(columns={'Resp_Clean': 'Responsável'})
        tabela_resumo = tabela_resumo.sort_values(by='TOTAL', ascending=False)
        
        # Exibe a tabela final
        st.dataframe(tabela_resumo, use_container_width=True, hide_index=True)
    else:
        st.warning("Sem dados suficientes para gerar o detalhamento.")

else:
    st.info("Aguardando sincronização com a planilha...")