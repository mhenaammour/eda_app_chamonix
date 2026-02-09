import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.chart_container import chart_container

# --- CONFIGURATION ET STYLE ---
st.set_page_config(page_title="Le Sommet en Sursis", page_icon="🦌", layout="wide")

# CSS Custom pour un look "Magazine / Storytelling"
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMarkdown h1 { font-family: 'Playfair Display', serif; font-size: 4rem; color: #FF9F1C; text-align: center; }
    .stMarkdown h2 { color: #2D6A4F; border-bottom: 2px solid #2D6A4F; padding-bottom: 10px; }
    .narrative-text { font-size: 1.2rem; line-height: 1.6; text-align: justify; padding: 20px; background: #1b1e23; border-radius: 10px; border-left: 5px solid #FF9F1C; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_all_data():
    lifts = pd.read_csv('remontees_long_all.csv', sep=';')
    pp_res = pd.read_csv('PP_results_cleaned.csv', sep=';')
    pp_stat = pd.read_excel('PP_stations_MB.xlsx', sheet_name='Feuil2')
    lifts_geo = pd.read_excel('remontees_coordonnees.xlsx', sheet_name='Feuil1')
    
    # Nettoyage
    pp_res['date'] = pd.to_datetime(pp_res['date'], format='%d/%m/%Y %H:%M', errors='coerce')
    human_tags = ['humain', 'vtt', 'vehicule', 'randonneur', 'chien']
    pp_res['is_human'] = pp_res['prediction_first'].str.contains('|'.join(human_tags), case=False, na=False)
    pp_res['is_animal'] = (~pp_res['is_human']) & (~pp_res['prediction_first'].isin(['vide', 'indéfini', 'autre']))
    
    full_pp = pp_res.merge(pp_stat, on='station', how='left')
    return lifts, full_pp, lifts_geo

lifts, df, lifts_geo = load_all_data()

# --- INTRODUCTION ---
st.title("🏔️ LE SOMMET EN SURSIS")
st.subheader("Une exploration des frontières invisibles entre l'Homme et la Faune au Mont-Blanc")

st.markdown('<div class="narrative-text">Bienvenue dans la Vallée de Chamonix. Ici, la majesté des cimes cache un conflit silencieux. '
            'Grâce aux données du CREA Mont-Blanc, nous avons cartographié la présence des randonneurs et des animaux sauvages. '
            'Préparez-vous à découvrir comment notre soif de grand air redessine la vie sauvage.</div>', unsafe_allow_html=True)

st.divider()

# --- CHAPITRE 1 : L'INVASION ESTIVALE ---
st.header("I. L'Invasion Silencieuse")
col1, col2 = st.columns([1, 2])

with col1:
    st.write("### Le poids du tourisme")
    st.write("Chaque été, les remontées mécaniques transportent des milliers de visiteurs vers les sommets. "
             "Ce flux massif crée une onde de choc sonore et visuelle qui s'étend bien au-delà des sentiers balisés.")
    
    total_h = len(df[df['is_human']])
    st.metric("Passages Humains Détectés", f"{total_h:,}")
    style_metric_cards(background_color="#1b1e23", border_left_color="#FF9F1C")

with col2:
    with chart_container(df):
        # Evolution mensuelle humaine vs animale
        df['month'] = df['date'].dt.month
        monthly = df.groupby('month')[['is_human', 'is_animal']].sum().reset_index()
        fig1 = px.line(monthly, x='month', y=['is_human', 'is_animal'], 
                      labels={'value': 'Nombre de détections', 'month': 'Mois'},
                      title="Saisonalité : Le Croisement des Courbes",
                      color_discrete_map={'is_human': '#FF9F1C', 'is_animal': '#2D6A4F'})
        st.plotly_chart(fig1, use_container_width=True)

# --- CHAPITRE 2 : LA FRAGMENTATION SPATIALE ---
st.header("II. Territoires Disputés")
st.markdown('<div class="narrative-text">Regardez cette carte. Les points rouges indiquent où nous sommes les plus nombreux. '
            'Observez comment les grands cercles verts (la faune) s\'éloignent systématiquement des zones de forte chaleur humaine.</div>', unsafe_allow_html=True)

map_stats = df.groupby('station').agg({
    'is_human': 'sum', 'is_animal': 'sum', 'latitude': 'first', 'longitude': 'first', 'altitude': 'first'
}).dropna()

fig_map = px.scatter_mapbox(map_stats, lat="latitude", lon="longitude", 
                            color="is_human", size="is_animal",
                            color_continuous_scale="OrRd", 
                            size_max=30, zoom=11, height=600,
                            hover_name=map_stats.index,
                            title="Carte de Friction : Humains (Couleur) vs Animaux (Taille)")
fig_map.update_layout(mapbox_style="carto-darkmatter")
st.plotly_chart(fig_map, use_container_width=True)

# --- CHAPITRE 3 : LA FUITE DANS LA NUIT ---
st.header("III. Le Partage du Temps")
col3, col4 = st.columns([2, 1])

with col3:
    df['hour'] = df['date'].dt.hour
    h_dist = df[df['is_human']].groupby('hour').size() / len(df[df['is_human']])
    a_dist = df[df['is_animal']].groupby('hour').size() / len(df[df['is_animal']])
    
    fig_polar = go.Figure()
    fig_polar.add_trace(go.Scatterpolar(r=h_dist.values, theta=h_dist.index*15, fill='toself', name='Humains', line_color='#FF9F1C'))
    fig_polar.add_trace(go.Scatterpolar(r=a_dist.values, theta=a_dist.index*15, fill='toself', name='Faune', line_color='#2D6A4F'))
    fig_polar.update_layout(polar=dict(radialaxis=dict(visible=False), angularaxis=dict(tickvals=list(range(0,360,15)), ticktext=list(range(24)))),
                            template="plotly_dark", title="Horloge Circadienne de Coexistence")
    st.plotly_chart(fig_polar, use_container_width=True)

with col4:
    st.write("### Le Couvre-feu")
    st.write("Ce graphique montre que la coexistence n'est pas spatiale, mais temporelle. "
             "La faune sauvage est devenue **nocturne**. Elle attend que le dernier téléphérique redescende (17h-18h) "
             "pour oser sortir de l'ombre des forêts.")

# --- CHAPITRE 4 : ANALYSE PAR ESPÈCE ---
st.header("IV. Qui sont les Résistants ?")
species = st.selectbox("Sélectionnez une espèce pour voir sa stratégie :", df[df['is_animal']]['prediction_first'].unique())

spec_df = df[df['prediction_first'] == species]
fig_spec = px.histogram(spec_df, x="altitude", nbins=20, color_discrete_sequence=['#2D6A4F'],
                        title=f"Distribution altitudinale du {species.upper()}")
st.plotly_chart(fig_spec, use_container_width=True)

# --- CONCLUSION ---
st.divider()
st.markdown("""
### Conclusion : Un équilibre à réinventer
Les données sont claires : notre présence en montagne n'est pas neutre. Elle impose à la faune un stress permanent, 
une fuite vers les hauteurs et une vie nocturne forcée. 

**En tant que visiteurs, notre rôle est simple : rester sur les sentiers, respecter le calme crépusculaire, et garder nos distances.**
""")
st.caption("Données : CREA Mont-Blanc | Dashboard : Master DS4SC 2026")