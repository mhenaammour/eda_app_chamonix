import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG + THEME (Chamonix / Mont-Blanc : faune-flore-humain)
# ============================================================
st.set_page_config(page_title="Chamonix — Le Sommet en Sursis", page_icon="🦌", layout="wide")

# Palette globale (décision globale)
C_HUM = "#FF9F1C"     # Humains (ambre)
C_FAU = "#2D6A4F"     # Faune (vert)
C_FLR = "#60A5FA"     # Flore / environnement (bleu)
C_MUT = "#94A3B8"

st.markdown(
    """
<style>
.main { background-color: #0b0f14; color: #E5E7EB; }
.block-container { max-width: 1250px; padding-top: 1.8rem; padding-bottom: 3.2rem; }

h1,h2,h3 { font-family: ui-serif, Georgia, "Times New Roman", serif; letter-spacing: -0.02em; }
h1 { text-align:center; font-size: 3.2rem !important; margin-bottom: 0.3rem; }
h2 { margin-top: 2rem; border-bottom: 1px solid rgba(255,255,255,0.12); padding-bottom: .5rem; }
h3 { margin-top: .4rem; }

.badge {
  display:inline-flex; align-items:center; gap:.5rem;
  padding:.35rem .65rem; border:1px solid rgba(255,255,255,0.14);
  border-radius:999px; background: rgba(255,255,255,0.04);
  color: rgba(229,231,235,0.78); font-size:.8rem;
  letter-spacing:.10em; text-transform:uppercase;
}

.hero {
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 18px;
  padding: 1.4rem 1.2rem;
  background:
    radial-gradient(900px 450px at 10% -10%, rgba(255,159,28,0.25), transparent 60%),
    radial-gradient(900px 450px at 90% 0%, rgba(45,106,79,0.22), transparent 60%),
    radial-gradient(900px 450px at 50% 120%, rgba(96,165,250,0.18), transparent 60%),
    linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  box-shadow: 0 18px 55px rgba(0,0,0,0.55);
}

.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 1rem 1rem;
  box-shadow: 0 18px 40px rgba(0,0,0,0.35);
}

.narr {
  font-size: 1.03rem;
  line-height: 1.75;
  text-align: justify;
  padding: 0.95rem 1.05rem;
  border-radius: 14px;
  background: rgba(255,255,255,0.03);
  border-left: 5px solid #FF9F1C;
  color: rgba(229,231,235,0.85);
}

.narr-green {
  border-left: 5px solid #2D6A4F;
}

.meta {
  color: rgba(229,231,235,0.70);
  font-size: 0.92rem;
  line-height: 1.55;
}

.nav {
  display:flex; gap:.55rem; flex-wrap:wrap; justify-content:center;
  margin-top: .85rem;
}
.nav a {
  text-decoration:none; color: rgba(229,231,235,0.78);
  border:1px solid rgba(255,255,255,0.14);
  border-radius:999px; padding:.42rem .8rem;
  background: rgba(0,0,0,0.15);
}
.nav a:hover { color: #fff; border-color: rgba(255,255,255,0.28); }

hr { border: none; border-top: 1px solid rgba(255,255,255,0.10); margin: 1.8rem 0; }

.kpi { display:flex; gap:12px; flex-wrap:wrap; }
.kpi .pill {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: .7rem .9rem;
  min-width: 210px;
}
.kpi .pill .lab { color: rgba(229,231,235,0.65); font-size:.78rem; letter-spacing:.12em; text-transform:uppercase; }
.kpi .pill .val { font-size: 1.5rem; font-weight: 800; margin-top: .15rem; }

.smallcap { font-size: .85rem; color: rgba(229,231,235,0.65); letter-spacing:.10em; text-transform:uppercase; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# CHARGEMENT DONNÉES
# ============================================================
def safe_read_csv(path: str):
    # essaie séparateurs classiques
    for sep in [";", ",", "\t"]:
        try:
            d = pd.read_csv(path, sep=sep)
            if d.shape[1] >= 2:
                return d
        except Exception:
            pass
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_all_data():
    lifts = safe_read_csv("remontees_long_all.csv")
    pp_res = safe_read_csv("PP_results_cleaned.csv")
    pp_stat = pd.read_excel("PP_stations_MB.xlsx", sheet_name="Feuil2")
    lifts_geo = pd.read_excel("remontees_coordonnees.xlsx", sheet_name="Feuil1")

    # dates
    pp_res["date"] = pd.to_datetime(pp_res["date"], format="%d/%m/%Y %H:%M", errors="coerce")
    pp_res = pp_res.dropna(subset=["date"]).copy()

    # tags
    human_tags = ["humain", "vtt", "vehicule", "randonneur", "chien"]
    pat = "|".join(human_tags)
    pp_res["prediction_first"] = pp_res["prediction_first"].astype(str)

    pp_res["is_human"] = pp_res["prediction_first"].str.contains(pat, case=False, na=False)
    pp_res["is_animal"] = (~pp_res["is_human"]) & (~pp_res["prediction_first"].str.lower().isin(["vide", "indéfini", "indefini", "autre"]))

    # temps
    pp_res["year"] = pp_res["date"].dt.year
    pp_res["month"] = pp_res["date"].dt.month
    pp_res["hour"] = pp_res["date"].dt.hour

    full_pp = pp_res.merge(pp_stat, on="station", how="left")
    # garder stations localisées
    full_pp = full_pp.dropna(subset=["latitude", "longitude"]).copy()

    return lifts, full_pp, lifts_geo

lifts, df, lifts_geo = load_all_data()

def day_night(hour: int) -> str:
    return "Jour" if 7 <= int(hour) < 19 else "Nuit"

# ============================================================
# PRÉPARATION DATA (BLOC 1/2/3)
# ============================================================
hum = df[df["is_human"]].copy()
fau = df[df["is_animal"]].copy()

hum["day_night"] = hum["hour"].apply(day_night)
fau["day_night"] = fau["hour"].apply(day_night)

# KPI utiles
total_hum = int(hum.shape[0])
total_fau = int(fau.shape[0])
stations = int(df["station"].nunique()) if "station" in df.columns else int(df.shape[0])

# BLOC 1
hourly_hum_2024 = hum[hum["year"] == 2024].groupby("hour").size().reset_index(name="counts")
hourly_hum_2025 = hum[hum["year"] == 2025].groupby("hour").size().reset_index(name="counts")

monthly_hum_2024 = hum[hum["year"] == 2024].groupby("month").size().reset_index(name="counts")
monthly_hum_2025 = hum[hum["year"] == 2025].groupby("month").size().reset_index(name="counts")

dn_hum_2024 = hum[hum["year"] == 2024].groupby("day_night").size().reset_index(name="counts")

# Top 10 sites (sans filtre)
if "site" in hum.columns:
    top10_sites = (
        hum.groupby("site").size().sort_values(ascending=False).head(10).reset_index(name="counts")
    )
else:
    top10_sites = pd.DataFrame({"site": [], "counts": []})

# BLOC 2
hourly_fau_2024 = fau[fau["year"] == 2024].groupby("hour").size().reset_index(name="detections")
dn_fau_2024 = fau[fau["year"] == 2024].groupby("day_night").size().reset_index(name="detections")
monthly_fau_2024 = fau[fau["year"] == 2024].groupby("month").size().reset_index(name="detections")

top_species_2024 = (
    fau.loc[fau["year"] == 2024, "prediction_first"]
    .value_counts()
    .head(5)
    .reset_index()
)
top_species_2024.columns = ["species", "detections"]

# BLOC 3 : normalisations (pour comparer des PROFILS)
def norm(s: pd.Series):
    mx = s.max()
    return s / (mx if mx and mx > 0 else 1)

# horaire
comp_hour = pd.merge(
    hourly_hum_2024.rename(columns={"counts":"humans"}),
    hourly_fau_2024.rename(columns={"detections":"fauna"}),
    on="hour", how="outer"
).fillna(0).sort_values("hour")
comp_hour["humans_norm"] = norm(comp_hour["humans"])
comp_hour["fauna_norm"] = norm(comp_hour["fauna"])

# jour/nuit
comp_dn = pd.merge(
    dn_hum_2024.rename(columns={"counts":"humans"}),
    dn_fau_2024.rename(columns={"detections":"fauna"}),
    on="day_night", how="outer"
).fillna(0)
comp_dn["humans_norm"] = norm(comp_dn["humans"])
comp_dn["fauna_norm"] = norm(comp_dn["fauna"])

# mois
comp_month = pd.merge(
    monthly_hum_2024.rename(columns={"counts":"humans"}),
    monthly_fau_2024.rename(columns={"detections":"fauna"}),
    on="month", how="outer"
).fillna(0).sort_values("month")
comp_month["humans_norm"] = norm(comp_month["humans"])
comp_month["fauna_norm"] = norm(comp_month["fauna"])

# ============================================================
# SIDEBAR : fichier audience (exigence prof)
# ============================================================
audience_txt = (
    "Audience cible :\n"
    "- Gestionnaires d’espaces naturels (parc/réserve/collectivités)\n"
    "- Acteurs du tourisme (opérateurs, remontées, offices)\n"
    "- Équipes terrain (écogardes, suivi faune)\n\n"
    "Objectif général :\n"
    "Étudier l’influence de la fréquentation humaine en milieu montagnard sur la présence "
    "et l’activité de la faune sauvage, en croisant comptages visiteurs et détections de pièges photos.\n"
)

with st.sidebar:
    st.markdown("### 📄 Fichier demandé (Audience)")
    st.download_button("Télécharger audience.txt", data=audience_txt, file_name="audience.txt", mime="text/plain")
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.markdown(
        """
<div class="meta">
<a href="#intro">Intro</a><br>
<a href="#acte1">Acte I — Humains</a><br>
<a href="#acte2">Acte II — Faune</a><br>
<a href="#acte3">Acte III — Interaction</a><br>
<a href="#final">Conclusion</a>
</div>
""",
        unsafe_allow_html=True
    )

# ============================================================
# INTRO (Narration : objectif + audience + forme)
# ============================================================
st.markdown('<a name="intro"></a>', unsafe_allow_html=True)

st.markdown(
    """
<div class="hero">
  <div style="display:flex; justify-content:center;">
    <span class="badge">Master DS4SC • TP Noté • Data Storytelling</span>
  </div>
  <h1>🦌 Chamonix — Le Sommet en Sursis</h1>
  <div class="meta" style="text-align:center;">
    Faune • “flore/environnement” • Humains — Mont-Blanc (données CREA)
  </div>

  <div class="nav">
    <a href="#acte1">Commencer →</a>
    <a href="#acte2">Aller à la faune</a>
    <a href="#acte3">Comparer</a>
  </div>

  <hr>

  <div class="narr">
    <b>Objectif général.</b> Étudier l’influence de la fréquentation humaine en milieu montagnard sur la présence
    et l’activité de la faune sauvage, via un croisement entre comptages (éco-compteurs / remontées) et détections
    issues de pièges photos, selon des dimensions <b>temporelles</b> (heure, jour/nuit, saison) et <b>spatiales</b> (site, altitude).<br><br>
    <b>Audience.</b> Gestionnaires d’espaces naturels et acteurs du tourisme qui cherchent des éléments concrets pour
    concilier attractivité et préservation, sans conclure à une causalité directe.
  </div>

  <div class="card" style="margin-top: 1rem;">
    <div class="smallcap">Conception globale (décisions)</div>
    <div class="meta">
      • Forme : <b>scrollytelling</b> en 3 actes + épilogue. <br>
      • Palette : Humains (ambre), Faune (vert), Environnement/flore (bleu). <br>
      • Mise en page : cartes + graphiques annotés + synthèses “Message/Insight”.
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# KPIs (visu simple)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='smallcap'>Indicateurs de contexte</div>", unsafe_allow_html=True)
st.markdown("<div class='kpi'>", unsafe_allow_html=True)
st.markdown(f"<div class='pill'><div class='lab'>Détections Humaines</div><div class='val'>{total_hum:,}</div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='pill'><div class='lab'>Détections Faune</div><div class='val'>{total_fau:,}</div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='pill'><div class='lab'>Stations observées</div><div class='val'>{stations:,}</div></div>", unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================
# ACTE I — HUMAIN (Bloc 1)
# ============================================================
st.markdown('<a name="acte1"></a>', unsafe_allow_html=True)
st.header("Acte I — L’empreinte humaine : quand et où la montagne se remplit ?")

st.markdown(
    """
<div class="narr">
<b>Message (Bloc 1).</b> La fréquentation humaine est fortement concentrée <b>en journée</b> et <b>en été</b>,
et elle est <b>spatialement inégale</b> : quelques sites dominent.
Ce cadre est essentiel pour analyser ensuite si la faune évite certaines fenêtres temporelles.
</div>
""",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("1) Rythme horaire (2024 vs 2025)")
    st.markdown("<div class='meta'><b>Objectif communicationnel :</b> décrire la structure journalière de la fréquentation.</div>", unsafe_allow_html=True)

    fig = go.Figure()
    if len(hourly_hum_2024):
        fig.add_trace(go.Scatter(x=hourly_hum_2024["hour"], y=hourly_hum_2024["counts"], mode="lines+markers",
                                 name="Humains 2024", line=dict(color=C_HUM, width=3)))
    if len(hourly_hum_2025):
        fig.add_trace(go.Scatter(x=hourly_hum_2025["hour"], y=hourly_hum_2025["counts"], mode="lines+markers",
                                 name="Humains 2025", line=dict(color="#fb923c", width=3)))
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10,r=10,t=30,b=10),
                      xaxis_title="Heure", yaxis_title="Passages (volume)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='meta'>"
        "<b>Type de données :</b> temporelles (heure). "
        "<b>Graphique :</b> courbes (comparaison inter-annuelle). "
        "<b>Variables visuelles :</b> position + couleur (année)."
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("2) Saisonnalité (2024 vs 2025)")
    st.markdown("<div class='meta'><b>Objectif communicationnel :</b> montrer le pic estival.</div>", unsafe_allow_html=True)

    fig = go.Figure()
    if len(monthly_hum_2024):
        fig.add_trace(go.Scatter(x=monthly_hum_2024["month"], y=monthly_hum_2024["counts"], mode="lines+markers",
                                 name="Humains 2024", line=dict(color=C_HUM, width=3)))
    if len(monthly_hum_2025):
        fig.add_trace(go.Scatter(x=monthly_hum_2025["month"], y=monthly_hum_2025["counts"], mode="lines+markers",
                                 name="Humains 2025", line=dict(color="#fb923c", width=3)))
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10,r=10,t=30,b=10),
                      xaxis_title="Mois", yaxis_title="Passages (volume)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='meta'>"
        "<b>Type :</b> temporelles (mois). "
        "<b>Graphique :</b> courbes. "
        "<b>Variable :</b> position (mois → volume) + couleur."
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

col3, col4 = st.columns([1, 1.2])

with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("3) Jour vs Nuit (2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> quantifier l’asymétrie jour/nuit.</div>", unsafe_allow_html=True)

    fig = px.bar(dn_hum_2024, x="day_night", y="counts", text="counts",
                 color="day_night", color_discrete_map={"Jour": C_HUM, "Nuit": C_MUT})
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=30,b=10),
                      xaxis_title="", yaxis_title="Passages")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='meta'><b>Graphique :</b> barres. <b>Variable :</b> hauteur (passages), couleur (jour/nuit).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("4) Top 10 des sites (pression localisée)")
    st.markdown("<div class='meta'><b>Objectif :</b> montrer l’hétérogénéité spatiale.</div>", unsafe_allow_html=True)

    if len(top10_sites):
        fig = px.bar(top10_sites.sort_values("counts"), x="counts", y="site", orientation="h", text="counts")
        fig.update_traces(marker_color=C_HUM)
        fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=30,b=10),
                          xaxis_title="Passages", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Colonne 'site' absente : impossible d’afficher le Top 10.")

    st.markdown("<div class='meta'><b>Graphique :</b> barres horizontales. <b>Variable :</b> longueur (passages), position (site).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ACTE II — FAUNE (Bloc 2)
# ============================================================
st.markdown('<a name="acte2"></a>', unsafe_allow_html=True)
st.header("Acte II — La faune : l’autre horloge du Mont-Blanc")

st.markdown(
    """
<div class="narr narr-green">
<b>Message (Bloc 2).</b> L’activité de la faune est <b>nocturne/crépusculaire</b>,
avec une activité réduite en milieu de journée. Elle présente aussi une saisonnalité :
augmentation du printemps à l’été, puis baisse forte en automne/hiver.
</div>
""",
    unsafe_allow_html=True,
)

a1, a2 = st.columns(2)
with a1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("1) Activité horaire (faune, 2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> repérer les pics (matin/soir) et le creux en journée.</div>", unsafe_allow_html=True)

    fig = px.line(hourly_fau_2024, x="hour", y="detections", markers=True)
    fig.update_traces(line_color=C_FAU)
    fig.update_layout(template="plotly_dark", height=340, margin=dict(l=10,r=10,t=30,b=10),
                      xaxis_title="Heure", yaxis_title="Détections")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='meta'><b>Graphique :</b> courbe (profil circadien). <b>Variable :</b> position + marqueurs.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with a2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("2) Jour vs Nuit (faune, 2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> comparer explicitement la nuit et le jour.</div>", unsafe_allow_html=True)

    fig = px.bar(dn_fau_2024, x="day_night", y="detections", text="detections",
                 color="day_night", color_discrete_map={"Jour": C_MUT, "Nuit": C_FAU})
    fig.update_layout(template="plotly_dark", height=340, margin=dict(l=10,r=10,t=30,b=10),
                      xaxis_title="", yaxis_title="Détections")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='meta'><b>Graphique :</b> barres. <b>Variable :</b> hauteur (détections), couleur (jour/nuit).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

b1, b2 = st.columns([1.2, 0.8])
with b1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("3) Saisonnalité (faune, 2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> détecter les périodes d’activité forte/faible.</div>", unsafe_allow_html=True)

    fig = px.line(monthly_fau_2024, x="month", y="detections", markers=True)
    fig.update_traces(line_color=C_FAU)
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=30,b=10),
                      xaxis_title="Mois", yaxis_title="Détections")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='meta'><b>Graphique :</b> courbe. <b>Variable :</b> position (mois→détections).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("4) Espèces les plus détectées (Top 5, 2024)")
    st.markdown("<div class='meta'><b>Objectif :</b> contextualiser l’activité (espèces dominantes).</div>", unsafe_allow_html=True)

    fig = px.bar(top_species_2024.sort_values("detections"), x="detections", y="species", orientation="h", text="detections")
    fig.update_traces(marker_color=C_FAU)
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=30,b=10),
                      xaxis_title="Détections", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='meta'><b>Graphique :</b> barres horizontales. <b>Variable :</b> longueur (détections).</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ACTE III — INTERACTION (Bloc 3) : tes visus clés (map + horloge)
# ============================================================
st.markdown('<a name="acte3"></a>', unsafe_allow_html=True)
st.header("Acte III — La coexistence : partager l’espace… ou le temps ?")

st.markdown(
    """
<div class="narr">
<b>Message (Bloc 3).</b> Les pics d’activité humaine et animale se recouvrent peu à l’échelle horaire.
La faune est plus active quand la fréquentation baisse (soir/nuit), ce qui suggère un <b>évitement temporel</b>.
À l’échelle saisonnière, humains et faune augmentent en été, mais cela ne signifie pas un recouvrement fin dans la journée.
</div>
""",
    unsafe_allow_html=True,
)

# --- 1) Courbes horaires normalisées (2024)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("1) Comparaison horaire normalisée (2024)")
st.markdown("<div class='meta'><b>Objectif :</b> comparer les profils (forme) indépendamment des volumes.</div>", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(x=comp_hour["hour"], y=comp_hour["humans_norm"], mode="lines+markers",
                         name="Humains (norm.)", line=dict(color=C_HUM, width=3)))
fig.add_trace(go.Scatter(x=comp_hour["hour"], y=comp_hour["fauna_norm"], mode="lines+markers",
                         name="Faune (norm.)", line=dict(color=C_FAU, width=3)))
fig.update_layout(template="plotly_dark", height=340, margin=dict(l=10,r=10,t=30,b=10),
                  xaxis_title="Heure", yaxis_title="Activité normalisée (0–1)")
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<div class='meta'>"
    "<b>Graphique :</b> 2 courbes normalisées. "
    "<b>Variables visuelles :</b> position (heure/activité), couleur (humains/faune)."
    "</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

# --- 2) CARTE friction : humains (couleur) vs faune (taille)  ✅ (ancien visu)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("2) Carte de friction : Humains (couleur) vs Faune (taille)")
st.markdown("<div class='meta'><b>Objectif :</b> visualiser la coexistence spatiale et les zones de pression.</div>", unsafe_allow_html=True)

map_stats = df.groupby("station").agg(
    is_human=("is_human", "sum"),
    is_animal=("is_animal", "sum"),
    latitude=("latitude", "first"),
    longitude=("longitude", "first"),
    altitude=("altitude", "first"),
).dropna()

fig_map = px.scatter_mapbox(
    map_stats,
    lat="latitude", lon="longitude",
    color="is_human", size="is_animal",
    color_continuous_scale="OrRd",
    size_max=32, zoom=10.5, height=560,
    hover_name=map_stats.index,
    hover_data={"altitude": True, "is_human": True, "is_animal": True},
    title="Chamonix / Mont-Blanc — zones de pression et présence animale"
)
fig_map.update_layout(mapbox_style="carto-darkmatter", template="plotly_dark", margin=dict(l=10,r=10,t=50,b=10))
st.plotly_chart(fig_map, use_container_width=True)

st.markdown(
    "<div class='meta'>"
    "<b>Graphique :</b> carte (scatter). "
    "<b>Variables :</b> position (lat/lon), couleur (intensité humaine), taille (détections faune), tooltip (altitude)."
    "</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

# --- 3) HORLOGE polaire (ancien visu) ✅
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("3) Horloge circadienne : le partage du temps (Humains vs Faune)")
st.markdown("<div class='meta'><b>Objectif :</b> montrer le décalage temporel sur 24h de façon intuitive.</div>", unsafe_allow_html=True)

# distributions relatives (0..1) sur 24h
hum_hour = hum.groupby("hour").size()
fau_hour = fau.groupby("hour").size()

# s'assurer 0..23
idx = pd.Index(range(24), name="hour")
hum_hour = hum_hour.reindex(idx, fill_value=0)
fau_hour = fau_hour.reindex(idx, fill_value=0)

hum_dist = hum_hour / (hum_hour.sum() if hum_hour.sum() > 0 else 1)
fau_dist = fau_hour / (fau_hour.sum() if fau_hour.sum() > 0 else 1)

theta = (idx.values * 15)  # 24h -> 360° (15° par heure)

fig_polar = go.Figure()
fig_polar.add_trace(go.Scatterpolar(
    r=hum_dist.values, theta=theta,
    fill="toself", name="Humains",
    line=dict(color=C_HUM, width=3)
))
fig_polar.add_trace(go.Scatterpolar(
    r=fau_dist.values, theta=theta,
    fill="toself", name="Faune",
    line=dict(color=C_FAU, width=3)
))
fig_polar.update_layout(
    template="plotly_dark",
    height=520,
    title="Horloge de coexistence (répartition relative des détections)",
    polar=dict(
        radialaxis=dict(visible=False),
        angularaxis=dict(
            tickvals=list(range(0, 360, 30)),
            ticktext=[str(h) for h in range(0, 24, 2)]
        )
    ),
    margin=dict(l=10,r=10,t=60,b=10)
)
st.plotly_chart(fig_polar, use_container_width=True)

st.markdown(
    "<div class='meta'>"
    "<b>Graphique :</b> polaire (horloge). "
    "<b>Variables :</b> angle = heure, rayon = proportion d’activité, couleur = humains/faune."
    "</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

# --- 4) Comparaison saisonnière normalisée (2024)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("4) Comparaison saisonnière normalisée (2024)")
st.markdown("<div class='meta'><b>Objectif :</b> vérifier la coïncidence estivale (sans confondre avec l’horaire).</div>", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(x=comp_month["month"], y=comp_month["humans_norm"], mode="lines+markers",
                         name="Humains (norm.)", line=dict(color=C_HUM, width=3)))
fig.add_trace(go.Scatter(x=comp_month["month"], y=comp_month["fauna_norm"], mode="lines+markers",
                         name="Faune (norm.)", line=dict(color=C_FAU, width=3)))
fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=30,b=10),
                  xaxis_title="Mois", yaxis_title="Activité normalisée (0–1)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# CONCLUSION
# ============================================================
st.markdown('<a name="final"></a>', unsafe_allow_html=True)
st.header("Conclusion — L’histoire en une idée")

st.markdown(
    """
<div class="narr narr-green">
Les données indiquent une coexistence partielle fondée sur un <b>décalage temporel</b> : la montagne est très fréquentée en journée (surtout en été), alors que la faune concentre davantage son activité la nuit et aux heures crépusculaires.  
À l’échelle saisonnière, humains et faune augmentent tous deux en été, mais l’opposition reste nette à l’échelle fine (horaire), compatible avec une stratégie d’évitement temporel.
</div>
""",
    unsafe_allow_html=True,
)

st.caption("Données : CREA Mont-Blanc | Narration : TP Noté EDA — DS4SC (2026)")
