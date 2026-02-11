import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="Chamonix — Le Sommet en Sursis", page_icon="🦌", layout="wide")

audience_txt = (
    "Audience cible :\n"
    "Gestionnaires d’espaces naturels (parc/réserve/collectivités), acteurs du tourisme (opérateurs, remontées, offices),\n"
    "et équipes terrain (écogardes, suivi faune) dans la vallée de Chamonix / Mont-Blanc.\n"
)

link_txt = (
    "Lien vers la narration (à compléter) :\n"
    "https://...\n"
)

# Palette (décision globale)
C_HUM = "#FF9F1C"   # humains
C_FAU = "#2D6A4F"   # faune
C_ENV = "#60A5FA"   # environnement/flore
C_MUT = "#94A3B8"

# ============================================================
# STYLE / EFFETS (CSS)
# ============================================================
st.markdown("""
<style>
.main { background: radial-gradient(1200px 500px at 12% -10%, rgba(255,159,28,.18), transparent 55%),
                 radial-gradient(1100px 550px at 88% -8%, rgba(45,106,79,.18), transparent 55%),
                 radial-gradient(900px 500px at 50% 120%, rgba(96,165,250,.14), transparent 55%),
                 linear-gradient(180deg, #070b10 0%, #0b1220 100%);
        color: #E5E7EB; }
.block-container { max-width: 1280px; padding-top: 1.3rem; padding-bottom: 3rem; }

h1,h2,h3 { font-family: ui-serif, Georgia, "Times New Roman", serif; letter-spacing: -0.02em; }
h1 { text-align:center; font-size: 3.25rem !important; margin-bottom: .15rem; }
h2 { margin-top: 2rem; border-bottom: 1px solid rgba(255,255,255,0.12); padding-bottom: .55rem; }
h3 { margin-top: .3rem; }

.hero {
  position: relative;
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 1.2rem 1.2rem 1rem 1.2rem;
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
  box-shadow: 0 20px 60px rgba(0,0,0,0.55);
  overflow: hidden;
}
.hero:before{
  content:"";
  position:absolute; inset:-2px;
  background: conic-gradient(from 180deg, rgba(255,159,28,.18), rgba(45,106,79,.18), rgba(96,165,250,.18), rgba(255,159,28,.18));
  filter: blur(18px);
  opacity:.55;
  animation: spin 10s linear infinite;
}
.hero > * { position: relative; z-index:1; }
@keyframes spin { from{ transform:rotate(0deg);} to{transform:rotate(360deg);} }

.badge{
  display:inline-flex; align-items:center; gap:.55rem;
  padding:.35rem .7rem;
  border:1px solid rgba(255,255,255,0.14);
  border-radius:999px;
  background: rgba(0,0,0,0.22);
  color: rgba(229,231,235,0.78);
  font-size:.78rem;
  letter-spacing:.12em;
  text-transform:uppercase;
}

.card{
  background: rgba(255,255,255,0.035);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 1rem 1rem;
  box-shadow: 0 18px 44px rgba(0,0,0,0.35);
  transition: transform .25s ease, border-color .25s ease;
}
.card:hover{ transform: translateY(-2px); border-color: rgba(255,255,255,0.18); }

.narr{
  font-size: 1.02rem;
  line-height: 1.75;
  text-align: justify;
  padding: 0.95rem 1.05rem;
  border-radius: 14px;
  background: rgba(255,255,255,0.03);
  border-left: 5px solid #FF9F1C;
  color: rgba(229,231,235,0.86);
}
.narr-green{ border-left: 5px solid #2D6A4F; }
.narr-blue{ border-left: 5px solid #60A5FA; }

.meta{
  color: rgba(229,231,235,0.70);
  font-size: 0.94rem;
  line-height: 1.55;
}

.desc{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: .9rem 1rem;
  color: rgba(229,231,235,0.82);
  line-height: 1.65;
}
.desc h4{
  font-family: ui-sans-serif, system-ui;
  letter-spacing: .14em;
  text-transform: uppercase;
  font-size: .72rem;
  color: rgba(229,231,235,0.65);
  margin: 0 0 .45rem 0;
}
.desc b{ color: rgba(255,255,255,0.92); }
.desc .key{ color: rgba(255,159,28,0.95); font-weight: 800; }
.desc .keyg{ color: rgba(45,106,79,0.95); font-weight: 800; }
.desc .note{
  font-size: .88rem;
  color: rgba(229,231,235,0.68);
  margin-top: .55rem;
}

.nav{
  display:flex; flex-wrap:wrap; justify-content:center;
  gap:.55rem; margin-top:.75rem;
}
.nav a{
  text-decoration:none;
  color: rgba(229,231,235,0.78);
  border:1px solid rgba(255,255,255,0.14);
  border-radius:999px;
  padding:.42rem .85rem;
  background: rgba(0,0,0,0.16);
  transition: all .22s ease;
}
.nav a:hover{ color:#fff; border-color: rgba(255,255,255,0.30); transform: translateY(-1px); }

hr{ border:none; border-top: 1px solid rgba(255,255,255,0.10); margin: 1.4rem 0; }

.kpi{ display:flex; flex-wrap:wrap; gap:12px; margin-top:.4rem; }
.pill{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: .7rem .9rem;
  min-width: 230px;
}
.pill .lab{ color: rgba(229,231,235,0.65); font-size:.76rem; letter-spacing:.12em; text-transform:uppercase; }
.pill .val{ font-size: 1.55rem; font-weight: 850; margin-top:.15rem; }

.sep{
  height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.10), transparent);
  margin: 1.6rem 0;
}

.fadein{ animation: fadeIn .7s ease both; }
@keyframes fadeIn { from{ opacity:0; transform: translateY(8px);} to{ opacity:1; transform: translateY(0);} }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def safe_read_csv(path: str):
    for sep in [";", ",", "\t"]:
        try:
            d = pd.read_csv(path, sep=sep)
            if d.shape[1] >= 2:
                return d
        except Exception:
            pass
    return pd.read_csv(path)

def day_night(hour: int) -> str:
    return "Jour" if 7 <= int(hour) < 19 else "Nuit"

def norm(s: pd.Series):
    mx = s.max()
    return s / (mx if mx and mx > 0 else 1)

def kpi_max_hour(df_hourly: pd.DataFrame, value_col: str = "counts"):
    if df_hourly.empty:
        return None, None
    idx = df_hourly[value_col].idxmax()
    return int(df_hourly.loc[idx, "hour"]), float(df_hourly.loc[idx, value_col])

def kpi_max_month(df_monthly: pd.DataFrame, value_col: str = "counts"):
    if df_monthly.empty:
        return None, None
    idx = df_monthly[value_col].idxmax()
    return int(df_monthly.loc[idx, "month"]), float(df_monthly.loc[idx, value_col])

def month_name(m: int) -> str:
    names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
    return names[m-1] if 1 <= m <= 12 else str(m)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data(show_spinner=False)
def load_all_data():
    lifts = safe_read_csv("remontees_long_all.csv")
    pp_res = safe_read_csv("PP_results_cleaned.csv")
    pp_stat = pd.read_excel("PP_stations_MB.xlsx", sheet_name="Feuil2")
    lifts_geo = pd.read_excel("remontees_coordonnees.xlsx", sheet_name="Feuil1")

    pp_res["date"] = pd.to_datetime(pp_res["date"], format="%d/%m/%Y %H:%M", errors="coerce")
    pp_res = pp_res.dropna(subset=["date"]).copy()

    human_tags = ["humain", "vtt", "vehicule", "randonneur", "chien"]
    pp_res["prediction_first"] = pp_res["prediction_first"].astype(str)
    pat = "|".join(human_tags)

    pp_res["is_human"] = pp_res["prediction_first"].str.contains(pat, case=False, na=False)
    pp_res["is_animal"] = (~pp_res["is_human"]) & (~pp_res["prediction_first"].str.lower().isin(["vide", "indéfini", "indefini", "autre"]))

    pp_res["year"] = pp_res["date"].dt.year
    pp_res["month"] = pp_res["date"].dt.month
    pp_res["hour"] = pp_res["date"].dt.hour

    full_pp = pp_res.merge(pp_stat, on="station", how="left")
    full_pp = full_pp.dropna(subset=["latitude", "longitude"]).copy()
    return lifts, full_pp, lifts_geo

lifts, df, lifts_geo = load_all_data()

hum = df[df["is_human"]].copy()
fau = df[df["is_animal"]].copy()

hum["day_night"] = hum["hour"].apply(day_night)
fau["day_night"] = fau["hour"].apply(day_night)

# ============================================================
# PREP (robuste : reindex heures & mois)
# ============================================================
total_hum = int(hum.shape[0])
total_fau = int(fau.shape[0])
stations = int(df["station"].nunique()) if "station" in df.columns else int(df.shape[0])

hour_idx = pd.Index(range(24), name="hour")
month_idx = pd.Index(range(1, 13), name="month")

hourly_hum_2024 = hum[hum["year"] == 2024].groupby("hour").size().reindex(hour_idx, fill_value=0).reset_index(name="counts")
hourly_hum_2023 = hum[hum["year"] == 2023].groupby("hour").size().reindex(hour_idx, fill_value=0).reset_index(name="counts")

monthly_hum_2024 = hum[hum["year"] == 2024].groupby("month").size().reindex(month_idx, fill_value=0).reset_index(name="counts")
monthly_hum_2023 = hum[hum["year"] == 2023].groupby("month").size().reindex(month_idx, fill_value=0).reset_index(name="counts")

dn_hum_2024 = hum[hum["year"] == 2024].groupby("day_night").size().reset_index(name="counts")
dn_hum_2023 = hum[hum["year"] == 2023].groupby("day_night").size().reset_index(name="counts")

top10_sites = (
    hum.groupby("site").size().sort_values(ascending=False).head(10).reset_index(name="counts")
) if "site" in hum.columns else pd.DataFrame({"site": [], "counts": []})

hourly_fau_2024 = fau[fau["year"] == 2024].groupby("hour").size().reindex(hour_idx, fill_value=0).reset_index(name="detections")
dn_fau_2024 = fau[fau["year"] == 2024].groupby("day_night").size().reset_index(name="detections")
dn_fau_2023 = fau[fau["year"] == 2023].groupby("day_night").size().reset_index(name="detections")
monthly_fau_2024 = fau[fau["year"] == 2024].groupby("month").size().reindex(month_idx, fill_value=0).reset_index(name="detections")

top_species_2024 = fau.loc[fau["year"] == 2024, "prediction_first"].value_counts().head(5).reset_index()
top_species_2024.columns = ["species", "detections"]

comp_hour = pd.merge(
    hourly_hum_2024.rename(columns={"counts": "humans"}),
    hourly_fau_2024.rename(columns={"detections": "fauna"}),
    on="hour", how="outer"
).fillna(0).sort_values("hour")
comp_hour["humans_norm"] = norm(comp_hour["humans"])
comp_hour["fauna_norm"] = norm(comp_hour["fauna"])

comp_month = pd.merge(
    monthly_hum_2024.rename(columns={"counts": "humans"}),
    monthly_fau_2024.rename(columns={"detections": "fauna"}),
    on="month", how="outer"
).fillna(0).sort_values("month")
comp_month["humans_norm"] = norm(comp_month["humans"])
comp_month["fauna_norm"] = norm(comp_month["fauna"])

map_stats = df.groupby("station").agg(
    humans=("is_human", "sum"),
    fauna=("is_animal", "sum"),
    latitude=("latitude", "first"),
    longitude=("longitude", "first"),
    altitude=("altitude", "first"),
).dropna()

hum_hour = hum.groupby("hour").size().reindex(hour_idx, fill_value=0)
fau_hour = fau.groupby("hour").size().reindex(hour_idx, fill_value=0)
hum_dist = hum_hour / (hum_hour.sum() if hum_hour.sum() > 0 else 1)
fau_dist = fau_hour / (fau_hour.sum() if fau_hour.sum() > 0 else 1)
theta = (hour_idx.values * 15)

# KPI insights rapides pour descriptions
h24_peak_h, h24_peak_v = kpi_max_hour(hourly_hum_2024, "counts")
h23_peak_h, h23_peak_v = kpi_max_hour(hourly_hum_2023, "counts")
mh24_peak_m, mh24_peak_v = kpi_max_month(monthly_hum_2024, "counts")
mh23_peak_m, mh23_peak_v = kpi_max_month(monthly_hum_2023, "counts")
f24_peak_h, f24_peak_v = kpi_max_hour(hourly_fau_2024.rename(columns={"detections":"counts"}), "counts")
mf24_peak_m, mf24_peak_v = kpi_max_month(monthly_fau_2024.rename(columns={"detections":"counts"}), "counts")

# ============================================================
# SIDEBAR (navigation only)
# ============================================================
with st.sidebar:
    st.download_button("Télécharger audience.txt", data=audience_txt, file_name="audience.txt", mime="text/plain")
    st.download_button("Télécharger lien_narration.txt", data=link_txt, file_name="lien_narration.txt", mime="text/plain")
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.markdown(
        """
<a href="#intro">Intro</a><br>
<a href="#acte1">Acte I — Humains</a><br>
<a href="#acte2">Acte II — Faune</a><br>
<a href="#acte3">Acte III — Coexistence</a><br>
<a href="#final">Conclusion</a>
""",
        unsafe_allow_html=True
    )

# ============================================================
# INTRO (objectif + audience)
# ============================================================
st.markdown('<a name="intro"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="hero fadein">
  <div style="display:flex; justify-content:center;">
    <span class="badge">TP Noté • Data Story • Chamonix / Mont-Blanc</span>
  </div>
  <h1>🦌 Le Sommet en Sursis</h1>
  <div class="meta" style="text-align:center;">
    Une narration de données sur la coexistence entre fréquentation humaine et activité de la faune sauvage.
  </div>

  <div class="nav">
    <a href="#acte1">Commencer la story →</a>
    <a href="#acte2">Voir la faune</a>
    <a href="#acte3">Comparer humains/faune</a>
  </div>

  <hr>

  <div class="narr">
    <b>Objectif général.</b> Étudier l’influence de la fréquentation humaine en milieu montagnard
    sur la présence et l’activité de la faune sauvage, en croisant des données de comptage
    (éco-compteurs / remontées) et des détections issues de pièges photos,
    selon des dimensions <b>temporelles</b> (heure, jour/nuit, saison) et <b>spatiales</b> (site, altitude).<br><br>
   
  </div>

  <div class="kpi">
    <div class="pill"><div class="lab">Détections Humaines</div><div class="val">{hum:,}</div></div>
    <div class="pill"><div class="lab">Détections Faune</div><div class="val">{fau:,}</div></div>
    <div class="pill"><div class="lab">Stations observées</div><div class="val">{stn:,}</div></div>
  </div>
</div>
""".format(hum=total_hum, fau=total_fau, stn=stations), unsafe_allow_html=True)

st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

# ============================================================
# ACTE I — HUMAINS
# ============================================================
st.markdown('<a name="acte1"></a>', unsafe_allow_html=True)
st.header("Acte I — Quand la montagne se remplit (Fréquentation humaine)")

st.markdown("""
<div class="narr fadein">
<b>Message.</b> La fréquentation humaine est concentrée en journée et en été, et elle est spatialement inégale :
quelques sites dominent nettement. Ce cadre permet d’évaluer ensuite les adaptations de la faune.
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M1 — Rythme horaire (2024 vs 2023)")
    st.markdown("<div class='meta'><b>Objectif :</b> décrire la structure journalière de la fréquentation.</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([2.1, 1])
    with gcol:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_hum_2024["hour"], y=hourly_hum_2024["counts"],
            mode="lines+markers", name="2024", line=dict(color=C_HUM, width=3), marker=dict(size=6)
        ))
        fig.add_trace(go.Scatter(
            x=hourly_hum_2023["hour"], y=hourly_hum_2023["counts"],
            mode="lines+markers", name="2023", line=dict(color="#2969a5", width=4), marker=dict(size=7, symbol="diamond")
        ))
        fig.add_vrect(x0=10, x1=16, fillcolor="rgba(255,159,28,0.10)", line_width=0,
                      annotation_text="Fenêtre de pic diurne", annotation_position="top left")
        fig.update_layout(template="plotly_dark", height=360,
                          xaxis_title="Heure", yaxis_title="Passages (volume)",
                          margin=dict(l=10,r=10,t=40,b=10),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, width='stretch')

    with tcol:
        st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Activité surtout <b>diurne</b> : montée le matin, baisse en fin d’après-midi.</div>
  <div>• Pic 2024 vers <span class="key">{h24_peak_h}h</span> (≈ {int(h24_peak_v):,} détections).</div>
  <div>• Profil 2023 très proche → <b>stabilité</b> des usages.</div>
  <div class="note">Ce graphique fixe le “rythme humain” qui servira de référence.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> position (heure/volume), couleur (année), marqueurs.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M2 — Saisonnalité (2024 vs 2023)")
    st.markdown("<div class='meta'><b>Objectif :</b> visualiser la concentration estivale et comparer les années.</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([2.1, 1])
    with gcol:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_hum_2024["month"], y=monthly_hum_2024["counts"],
            mode="lines+markers", name="2024",
            line=dict(color=C_HUM, width=3),
            marker=dict(size=7)
        ))
        fig.add_trace(go.Scatter(
            x=monthly_hum_2023["month"], y=monthly_hum_2023["counts"],
            mode="lines+markers", name="2023",
            line=dict(color="#2969a5", width=4),
            marker=dict(size=9, symbol="diamond")
        ))
        fig.add_vrect(
            x0=6, x1=9,
            fillcolor="rgba(255,159,28,0.14)",
            line_width=0,
            annotation_text="Période estivale",
            annotation_position="top left"
        )
        fig.update_layout(
            template="plotly_dark",
            height=360,
            xaxis=dict(
                title="Mois",
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
            ),
            yaxis=dict(title="Passages (volume)"),
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, width='stretch')

    with tcol:
        st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Forte <b>saisonnalité</b> : pic en été (Juin→Sep).</div>
  <div>• Pic 2024 en <span class="key">{month_name(mh24_peak_m)}</span> (≈ {int(mh24_peak_v):,}).</div>
  <div>• Pic 2023 en <span class="key">{month_name(mh23_peak_m)}</span> (≈ {int(mh23_peak_v):,}).</div>
  <div class="note">La pression touristique se concentre sur quelques mois → “fenêtres de risque”.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> position (mois/volume), couleur (année), marqueur.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

c3, c4 = st.columns([1, 1.2])

with c3:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M3 — Jour vs Nuit (2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> quantifier l’asymétrie jour/nuit.</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([1.6, 1])
    with gcol:
        fig = px.bar(dn_hum_2024, x="day_night", y="counts", text="counts",
                     color="day_night", color_discrete_map={"Jour": C_HUM, "Nuit": C_MUT})
        fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=40,b=10),
                          xaxis_title="", yaxis_title="Passages")
        st.plotly_chart(fig, width='stretch')

    with tcol:
        # Ratio jour/nuit
        dn_map = dict(zip(dn_hum_2024["day_night"], dn_hum_2024["counts"]))
        day_v = float(dn_map.get("Jour", 0))
        night_v = float(dn_map.get("Nuit", 0))
        ratio = (day_v / night_v) if night_v > 0 else np.inf

        st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Activité <b>quasi entièrement</b> en journée.</div>
  <div>• Rapport Jour/Nuit ≈ <span class="key">{ratio:.1f}×</span>.</div>
  <div class="note">La nuit devient un “espace-temps” plus calme, clé pour analyser la faune.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> hauteur (volume), couleur (jour/nuit).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M4 — Top 10 sites (pression localisée)")
    st.markdown("<div class='meta'><b>Objectif :</b> montrer l’hétérogénéité spatiale.</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([2.1, 1])
    with gcol:
        if len(top10_sites):
            fig = px.bar(top10_sites.sort_values("counts"), x="counts", y="site", orientation="h", text="counts")
            fig.update_traces(marker_color=C_HUM)
            fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=40,b=10),
                              xaxis_title="Passages", yaxis_title="")
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Colonne 'site' absente : impossible d’afficher le Top 10.")

    with tcol:
        if len(top10_sites):
            top_site = top10_sites.iloc[0]["site"]
            top_val = int(top10_sites.iloc[0]["counts"])
            share_top3 = (top10_sites.head(3)["counts"].sum() / top10_sites["counts"].sum()) if top10_sites["counts"].sum() > 0 else 0

            st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Forte <b>hétérogénéité</b> : quelques sites dominent.</div>
  <div>• Site n°1 : <span class="key">{top_site}</span> (≈ {top_val:,}).</div>
  <div>• Les 3 premiers concentrent ≈ <span class="key">{share_top3*100:.0f}%</span> du Top10.</div>
  <div class="note">La pression humaine est <b>localisée</b>, pas uniforme.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> longueur (volume) + position (site).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ACTE II — FAUNE
# ============================================================
st.markdown('<a name="acte2"></a>', unsafe_allow_html=True)
st.header("Acte II — L’autre horloge (Activité de la faune)")

st.markdown("""
<div class="narr narr-green fadein">
<b>Message.</b> L’activité de la faune est majoritairement nocturne/crépusculaire, avec un creux en milieu de journée.
Elle augmente du printemps à l’été puis diminue fortement en automne/hiver.
</div>
""", unsafe_allow_html=True)

d1, d2 = st.columns(2)

with d1:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M5 — Activité horaire (faune, 2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> repérer les pics (matin/soir) et le creux diurne.</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([2.1, 1])
    with gcol:
        fig = px.line(hourly_fau_2024, x="hour", y="detections", markers=True)
        fig.update_traces(line_color=C_FAU)
        fig.add_vrect(x0=10, x1=16, fillcolor="rgba(255,159,28,0.08)", line_width=0,
                      annotation_text="Créneau humain (faune en retrait)", annotation_position="top left")
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10,r=10,t=40,b=10),
                          xaxis_title="Heure", yaxis_title="Détections")
        st.plotly_chart(fig, width='stretch')

    with tcol:
        st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Deux moments forts : <span class="keyg">crépuscule</span> et <span class="keyg">nuit</span>.</div>
  <div>• Pic 2024 vers <span class="keyg">{f24_peak_h}h</span> (≈ {int(f24_peak_v):,}).</div>
  <div>• Creux en milieu de journée → profil <b>inverse</b> des humains.</div>
  <div class="note">Premier indice d’un <b>décalage temporel</b>.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> position (heure/détections).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with d2:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M6 — Jour vs Nuit (faune, 2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> vérifier l’asymétrie opposée à l’humain.</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([1.6, 1])
    with gcol:
        fig = px.bar(dn_fau_2024, x="day_night", y="detections", text="detections",
                     color="day_night", color_discrete_map={"Jour": C_MUT, "Nuit": C_FAU})
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10,r=10,t=40,b=10),
                          xaxis_title="", yaxis_title="Détections")
        st.plotly_chart(fig, width='stretch')

    with tcol:
        dn_map = dict(zip(dn_fau_2024["day_night"], dn_fau_2024["detections"]))
        day_v = float(dn_map.get("Jour", 0))
        night_v = float(dn_map.get("Nuit", 0))
        ratio = (night_v / day_v) if day_v > 0 else np.inf

        st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Activité surtout <b>nocturne</b>.</div>
  <div>• Nuit/Jour ≈ <span class="keyg">{ratio:.1f}×</span>.</div>
  <div class="note">La nuit apparaît comme une <b>période refuge</b> (moins de perturbations).</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> hauteur + couleur.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

e1, e2 = st.columns([1.2, 0.8])

with e1:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M7 — Saisonnalité (faune, 2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> identifier les périodes d’activité forte/faible.</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([2.1, 1])
    with gcol:
        fig = px.line(monthly_fau_2024, x="month", y="detections", markers=True)
        fig.update_traces(line_color=C_FAU)
        fig.add_vrect(x0=6, x1=9, fillcolor="rgba(45,106,79,0.10)", line_width=0,
                      annotation_text="Pic estival", annotation_position="top left")
        fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=40,b=10),
                          xaxis_title="Mois", yaxis_title="Détections",
                          xaxis=dict(tickmode="array", tickvals=list(range(1, 13)),
                                     ticktext=["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]))
        st.plotly_chart(fig, width='stretch')

    with tcol:
        st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Hausse du printemps à l’été, baisse en automne/hiver.</div>
  <div>• Pic en <span class="keyg">{month_name(mf24_peak_m)}</span> (≈ {int(mf24_peak_v):,}).</div>
  <div class="note">Même si l’été est plus “vivant”, l’horaire reste <b>décliné hors journée</b>.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> position.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with e2:
    st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
    st.subheader("M8 — Top 5 espèces (2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> contextualiser (espèces dominantes).</div>", unsafe_allow_html=True)

    gcol, tcol = st.columns([1.4, 1])
    with gcol:
        fig = px.bar(top_species_2024.sort_values("detections"), x="detections", y="species", orientation="h", text="detections")
        fig.update_traces(marker_color=C_FAU)
        fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=40,b=10),
                          xaxis_title="Détections", yaxis_title="")
        st.plotly_chart(fig, width='stretch')

    with tcol:
        if len(top_species_2024):
            sp1 = top_species_2024.iloc[0]["species"]
            sp1v = int(top_species_2024.iloc[0]["detections"])
            st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Espèce la plus détectée : <span class="keyg">{sp1}</span>.</div>
  <div>• Volume ≈ <span class="keyg">{sp1v:,}</span> détections en 2024.</div>
  <div class="note">Ces espèces structurent l’activité globale observée dans les blocs précédents.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='meta'><b>Variables visuelles :</b> longueur + position.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ACTE III — COEXISTENCE
# ============================================================
st.markdown('<a name="acte3"></a>', unsafe_allow_html=True)
st.header("Acte III — Coexistence : partager l’espace… ou le temps ?")

st.markdown("""
<div class="narr narr-blue fadein">
<b>Message.</b> Les pics d’activité humaine (jour) et animale (soir/nuit) se recouvrent peu.
La nuit devient une fenêtre privilégiée pour la faune, compatible avec une stratégie d’évitement temporel.
</div>
""", unsafe_allow_html=True)

# M9
st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
st.subheader("M9 — Comparaison horaire normalisée (2024)")
st.markdown("<div class='meta'><b>Objectif :</b> comparer les profils indépendamment des volumes.</div>", unsafe_allow_html=True)

gcol, tcol = st.columns([2.3, 1])
with gcol:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comp_hour["hour"], y=comp_hour["humans_norm"], mode="lines+markers",
                             name="Humains (norm.)", line=dict(color=C_HUM, width=3)))
    fig.add_trace(go.Scatter(x=comp_hour["hour"], y=comp_hour["fauna_norm"], mode="lines+markers",
                             name="Faune (norm.)", line=dict(color=C_FAU, width=3)))
    fig.add_vrect(x0=10, x1=16, fillcolor="rgba(255,159,28,0.10)", line_width=0,
                 annotation_text="Fenêtre de forte présence humaine", annotation_position="top left")
    fig.update_layout(template="plotly_dark", height=340, margin=dict(l=10,r=10,t=40,b=10),
                      xaxis_title="Heure", yaxis_title="Activité normalisée (0–1)")
    st.plotly_chart(fig, width='stretch')

with tcol:
    # mesure simple de recouvrement (approx)
    overlap = float(np.minimum(comp_hour["humans_norm"], comp_hour["fauna_norm"]).sum() / (comp_hour["fauna_norm"].sum() if comp_hour["fauna_norm"].sum() > 0 else 1))
    st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Les pics humains sont <b>diurnes</b>, la faune se décale <b>soir/nuit</b>.</div>
  <div>• Recouvrement relatif ≈ <span class="key">{overlap*100:.0f}%</span> (faible).</div>
  <div class="note">Compatible avec une stratégie d’<b>évitement temporel</b>.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='meta'><b>Variables visuelles :</b> position + couleur.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# M10
st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
st.subheader("M10 — Carte de friction (Humains = couleur, Faune = taille)")
st.markdown("<div class='meta'><b>Objectif :</b> visualiser la pression humaine et la présence animale par station.</div>", unsafe_allow_html=True)

gcol, tcol = st.columns([2.3, 1])
with gcol:
    fig_map = px.scatter_map(
        map_stats,
        lat="latitude", lon="longitude",
        color="humans", size="fauna",
        color_continuous_scale="OrRd",
        size_max=32, zoom=10.5, height=560,
        hover_name=map_stats.index,
        hover_data={"altitude": True, "humans": True, "fauna": True}
    )
    fig_map.update_layout(mapbox_style="carto-darkmatter", template="plotly_dark", margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig_map, width='stretch')

with tcol:
    # stats simples
    if len(map_stats):
        most_h = map_stats["humans"].idxmax()
        most_h_v = int(map_stats.loc[most_h, "humans"])
        most_f = map_stats["fauna"].idxmax()
        most_f_v = int(map_stats.loc[most_f, "fauna"])
        st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Couleur = intensité humaine, taille = présence faune.</div>
  <div>• Station la plus “humaine” : <span class="key">{most_h}</span> (≈ {most_h_v:,}).</div>
  <div>• Station la plus “faune” : <span class="keyg">{most_f}</span> (≈ {most_f_v:,}).</div>
  <div class="note">Lecture rapide des <b>zones de friction</b> potentielles.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='meta'><b>Variables visuelles :</b> position (lat/lon), couleur (humains), taille (faune).</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# M11
st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
st.subheader("M11 — Horloge circadienne (répartition relative sur 24h)")
st.markdown("<div class='meta'><b>Objectif :</b> rendre le décalage temporel intuitif.</div>", unsafe_allow_html=True)

gcol, tcol = st.columns([2.3, 1])
with gcol:
    fig_polar = go.Figure()
    fig_polar.add_trace(go.Scatterpolar(r=hum_dist.values, theta=theta, fill="toself",
                                       name="Humains", line=dict(color=C_HUM, width=3)))
    fig_polar.add_trace(go.Scatterpolar(r=fau_dist.values, theta=theta, fill="toself",
                                       name="Faune", line=dict(color=C_FAU, width=3)))
    fig_polar.update_layout(
        template="plotly_dark",
        height=520,
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(
                tickvals=list(range(0, 360, 30)),
                ticktext=[str(h) for h in range(0, 24, 2)]
            )
        ),
        margin=dict(l=10,r=10,t=20,b=10)
    )
    st.plotly_chart(fig_polar, width='stretch')

with tcol:
    st.markdown(f"""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Forme orange (humains) gonfle au cœur de la journée.</div>
  <div>• Forme verte (faune) s’étend surtout le soir et la nuit.</div>
  <div class="note">Une “coexistence” qui se joue d’abord sur <b>l’horloge</b>.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='meta'><b>Variables visuelles :</b> angle=heure, rayon=proportion, couleur=type.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# M12
st.markdown("<div class='card fadein'>", unsafe_allow_html=True)
st.subheader("M12 — Comparaison saisonnière normalisée (2024)")
st.markdown("<div class='meta'><b>Objectif :</b> montrer la coïncidence estivale sans confondre avec l’horaire.</div>", unsafe_allow_html=True)

gcol, tcol = st.columns([2.3, 1])
with gcol:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comp_month["month"], y=comp_month["humans_norm"], mode="lines+markers",
                             name="Humains (norm.)", line=dict(color=C_HUM, width=3)))
    fig.add_trace(go.Scatter(x=comp_month["month"], y=comp_month["fauna_norm"], mode="lines+markers",
                             name="Faune (norm.)", line=dict(color=C_FAU, width=3)))
    fig.add_vrect(x0=6, x1=9, fillcolor="rgba(96,165,250,0.10)", line_width=0,
                 annotation_text="Été", annotation_position="top left")
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=40,b=10),
                      xaxis_title="Mois", yaxis_title="Activité normalisée (0–1)",
                      xaxis=dict(tickmode="array", tickvals=list(range(1, 13)),
                                 ticktext=["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]))
    st.plotly_chart(fig, width='stretch')

with tcol:
    st.markdown("""
<div class="desc">
  <h4>Mini-lecture</h4>
  <div>• Les deux courbes montent en été (effet “saison”).</div>
  <div>• Mais cela ne signifie pas un recouvrement horaire : cf. M9 & M11.</div>
  <div class="note">Important pour l’audience : saison ≠ coexistence fine.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='meta'><b>Variables visuelles :</b> position + couleur.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# CONCLUSION
# ============================================================
st.markdown('<a name="final"></a>', unsafe_allow_html=True)
st.header("Épilogue — Ce que doit retenir l’audience")

st.markdown("""
<div class="narr narr-green fadein">
<b>Conclusion.</b> La montagne est un espace partagé, mais le partage se fait surtout par le <b>temps</b>.
La fréquentation humaine se concentre en journée et en été, tandis que la faune apparaît davantage la nuit et aux heures
crépusculaires. Cette dissociation temporelle est compatible avec une stratégie d’évitement.
</div>
""", unsafe_allow_html=True)

st.caption("Données : CREA Mont-Blanc | Narration : Master DS4SC — Chamonix / Mont-Blanc")


