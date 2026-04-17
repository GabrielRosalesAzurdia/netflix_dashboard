import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Netflix Analytics", layout="wide", page_icon="🎬")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #F0F2F8; }
.block-container { padding: 1.5rem 2.5rem 2rem 2.5rem !important; max-width: 1400px; }
.header-banner {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1.5rem;
}
.header-title { color:#fff; font-size:2rem; font-weight:700; margin:0; letter-spacing:-0.5px; }
.header-sub   { color:#A0AEC0; font-size:0.95rem; margin:0.25rem 0 0 0; }
.header-badge {
    background: linear-gradient(135deg, #E94560, #C62A47); color:white;
    padding:0.4rem 1rem; border-radius:20px; font-size:0.8rem;
    font-weight:600; letter-spacing:0.5px; margin-left:auto;
}
.kpi-card {
    background:white; border-radius:14px; padding:1.4rem 1.6rem;
    box-shadow:0 2px 12px rgba(0,0,0,0.07); border-left:5px solid;
}
.kpi-label { font-size:0.78rem; font-weight:600; text-transform:uppercase; letter-spacing:0.8px; color:#718096; margin-bottom:0.4rem; }
.kpi-value { font-size:2.1rem; font-weight:700; line-height:1; }
.kpi-icon  { font-size:1.6rem; margin-bottom:0.6rem; }
.sec-title {
    font-size:1.1rem; font-weight:700; color:#1A202C;
    margin:1.8rem 0 0.8rem 0;
    border-bottom: 2px solid #E94560;
    padding-bottom: 0.4rem;
}
#MainMenu, footer, header { visibility:hidden; }
            
/* Labels de filtros */
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label {
    color: #1A202C !important;
    font-weight: 500;
}

/* Texto seleccionado dentro del selectbox */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #1A202C !important;
}

/* Valor del slider */
div[data-testid="stSlider"] p {
    color: #1A202C !important;
}
</style>
""", unsafe_allow_html=True)


# ── DATOS ─────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar():
    p = "Netflix_Titulos.xlsx"
    t  = pd.read_excel(p, sheet_name="netflix_titulos")
    d  = pd.read_excel(p, sheet_name="netflix_titulos_directores")
    pa = pd.read_excel(p, sheet_name="netflix_titulos_paises")
    c  = pd.read_excel(p, sheet_name="netflix_titulos_categoria")
    return t, d, pa, c

titulos, directores, paises, categorias = cargar()
titulos = titulos[titulos["año_lanzamiento"].notna() & titulos["año_lanzamiento"].between(1940, 2025)]
titulos["año_lanzamiento"] = titulos["año_lanzamiento"].astype(int)


# ── CONFIGURACIÓN BASE DE GRÁFICOS ────────────────────────────────────────────
NEGRO       = "#1A202C"
GRIS_TEXTO  = "#374151"
GRID_COLOR  = "#E8ECF0"
LINE_COLOR  = "#D1D5DB"

# Ejes reutilizables con texto negro
def eje(size=11, **kwargs):
    return dict(
        gridcolor=GRID_COLOR,
        linecolor=LINE_COLOR,
        tickfont=dict(size=size, color=NEGRO),
        title_font=dict(size=12, color=NEGRO),
        **kwargs
    )

def base_layout(title, height, extra=None):
    cfg = dict(
        title=dict(text=title, font=dict(size=15, color=NEGRO, family="Inter, sans-serif"), x=0.02),
        font=dict(family="Inter, sans-serif", size=12, color=NEGRO),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=50, b=35, l=15, r=15),
        height=height,
    )
    if extra:
        cfg.update(extra)
    return cfg

ESCALA_PURP = [[0,"#EDE9FF"],[0.5,"#6C63FF"],[1,"#2D1B8E"]]
ESCALA_TEAL = [[0,"#CCFBF1"],[0.5,"#2EC4B6"],[1,"#0D7A74"]]
ESCALA_WARM = [[0,"#FFF3CD"],[0.5,"#F7971E"],[1,"#C05C00"]]


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div>
  <div>
    <p class="header-title">Netflix Analytics Dashboard</p>
    <p class="header-sub">Análisis del catálogo global de contenido en la plataforma</p>
  </div>
  <div class="header-badge">ANÁLISIS DE DATOS</div>
</div>
""", unsafe_allow_html=True)


# ── FILTROS ───────────────────────────────────────────────────────────────────
f1, f2 = st.columns([1, 3])
with f1:
    tipo_sel = st.selectbox("Tipo de contenido", ["Todos"] + sorted(titulos["Tipo"].dropna().unique().tolist()))
with f2:
    año_min = int(titulos["año_lanzamiento"].min())
    año_max = int(titulos["año_lanzamiento"].max())
    rango   = st.slider("Año de lanzamiento", año_min, año_max, (2000, año_max))

df = titulos.copy()
if tipo_sel != "Todos":
    df = df[df["Tipo"] == tipo_sel]
df = df[df["año_lanzamiento"].between(rango[0], rango[1])]


# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Indicadores Clave</p>', unsafe_allow_html=True)

kpis = [
    ("", "Total Títulos",  f"{len(df):,}",                             "#6C63FF"),
    ("", "Películas",       f"{len(df[df['Tipo']=='Movie']):,}",         "#E94560"),
    ("", "Series",          f"{len(df[df['Tipo']=='TV Show']):,}",        "#2EC4B6"),
    ("", "Años Cubiertos",  str(df["año_lanzamiento"].nunique()),         "#F7971E"),
]
for col, (icon, label, val, color) in zip(st.columns(4), kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="color:{color}">{val}</div>
        </div>""", unsafe_allow_html=True)


# ── DONA + LÍNEA ──────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Distribución de Contenido · Evolución por Año</p>', unsafe_allow_html=True)
c1, c2 = st.columns([1, 2])

with c1:
    tc = titulos["Tipo"].value_counts().reset_index()
    tc.columns = ["Tipo", "Cantidad"]
    fig = go.Figure(go.Pie(
        labels=tc["Tipo"], values=tc["Cantidad"], hole=0.58,
        marker=dict(colors=["#6C63FF","#E94560"], line=dict(color="white", width=3)),
        textinfo="label+percent",
        textfont=dict(size=13, color=NEGRO),
        hovertemplate="<b>%{label}</b><br>%{value:,} títulos<br>%{percent}<extra></extra>"
    ))
    fig.add_annotation(
        text=f"<b>{titulos.shape[0]:,}</b><br><span style='font-size:11px'>títulos</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=16, color=NEGRO)
    )
    fig.update_layout(**base_layout("Películas vs Series", 330, {
        "legend": dict(orientation="h", y=-0.05, x=0.2, font=dict(color=NEGRO, size=12))
    }))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    pa = df.groupby("año_lanzamiento").size().reset_index(name="Cantidad")
    fig = go.Figure(go.Scatter(
        x=pa["año_lanzamiento"], y=pa["Cantidad"],
        mode="lines", line=dict(color="#E94560", width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(233,69,96,0.10)",
        hovertemplate="<b>%{x}</b> → %{y} títulos<extra></extra>"
    ))
    fig.update_layout(**base_layout("Títulos lanzados por año", 330, {
        "xaxis": eje(title="Año"),
        "yaxis": eje(title="Cantidad"),
        "showlegend": False,
        "hovermode": "x unified"
    }))
    st.plotly_chart(fig, use_container_width=True)


# ── PAÍSES ────────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Países con Más Títulos</p>', unsafe_allow_html=True)
top_p = paises["Pais"].value_counts().head(15).reset_index()
top_p.columns = ["País", "Títulos"]

pc1, pc2 = st.columns([3, 1])
with pc1:
    fig = go.Figure(go.Bar(
        x=top_p["Títulos"], y=top_p["País"], orientation="h",
        marker=dict(color=top_p["Títulos"], colorscale=ESCALA_PURP,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} títulos<extra></extra>"
    ))
    fig.update_layout(**base_layout("Top 15 Países productores de contenido", 450, {
        "xaxis": eje(title="Cantidad de títulos"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)
with pc2:
    st.markdown("**Ranking**")
    tp = top_p.copy(); tp.index = range(1, len(tp)+1)
    st.dataframe(tp.style.bar(subset=["Títulos"], color="#C7C2FF"), use_container_width=True, height=415)


# ── DIRECTORES ────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Directores con Más Títulos</p>', unsafe_allow_html=True)
top_d = directores["Director"].value_counts().head(15).reset_index()
top_d.columns = ["Director", "Títulos"]

dc1, dc2 = st.columns([3, 1])
with dc1:
    fig = go.Figure(go.Bar(
        x=top_d["Títulos"], y=top_d["Director"], orientation="h",
        marker=dict(color=top_d["Títulos"], colorscale=ESCALA_TEAL,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x} títulos<extra></extra>"
    ))
    fig.update_layout(**base_layout("Top 15 Directores más prolíficos", 450, {
        "xaxis": eje(title="Cantidad de títulos"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)
with dc2:
    st.markdown("**Ranking**")
    td = top_d.copy(); td.index = range(1, len(td)+1)
    st.dataframe(td.style.bar(subset=["Títulos"], color="#99F0EA"), use_container_width=True, height=415)


# ── GÉNEROS ───────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Géneros Más Populares</p>', unsafe_allow_html=True)
top_g = categorias["Listado_en"].value_counts().head(20).reset_index()
top_g.columns = ["Género", "Títulos"]

gc1, gc2 = st.columns([3, 1])
with gc1:
    fig = go.Figure(go.Bar(
        x=top_g["Títulos"], y=top_g["Género"], orientation="h",
        marker=dict(color=top_g["Títulos"], colorscale=ESCALA_WARM,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} títulos<extra></extra>"
    ))
    fig.update_layout(**base_layout("Top 20 Géneros con más contenido", 550, {
        "xaxis": eje(title="Cantidad de títulos"),
        "yaxis": eje(size=10, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)
with gc2:
    st.markdown("**Ranking**")
    tg = top_g.copy(); tg.index = range(1, len(tg)+1)
    st.dataframe(tg.style.bar(subset=["Títulos"], color="#FDE68A"), use_container_width=True, height=515)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;color:#94A3B8;font-size:0.8rem">
    Netflix Analytics Dashboard · Catálogo de títulos · Streamlit & Plotly
</div>
""", unsafe_allow_html=True)