import io
import re
import unicodedata
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# 1. Configuração da página do Streamlit
st.set_page_config(
    layout="wide", page_title="Dashboard Unimed Nacional", page_icon="📊"
)

# 2. Cabeçalho Oficial
st.markdown(
    "<h1 style='text-align: center; margin-bottom: 0px;'>Sulwork</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='text-align: center; color: #555; margin-top: 5px;'>UNIMED"
    " NACIONAL/Migracao Oracle 19</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

# 3. Mapeamento das 14 empresas (abas da planilha)
mapa_empresas = {
    "Empresa 06": "06 - ESPAÇO SAUDE UNIMED SP",
    "Empresa 6": "06 - ESPAÇO SAUDE UNIMED SP",
    "Empresa 08": "08 - ESPACO UNIMED BRASILIA",
    "Empresa 8": "08 - ESPACO UNIMED BRASILIA",
    "Empresa 09": "09 - TEA TATUAPE",
    "Empresa 9": "09 - TEA TATUAPE",
    "Empresa 10": "10 - ESPAÇO UNIMED SALVADOR",
    "Empresa 11": "11 - LABORATORIO PATIO BRASIL BRASILIA",
    "Empresa 12": "12 - LABORATORIO ASA SUL BRASILIA",
    "Empresa 13": "13 - LABORATORIO ASA NORTE BRASILIA",
    "Empresa 14": "14 - LABORATORIO GAMA BRASILIA",
    "Empresa 15": "15 - LABORATORIO AGUAS CLARAS BRASILIA",
    "Empresa 16": "16 - LABORATORIO RIACHO FUNDO BRASILIA",
    "Empresa 17": "17 - LABORATORIO SOBRADINHO BRASILIA",
    "Empresa 19": "19 - UNIMED CUIDAR MAIS MANAUS",
    "Empresa 20": "20 - LABORATORIO CEILANDIA NORT BRASILIA",
    "Empresa 21": "21 - LABORATORIO SAMAMBAIA SUL BRASILIA",
}

# 4. Lista oficial dos módulos solicitados
MODULOS_OFICIAIS = [
    "URGÊNCIA E EMERGÊNCIA",
    "CENTRAL DE MARCAÇÕES",
    "AMBULATÓRIO",
    "INTERNAÇÃO",
    "ESTOQUE",
    "Totem Senha (todos)",
    "Painel (todos)",
    "CLASSIFICAÇÃO DE RISCO",
    "PRONTUÁRIO ELETRÔNICO - PEP",
    "MOVIMENTAÇÃO DE DOCUMENTOS",
    "AMAP - SAME",
    "PEDIDOS DE IMAGEM",
    "PEDIDOS DE LABORATÓRIO",
    "COMPRAS",
    "GIW",
    "EDITOR 2",
    "REPORT DESIGNER",
    "REPASSE",
    "NUTRIÇÃO",
    "FINANCEIRO",
    "CAIXA",
    "PATRIMÔNIO",
    "CME",
    "CONTABILIDADE",
    "CUSTOS",
    "FATURAMENTO DE CONVÊNIOS",
    "SGU - APOIO A TI",
    "CENTRO CIRUGICO",
]


def normalizar(texto):
  if not texto or pd.isna(texto):
    return ""
  txt = str(texto).strip().upper()
  return "".join(
      c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn"
  )


ALIASES_MODULOS = {
    "URGENCIA E EMERGENCIA": "URGÊNCIA E EMERGÊNCIA",
    "PAEU": "URGÊNCIA E EMERGÊNCIA",
    "CENTRAL DE MARCACOES": "CENTRAL DE MARCAÇÕES",
    "CENTRAL DE MARCACAO": "CENTRAL DE MARCAÇÕES",
    "AMBULATORIO": "AMBULATÓRIO",
    "INTERNACAO": "INTERNAÇÃO",
    "ESTOQUE": "ESTOQUE",
    "TOTEM SENHA": "Totem Senha (todos)",
    "TOTEM SENHA (TODOS)": "Totem Senha (todos)",
    "TOTEM": "Totem Senha (todos)",
    "PAINEL": "Painel (todos)",
    "PAINEL (TODOS)": "Painel (todos)",
    "CLASSIFICACAO DE RISCO": "CLASSIFICAÇÃO DE RISCO",
    "PRONTUARIO ELETRONICO - PEP": "PRONTUÁRIO ELETRÔNICO - PEP",
    "PRONTUARIO ELETRONICO": "PRONTUÁRIO ELETRÔNICO - PEP",
    "PEP": "PRONTUÁRIO ELETRÔNICO - PEP",
    "MOVIMENTACAO DE DOCUMENTOS": "MOVIMENTAÇÃO DE DOCUMENTOS",
    "AMAP - SAME": "AMAP - SAME",
    "AMAP": "AMAP - SAME",
    "SAME": "AMAP - SAME",
    "PEDIDOS DE IMAGEM": "PEDIDOS DE IMAGEM",
    "IMAGEM": "PEDIDOS DE IMAGEM",
    "PEDIDOS DE LABORATORIO": "PEDIDOS DE LABORATÓRIO",
    "LABORATORIO": "PEDIDOS DE LABORATÓRIO",
    "COMPRAS": "COMPRAS",
    "GIW": "GIW",
    "EDITOR 2": "EDITOR 2",
    "EDITOR": "EDITOR 2",
    "REPORT DESIGNER": "REPORT DESIGNER",
    "REPASSE": "REPASSE",
    "NUTRICAO": "NUTRIÇÃO",
    "FINANCEIRO": "FINANCEIRO",
    "CAIXA": "CAIXA",
    "PATRIMONIO": "PATRIMÔNIO",
    "CME": "CME",
    "CONTABILIDADE": "CONTABILIDADE",
    "CUSTOS": "CUSTOS",
    "FATURAMENTO DE CONVENIOS": "FATURAMENTO DE CONVÊNIOS",
    "FATURAMENTO": "FATURAMENTO DE CONVÊNIOS",
    "SGU - APOIO A TI": "SGU - APOIO A TI",
    "SGU": "SGU - APOIO A TI",
    "CENTRO CIRUGICO": "CENTRO CIRUGICO",
    "CENTRO CIRURGICO": "CENTRO CIRUGICO",
}


def identificar_linha(item_norm, sys_ok_norm, stat_norm):
  if "RESPONSAVEL" in item_norm or "HOMOLOGACAO" in item_norm:
    return "IGNORAR"

  if item_norm in ALIASES_MODULOS:
    return ALIASES_MODULOS[item_norm]

  if not sys_ok_norm and not stat_norm:
    for alias_key, mod_oficial in ALIASES_MODULOS.items():
      if len(alias_key) >= 4 and (
          alias_key in item_norm or item_norm in alias_key
      ):
        return mod_oficial
    return "SUBTITULO"

  return "ITEM"


def classificar_status_row(row):
  stat_norm = normalizar(row.get("status", ""))
  sys_norm = normalizar(row.get("Sistema OK?", ""))

  # 1. Se a coluna 'status' OU 'Sistema OK?' começar por NAO SE APLICA
  if stat_norm.startswith("NAO SE APLICA") or sys_norm.startswith("NAO SE APLICA"):
    return "NÃO SE APLICA"

  # 2. Se for VALIDADO
  if stat_norm == "VALIDADO":
    return "VALIDADO"

  # 3. Se estiver em branco
  if stat_norm in ["", "NAN", "NONE"]:
    return "NÃO INICIADO"

  # 4. Qualquer outro valor diferente de VALIDADO, em branco e iniciado por NAO SE APLICA
  return "IMPEDIMENTO"


def extrair_id(url):
  match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
  return match.group(1) if match else None


@st.cache_data(ttl=300)
def carregar_dados_online(url_planilha):
  doc_id = extrair_id(url_planilha)
  if not doc_id:
    st.error("Link da planilha inválido.")
    return pd.DataFrame()

  export_url = (
      f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=xlsx"
  )
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

  try:
    resp = requests.get(export_url, headers=headers, timeout=30)
    xls = pd.ExcelFile(io.BytesIO(resp.content))
  except Exception as e:
    st.error(f"Erro ao carregar a planilha online: {e}")
    return pd.DataFrame()

  dfs = []

  for aba in xls.sheet_names:
    aba_limpa = aba.strip()
    if aba_limpa in mapa_empresas:
      nome_empresa = mapa_empresas[aba_limpa]
      df_temp = pd.read_excel(xls, sheet_name=aba, header=None)

      header_idx = df_temp[
          df_temp.apply(lambda row: "Itens" in row.values, axis=1)
      ].index

      if not header_idx.empty:
        df = df_temp.iloc[header_idx[0] + 1 :].reset_index(drop=True)
        df.columns = df_temp.iloc[header_idx[0]]
        df.columns = [str(c).strip() for c in df.columns]

        if "Itens" not in df.columns or "status" not in df.columns:
          continue

        df["Modulo"] = None
        modulo_atual = None

        for idx, row in df.iterrows():
          item_raw = str(row["Itens"]).strip()
          if item_raw in ["nan", "None", ""]:
            continue

          item_norm = normalizar(item_raw)
          sys_ok_norm = normalizar(row.get("Sistema OK?", ""))
          stat_norm = normalizar(row.get("status", ""))

          tipo = identificar_linha(item_norm, sys_ok_norm, stat_norm)

          if tipo == "IGNORAR":
            continue
          elif tipo == "SUBTITULO":
            continue
          elif tipo in MODULOS_OFICIAIS:
            modulo_atual = tipo
            continue
          elif tipo == "ITEM":
            if modulo_atual:
              df.at[idx, "Modulo"] = modulo_atual

        df = df.dropna(subset=["Modulo", "Itens"])
        df = df[
            ~df["Itens"]
            .astype(str)
            .str.contains(
                "Responsável pela homologação|responsavel|homologacao",
                case=False,
                na=False,
                regex=True,
            )
        ]

        # Classificação por linha considerando 'status' e 'Sistema OK?'
        df["Status Final"] = df.apply(classificar_status_row, axis=1)
        df["Empresa"] = nome_empresa

        dfs.append(df[["Empresa", "Modulo", "Itens", "Status Final"]])

  if dfs:
    return pd.concat(dfs, ignore_index=True)
  return pd.DataFrame()


SHEET_URL = "https://docs.google.com/spreadsheets/d/1i8GDwchv0BNnj9cmecr81INuh8kbbSZ8/edit?usp=sharing"

with st.spinner("A carregar informações em tempo real da planilha..."):
  dados = carregar_dados_online(SHEET_URL)

if dados.empty:
  st.warning("Nenhum dado encontrado para os módulos especificados.")
  st.stop()

# 5. Filtro lateral por Empresa
st.sidebar.title("Empresas")
empresas_disponiveis = sorted(dados["Empresa"].unique())
empresa_selecionada = st.sidebar.selectbox(
    "Selecione a Empresa", empresas_disponiveis
)

df_filtrado = dados[dados["Empresa"] == empresa_selecionada]

st.markdown(
    f"<h2 style='text-align: center; color: #0066cc;'>{empresa_selecionada}</h2>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

color_map = {
    "VALIDADO": "#28a745",       # Verde
    "NÃO INICIADO": "#6c757d",   # Cinza
    "IMPEDIMENTO": "#dc3545",    # Vermelho
    "NÃO SE APLICA": "#17a2b8",  # Azul
}

modulos_presentes = [
    m for m in MODULOS_OFICIAIS if m in df_filtrado["Modulo"].unique()
]

cols = st.columns(2)

for idx, modulo in enumerate(modulos_presentes):
  df_mod = df_filtrado[df_filtrado["Modulo"] == modulo]

  if df_mod.empty:
    continue

  contagem = df_mod["Status Final"].value_counts().reset_index()
  contagem.columns = ["Status Final", "Quantidade"]

  fig = px.pie(
      contagem,
      values="Quantidade",
      names="Status Final",
      title=f"<b>Módulo: {modulo}</b>",
      color="Status Final",
      color_discrete_map=color_map,
      hole=0.4,
  )

  fig.update_traces(
      textposition="inside",
      textinfo="percent+value",
      hovertemplate=(
          "<b>%{label}</b><br>Quantidade: %{value}<br>Percentual:"
          " %{percent}<extra></extra>"
      ),
  )

  fig.update_layout(
      margin=dict(t=50, b=20, l=20, r=20),
      legend=dict(
          orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
      ),
  )

  col_target = cols[idx % 2]
  with col_target:
    st.plotly_chart(fig, use_container_width=True)