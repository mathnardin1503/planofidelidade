import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

st.set_page_config(
    page_title="Meta Plano Fidelidade – Minerva Foods",
    page_icon="📦",
    layout="wide",
)

# ─── CONSTANTES ───────────────────────────────────────────────────────────────

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}
MESES_ORDER = list(MESES_PT.values())

SIGLAS_ESTADO = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM",
    "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF",
    "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA",
    "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
    "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE",
    "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR",
    "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE",
    "Tocantins": "TO",
}

# Mapeamento: nome normalizado (igual ao Meta) → palavras-chave no nome jurídico (Realizado)
CARRIER_KEYWORDS: dict[str, list[str]] = {
    "Transrima":         ["TRANSRIMA"],
    "Framento":          ["FRAMENTO"],
    "Prodelog":          ["PRODELOG"],
    "Kothe":             ["KOTHE"],
    "Lunardi":           ["LUNARDI"],
    "Marvel":            ["MARVEL"],
    "Hergert":           ["HERGERT"],
    "Cavalheiro":        ["CAVALHEIRO"],
    "Brehm":             ["BREHM"],
    "Canarinho":         ["CANARINHO"],
    "Cootracap":         ["COOTRACAP"],
    "Cootravale":        ["COOTRAVALE"],
    "Cordenonsi":        ["CORDENONSI"],
    "Crismara":          ["CRISMARA"],
    "Friron":            ["FRIRON"],
    "Horizonte Frios":   ["HORIZONTE FRIOS"],
    "Jahnel":            ["JAHNEL"],
    "Lanidir":           ["LANIDIR"],
    "Maroni":            ["MARONI"],
    "Maroso":            ["MAROSO"],
    "Piraju":            ["PIRAJU"],
    "SGT":               ["SGT"],
    "Takahara":          ["TAKAHARA"],
    "Top":               ["TOP DISTRIBUIDORA"],
    "Tozzo":             ["TOZZO"],
    "Transcol":          ["TRANSCOL"],
    "Transjardinopolis": ["TRANSJARDINOPOLIS"],
    "Transpanorama":     ["TRANSPANORAMA"],
    "Tremea":            ["TREMEA"],
    "Vicon":             ["VICON"],
    "Vizotto":           ["VIZZOTTO", "VIZOTTO"],
    "Xap":               ["XAP"],
    "Zilli":             ["ZILLI"],
    "Zili":              ["ZILI"],
    "Continental":       ["CONTINENTAL"],
    "Avanti":            ["AVANTI"],
    "B2":                ["B2 "],
    "Carvalima":         ["CARVALIMA"],
    "Dal Pizzol":        ["DAL PIZZOL"],
    "Dalastra":          ["DALASTRA"],
    "Everson":           ["EVERSON"],
    "Orlando":           ["ORLANDO"],
    "Orlato":            ["ORLATO"],
    "Pedra Ferro":       ["PEDRA FERRO"],
    "Rosso":             ["ROSSO"],
    "TP":                ["TP "],
    "Volce":             ["VOLCE"],
    "Crivilin":          ["CRIVILIN"],
}

# Variantes TAB DIF. consolidam no mesmo nome base
TAB_DIF_MAP = {
    "FRAMENTO - TAB DIF.": "Framento",
    "PRODELOG - TAB DIF.": "Prodelog",
    "LUNARDI - TAB DIF.":  "Lunardi",
    "MARVEL - TAB DIF.":   "Marvel",
    "HERGERT - TAB DIF.":  "Hergert",
}

EMPRESA_ESTADO: dict[str, str] = {
    "FORTUNCERES (AGE)":  "Rio Grande do Sul",
    "FORTUNCERES (BGE)":  "Rio Grande do Sul",
    "FORTUNCERES (BTU)":  "Mato Grosso do Sul",
    "FORTUNCERES (CGA)":  "Rondônia",
    "FORTUNCERES (MNS)":  "Goiás",
    "FORTUNCERES (PLA)":  "Mato Grosso",
    "FORTUNCERES (SGL)":  "Rio Grande do Sul",
    "FORTUNCERES (TGA)":  "Mato Grosso",
    "MINERVA (AR)":       "Tocantins",
    "MINERVA (BT)":       "São Paulo",
    "MINERVA (JB)":       "São Paulo",
    "MINERVA (JNB)":      "Minas Gerais",
    "MINERVA (PG)":       "Goiás",
    "MINERVA S.A. (MFI)": "São Paulo",
    "MINERVA S.A. (MO)":  "Mato Grosso",
    "MINERVA S.A. (PRN)": "Mato Grosso",
    "MINERVA S.A. (RM)":  "Rondônia",
    "MINERVA S/A (AQ)":   "São Paulo",
}

# ─── CARREGAMENTO ─────────────────────────────────────────────────────────────

@st.cache_data
def load_metas() -> pd.DataFrame:
    df = pd.read_excel("data/Metasplano.xlsx")
    df["Ano"] = df["DataBase"].dt.year.astype(int)
    df["Nome do Mês"] = df["DataBase"].dt.month.map(MESES_PT)
    df["Transportadora_norm"] = df["Transportadora"].replace(TAB_DIF_MAP)
    return df


def _normalize_transportador(row: pd.Series) -> str:
    tipo    = str(row.get("Tipo de Contratação", ""))
    veiculo = str(row.get("Veículo", "")).upper()
    nome    = str(row.get("Transportador", "")).upper()

    if tipo == "Dedicada":
        return "DEDICADO - BITRUCK" if "BITRUCK" in veiculo else "DEDICADO - CARRETA"
    if tipo == "Spot":
        return "SPOT - BITRUCK" if "BITRUCK" in veiculo else "SPOT - CARRETA"

    for norm, keywords in CARRIER_KEYWORDS.items():
        if any(kw in nome for kw in keywords):
            return norm

    return row.get("Transportador", "Outros")


@st.cache_data(ttl=3600, show_spinner="Carregando, Aguarde...")
def load_realizado() -> pd.DataFrame:
    pasta_local = Path("data/cargas/")
    pasta_rede  = Path(r"\\btserver001\CSC_Transportes\Primária\Gestão\Matheus Nardin\Bases de Dados\Base Frete Power BI")

    if pasta_local.exists() and any(pasta_local.glob("*.xlsx")):
        pasta = pasta_local
    else:
        pasta = pasta_rede

    arquivos = [
        f for f in pasta.glob("*.xlsx")
        if not f.name.startswith("~$")
        and "2025" not in f.name
    ]
    if not arquivos:
        st.error("Nenhum arquivo .xlsx encontrado na pasta de rede.")
        st.stop()
    df = pd.concat([pd.read_excel(f) for f in arquivos], ignore_index=True)
    st.write("Total linhas brutas:", len(df))
    st.write("Meses encontrados:", df["Dta. Carga"].dt.month.value_counts().to_dict() if "Dta. Carga" in df.columns else "coluna não encontrada")
    df["Dta. Carga"] = pd.to_datetime(df["Dta. Carga"], errors="coerce")
    df = df[~df["Empresa"].astype(str).str.startswith("Total")]
    df = df[~df["Empresa"].astype(str).str.startswith("Filtros aplicados")]
    df = df[df["Empresa"].astype(str).str.strip() != "nan"]
    df["Estado"] = df["Empresa"].map(EMPRESA_ESTADO)
    junho = df[df["Dta. Carga"].dt.month == 6]
    st.write("Junho antes do filtro Estado:", len(junho))
    st.write("Empresas de Junho sem mapeamento:", junho[junho["Estado"].isna()]["Empresa"].unique().tolist())
    df = df[df["Estado"].notna()]
    df = df[df["Dta. Carga"].notna()].copy()
    df["Ano"] = df["Dta. Carga"].dt.year.astype(int)
    df["Nome do Mês"] = df["Dta. Carga"].dt.month.map(MESES_PT)
    df["Transportadora_norm"] = df.apply(_normalize_transportador, axis=1)
    df = df.drop_duplicates(subset=["Empresa", "Carga CF"])
    junho_apos = df[df["Dta. Carga"].dt.month == 6]
    st.write("Junho após drop_duplicates:", len(junho_apos))
    st.write("Transportadoras de Junho:", junho_apos["Transportadora_norm"].value_counts().to_dict())
    df["Qtd_Cargas"] = 1
    return df


# ─── FILTROS ──────────────────────────────────────────────────────────────────

def apply_filters(df: pd.DataFrame, ano: int, mes: str, estados: list = None, col_estado: str = None) -> pd.DataFrame:
    df = df[df["Ano"] == ano]
    if mes != "Todos":
        df = df[df["Nome do Mês"] == mes]
    if estados and col_estado and col_estado in df.columns:
        df = df[df[col_estado].isin(estados)]
    return df


# ─── KPIs ─────────────────────────────────────────────────────────────────────

def calc_kpis(df_meta: pd.DataFrame, df_real: pd.DataFrame) -> dict:
    total_meta = df_meta["Meta"].sum()
    total_real = df_real["Qtd_Cargas"].sum()
    return {
        "total_meta":      total_meta,
        "total_realizado": total_real,
        "gap":             total_meta - total_real,
    }


# ─── PIVOTS ───────────────────────────────────────────────────────────────────

def build_pivot(df: pd.DataFrame, value_col: str, index_col: str, columns_col: str) -> pd.DataFrame:
    grp = df.groupby([index_col, columns_col])[value_col].sum().reset_index()
    pivot = grp.pivot(index=index_col, columns=columns_col, values=value_col).fillna(0)
    pivot.columns.name = None
    pivot.index.name = None
    pivot.rename(columns=SIGLAS_ESTADO, inplace=True)
    pivot["Total"] = pivot.sum(axis=1)
    pivot.loc["TOTAL"] = pivot.sum(axis=0)
    return pivot


def build_gap_pivot(pivot_meta: pd.DataFrame, pivot_real: pd.DataFrame) -> pd.DataFrame:
    pm = pivot_meta.drop(index="TOTAL", errors="ignore").drop(columns="Total", errors="ignore")
    pr = pivot_real.drop(index="TOTAL", errors="ignore").drop(columns="Total", errors="ignore")

    # Colunas: união dos estados de ambos; linhas: somente transportadoras da meta
    all_cols = sorted(set(pm.columns) | set(pr.columns))
    meta_rows = sorted(pm.index)

    pm = pm.reindex(index=meta_rows, columns=all_cols, fill_value=0)
    pr = pr.reindex(index=meta_rows, columns=all_cols, fill_value=0)

    gap = pm - pr
    gap["Total"] = gap.sum(axis=1)
    gap.loc["TOTAL"] = gap.sum(axis=0)
    return gap


# ─── FORMATAÇÃO ───────────────────────────────────────────────────────────────

def fmt_br(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


# ─── CSS ──────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #2B3d4a !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
        background-image: url("app/static/conteudo.png");
        background-repeat: no-repeat;
        background-position: bottom left;
        background-size: 400px auto;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: transparent; }
    [data-testid="stSidebar"] {
        background-color: rgba(255,255,255,0.92) !important;
        border-right: 1px solid rgba(43,61,74,0.1);
        min-width: 160px !important;
        max-width: 160px !important;
        width: 160px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0.6rem !important;
    }
    [data-testid="stSidebar"] * {
        font-size: 0.65rem !important;
        white-space: nowrap !important;
    }

    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 1400px; }

    /* Header */
    .dash-header { text-align: center; padding-bottom: 0.25rem; }
    .dash-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem; font-weight: 800;
        color: #2B3d4a; margin: 0; line-height: 1.1;
    }
    .dash-subtitle {
        font-size: 0.75rem; color: #8a9aaa;
        letter-spacing: 0.14em; text-transform: uppercase; margin-top: 0.25rem;
    }
    .dash-divider {
        border: none; border-top: 1px solid rgba(43,61,74,0.1); margin: 0.75rem 0;
    }

    /* Filter labels */
    .filter-label {
        font-size: 0.68rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase;
        color: #2B3d4a; margin-bottom: 0.2rem;
    }

    /* KPI Cards */
    .kpi-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(43,61,74,0.1);
        border-radius: 14px; padding: 1rem 1.25rem;
        border-top-width: 4px;
        box-shadow: 0 2px 12px rgba(43,61,74,0.07);
    }
    .kpi-card-meta    { border-top-color: #e84752 !important; }
    .kpi-card-real    { border-top-color: #2B3d4a !important; }
    .kpi-card-gap-pos { border-top-color: #3B6D11 !important; }
    .kpi-card-gap-neg { border-top-color: #e84752 !important; }

    .kpi-label {
        font-size: 0.68rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;
    }
    .kpi-label-meta    { color: #e84752; }
    .kpi-label-real    { color: #2B3d4a; }
    .kpi-label-gap     { color: #3B6D11; }
    .kpi-label-gap-neg { color: #e84752; }

    .kpi-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem; font-weight: 700; color: #2B3d4a; line-height: 1;
    }
    .kpi-value-pos { color: #3B6D11 !important; }
    .kpi-value-neg { color: #e84752 !important; }
    .kpi-desc { font-size: 0.7rem; color: #8a9aaa; margin-top: 0.35rem; }

    /* Section */
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 0.85rem; font-weight: 700; color: #2B3d4a; margin-bottom: 0.1rem;
    }
    .section-subtitle { font-size: 0.65rem; color: #8a9aaa; margin-bottom: 0.5rem; }

    /* Tables */
    .table-wrapper {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(43,61,74,0.1);
        border-radius: 14px; padding: 0.5rem;
        overflow-x: auto; overflow-y: auto;
        max-height: 220px;
        margin-bottom: 0;
        box-shadow: 0 2px 12px rgba(43,61,74,0.06);
    }
    table.dash-table {
        table-layout: fixed; width: 100%; border-collapse: collapse; font-size: 0.52rem;
    }
    table.dash-table thead tr th {
        position: sticky; top: 0; z-index: 1;
    }
    table.dash-table th {
        background: #2B3d4a;
        color: #ffffff; font-size: 0.48rem;
        font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
        padding: 0.15rem 0.15rem; text-align: left;
        border-bottom: 1px solid rgba(43,61,74,0.1);
        white-space: nowrap;
        position: sticky; top: 0; z-index: 1;
        overflow: hidden; text-overflow: ellipsis;
    }
    table.dash-table td {
        padding: 0.15rem 0.15rem; color: #2B3d4a;
        font-size: 0.48rem;
        text-align: left; border-bottom: none;
        white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis;
    }
    table.dash-table td:first-child { color: #2B3d4a; font-weight: 500; }
    table.dash-table tbody tr:nth-child(odd)  td { background: rgba(255,255,255,0.8); }
    table.dash-table tbody tr:nth-child(even) td { background: rgba(240,237,224,0.8); }
    table.dash-table tr:last-child td {
        border-top: 1px solid rgba(43,61,74,0.1);
        font-weight: 700; color: #2B3d4a;
        background: #f5f2e8 !important;
    }
    table.dash-table tr:hover td { background: rgba(232,71,82,0.05) !important; }
    table.dash-table th:hover { background: #1a2830; cursor: pointer; }

    /* GAP colors */
    .c-pos { color: #3B6D11 !important; font-weight: 600; }
    .c-neg { color: #e84752 !important; font-weight: 600; }

    /* Footer */
    .dash-footer {
        text-align: center; font-size: 0.7rem; color: #8a9aaa;
        padding: 1.5rem 0 0.5rem;
        border-top: 1px solid rgba(43,61,74,0.08);
        margin-top: 1rem;
    }

    /* Selectbox + Multiselect */
    div[data-baseweb="select"] > div {
        background-color: #f5f2e8 !important;
        border: 1.5px solid rgba(43,61,74,0.25) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] [data-testid="stSelectboxValue"] {
        color: #2B3d4a !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
    }
    span[data-baseweb="tag"] {
        background-color: rgba(232,71,82,0.10) !important;
        border: 1px solid rgba(232,71,82,0.30) !important;
        border-radius: 6px !important;
    }
    span[data-baseweb="tag"] span { color: #e84752 !important; font-weight: 600 !important; }
    ul[data-baseweb="menu"] { background-color: #f5f2e8 !important; }
    ul[data-baseweb="menu"] li { color: #2B3d4a !important; }
    ul[data-baseweb="menu"] li:hover { background-color: rgba(232,71,82,0.07) !important; }
    </style>
    """, unsafe_allow_html=True)


# ─── COMPONENTES VISUAIS ──────────────────────────────────────────────────────

def render_header():
    st.markdown("""
    <div class="dash-header">
        <div class="dash-title">📦 Meta Plano Fidelidade</div>
        <div class="dash-subtitle">Minerva Foods &nbsp;·&nbsp; Acompanhamento de Cargas por Transportadora</div>
    </div>
    <hr class="dash-divider">
    """, unsafe_allow_html=True)


def render_kpi_cards(kpis: dict):
    meta = kpis["total_meta"]
    real = kpis["total_realizado"]
    gap  = kpis["gap"]

    gap_val_class   = "kpi-value-pos" if gap >= 0 else "kpi-value-neg"
    gap_card_class  = "kpi-card-gap-pos" if gap >= 0 else "kpi-card-gap-neg"
    gap_label_class = "kpi-label-gap" if gap >= 0 else "kpi-label-gap-neg"
    gap_sign        = "+" if gap > 0 else ""
    gap_desc        = "acima da meta" if gap > 0 else ("abaixo da meta" if gap < 0 else "meta atingida exatamente")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-card kpi-card-meta" title="Soma de todas as cargas previstas no período selecionado">
            <div class="kpi-label kpi-label-meta">Total de Cargas Meta</div>
            <div class="kpi-value">{fmt_br(meta)}</div>
            <div class="kpi-desc">cargas previstas</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card kpi-card-real" title="Soma de todas as cargas efetivamente realizadas">
            <div class="kpi-label kpi-label-real">Total de Cargas Realizadas</div>
            <div class="kpi-value">{fmt_br(real)}</div>
            <div class="kpi-desc">cargas realizadas</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card {gap_card_class}" title="Diferença: Meta − Realizado">
            <div class="kpi-label {gap_label_class}">GAP (Meta − Realizado)</div>
            <div class="kpi-value {gap_val_class}">{gap_sign}{fmt_br(gap)}</div>
            <div class="kpi-desc">{gap_desc}</div>
        </div>""", unsafe_allow_html=True)


def _pivot_to_html(pivot: pd.DataFrame, conditional: bool = False, table_id: str = "table") -> str:
    cols = list(pivot.columns)
    headers = f'<th style="width:55px; max-width:55px; min-width:55px; cursor:pointer;" onclick="sortTable(\'{table_id}\', 0)">TRANSP.</th>'
    for i, c in enumerate(cols):
        headers += f'<th style="width:26px; min-width:24px; max-width:28px; cursor:pointer;" onclick="sortTable(\'{table_id}\', {i+1})">{c}</th>'

    rows_html = ""
    TOTAL_STYLE = "background:#2B3d4a !important; color:#ffffff !important; font-weight:700;"
    for idx, row in pivot.iterrows():
        is_total = str(idx) == "TOTAL"
        row_style = TOTAL_STYLE if is_total else ""
        label = f"<b>{idx}</b>" if is_total else f'<span title="{idx}">{idx}</span>'
        cells = f'<td style="width:55px; max-width:55px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; {row_style}">{label}</td>'
        for col in cols:
            val     = row[col]
            val_fmt = fmt_br(val)
            is_total_col = col == "Total"
            if is_total or is_total_col:
                cells += f'<td style="{TOTAL_STYLE}">{val_fmt}</td>'
            elif conditional:
                css = "c-pos" if val >= 0 else "c-neg"
                cells += f'<td class="{css}">{val_fmt}</td>'
            else:
                cells += f"<td>{val_fmt}</td>"
        rows_html += f"<tr>{cells}</tr>"

    return f"""
    <table class="dash-table" id="{table_id}">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <script>
    function sortTable(tableId, col) {{
        var table = document.getElementById(tableId);
        var tbody = table.querySelector('tbody');
        var rows = Array.from(tbody.querySelectorAll('tr'));
        var totalRow = rows.find(r => r.querySelector('td b'));
        var dataRows = rows.filter(r => !r.querySelector('td b'));
        var asc = table.getAttribute('data-sort-col') == col && table.getAttribute('data-sort-dir') == 'asc';
        dataRows.sort(function(a, b) {{
            var aVal = a.cells[col].innerText.replace(/\\./g,'').replace('+','').trim();
            var bVal = b.cells[col].innerText.replace(/\\./g,'').replace('+','').trim();
            var aNum = parseFloat(aVal);
            var bNum = parseFloat(bVal);
            if (!isNaN(aNum) && !isNaN(bNum)) return asc ? bNum - aNum : aNum - bNum;
            return asc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
        }});
        tbody.innerHTML = '';
        dataRows.forEach(r => tbody.appendChild(r));
        if (totalRow) tbody.appendChild(totalRow);
        table.setAttribute('data-sort-col', col);
        table.setAttribute('data-sort-dir', asc ? 'desc' : 'asc');
    }}
    </script>"""


def render_table(pivot: pd.DataFrame, title: str, subtitle: str, conditional: bool = False, print_mode: bool = False, table_id: str = "table"):
    table_html = _pivot_to_html(pivot, conditional=conditional, table_id=table_id)
    wrapper_style = "max-height: none; overflow-y: visible;" if print_mode else "max-height: 220px; overflow-y: auto;"
    st.markdown(f"""
    <div class="section-title">{title}</div>
    <div class="section-subtitle">{subtitle}</div>
    <div class="table-wrapper" style="{wrapper_style}">{table_html}</div>
    """, unsafe_allow_html=True)


def render_detalhe_table(df: pd.DataFrame):
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join(f'<td style="text-align:left">{row[c]}</td>' for c in df.columns)
        rows_html += f"<tr>{cells}</tr>"
    st.markdown(f"""
    <div class="table-wrapper" style="max-height:290px; overflow-y:auto;">
        <table class="dash-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    today = date.today().strftime("%d/%m/%Y")
    st.markdown(
        f'<div class="dash-footer">Dados reais &nbsp;—&nbsp; atualizado em {today}</div>',
        unsafe_allow_html=True,
    )


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    inject_css()
    st.markdown('<div style="background:#e84752;height:6px;width:100%;margin-bottom:0;"></div>', unsafe_allow_html=True)
    render_header()

    df_meta = load_metas()
    df_real = load_realizado()

    anos_meta = set(df_meta["Ano"].dropna().unique())
    anos_real = set(df_real["Ano"].dropna().unique())
    anos = sorted(anos_meta | anos_real, reverse=True)

    # ── Sidebar com todos os filtros ──────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="filter-label">Ano</div>', unsafe_allow_html=True)
        ano_sel = st.selectbox("Ano", anos, label_visibility="collapsed")

        meses_no_ano = [
            m for m in MESES_ORDER
            if m in set(df_meta[df_meta["Ano"] == ano_sel]["Nome do Mês"])
            or m in set(df_real[df_real["Ano"] == ano_sel]["Nome do Mês"])
        ]

        st.markdown('<div class="filter-label" style="margin-top:0.75rem">Mês</div>', unsafe_allow_html=True)
        mes_sel = st.selectbox("Mês", ["Todos"] + meses_no_ano, label_visibility="collapsed")

        estados_disp = sorted(set(
            df_meta["Região"].dropna().unique().tolist() +
            df_real["Estado"].dropna().unique().tolist()
        ))
        st.markdown('<div class="filter-label" style="margin-top:0.75rem">Estado</div>', unsafe_allow_html=True)
        estados_sel = st.multiselect(
            "Estado",
            options=estados_disp,
            default=[],
            placeholder="Todos...",
            label_visibility="collapsed",
        )

        meta_f = apply_filters(df_meta, ano_sel, mes_sel, estados_sel, "Região")
        real_f = apply_filters(df_real, ano_sel, mes_sel, estados_sel, "Estado")

        transportadoras_com_meta = sorted(
            meta_f[meta_f["Meta"] > 0]["Transportadora_norm"].unique()
        )

        st.markdown('<div class="filter-label" style="margin-top:0.75rem">Transportadora</div>', unsafe_allow_html=True)
        trans_sel = st.multiselect(
            "Transportadora",
            options=transportadoras_com_meta,
            default=[],
            placeholder="Todas",
            label_visibility="collapsed",
        )

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()

    # ── Aplica filtros nos dados ───────────────────────────────────────────────
    meta_f = meta_f[meta_f["Transportadora_norm"].isin(transportadoras_com_meta)]
    real_f = real_f[real_f["Transportadora_norm"].isin(transportadoras_com_meta)]

    if trans_sel:
        meta_f = meta_f[meta_f["Transportadora_norm"].isin(trans_sel)]
        real_f = real_f[real_f["Transportadora_norm"].isin(trans_sel)]

    # KPIs
    kpis = calc_kpis(meta_f, real_f)
    render_kpi_cards(kpis)

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

    # Aviso se não há dados
    if meta_f.empty and real_f.empty:
        st.warning("Nenhum dado encontrado para o período selecionado.")
        render_footer()
        return

    # Modo Print
    if "print_mode" not in st.session_state:
        st.session_state.print_mode = False

    col_btn, _ = st.columns([1, 6])
    with col_btn:
        btn_label = "📊 Modo Normal" if st.session_state.print_mode else "🖨️ Modo Print"
        if st.button(btn_label):
            st.session_state.print_mode = not st.session_state.print_mode
            st.rerun()

    print_mode = st.session_state.print_mode

    # Pivots
    pivot_meta = build_pivot(meta_f, "Meta",            "Transportadora_norm", "Região")
    pivot_real = build_pivot(real_f, "Qtd_Cargas", "Transportadora_norm", "Estado")
    pivot_gap  = build_gap_pivot(pivot_meta, pivot_real)

    col_meta, col_real, col_gap = st.columns(3)
    with col_meta:
        render_table(pivot_meta, "Meta", "Cargas previstas por estado", print_mode=print_mode, table_id="table-meta")
    with col_real:
        render_table(pivot_real, "Realizado", "Cargas realizadas por estado", print_mode=print_mode, table_id="table-real")
    with col_gap:
        render_table(pivot_gap, "GAP (Meta − Realizado)",
                     "Verde = cumprida · Vermelho = abaixo",
                     conditional=True, print_mode=print_mode, table_id="table-gap")

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Cargas Detalhadas</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Últimas cargas registradas no período selecionado</div>', unsafe_allow_html=True)

    colunas_detalhe = ["Empresa", "Estado", "Grp. Rota", "Transportador", "Veículo", "Carga Multi", "Dta. Carga", "Dta. Fatur."]
    colunas_existentes = [c for c in colunas_detalhe if c in real_f.columns]
    df_detalhe = real_f[colunas_existentes].copy()
    df_detalhe["Estado"] = df_detalhe["Estado"].map(SIGLAS_ESTADO).fillna(df_detalhe["Estado"])
    if "Dta. Carga" in df_detalhe.columns:
        df_detalhe["Dta. Carga"] = pd.to_datetime(df_detalhe["Dta. Carga"]).dt.strftime("%d/%m/%Y")
    if "Dta. Fatur." in df_detalhe.columns:
        df_detalhe["Dta. Fatur."] = pd.to_datetime(df_detalhe["Dta. Fatur."]).dt.strftime("%d/%m/%Y")

    render_detalhe_table(df_detalhe)

    render_footer()


if __name__ == "__main__":
    main()
