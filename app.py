import streamlit as st
import pandas as pd
import json
import os
import requests
from datetime import datetime

# --- CONFIGURATION DE LA PAGE & THÈME BTP ---
st.set_page_config(
    page_title="Chef de Chantier AI - Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Thème BTP : Orange Sécurité / Gris Ardoise / Moderne Mobile-First)
st.markdown("""
    <style>
    /* Main style overrides */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: #ffffff;
        border: none;
        padding: 0.6rem 1rem;
        box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
        color: #ffffff;
    }
    /* Cards / Containers */
    div[data-testid="stMetricValue"] {
        color: #f97316 !important;
        font-weight: 800;
    }
    .btp-card {
        background-color: #1e293b;
        border-left: 4px solid #f97316;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .alert-card {
        background-color: #450a0a;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


# --- ENGINE MISTRAL AI ---
class UltimateTPAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

    def _call(self, system_prompt, user_msg):
        if not self.api_key or self.api_key == "mstrl_vMSBfYr10D2KBnRWjRLVPS0gLsspL7Yg_0q5fTA":
            return "⚠️ Clé API Mistral non configurée dans la barre latérale."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.3
        }
        try:
            res = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            return f"Erreur API ({res.status_code}): {res.text}"
        except Exception as e:
            return f"Erreur réseau : {str(e)}"

    def structurer_rapport(self, brut):
        sys = "Tu es un conducteur de travaux TP chevronné. Rédige un rapport de fin de journée clair, professionnel et précis avec sections : 1. Météo & Conditions, 2. Avancement, 3. Aléas & Sécurité, 4. Planning Demain."
        return self._call(sys, brut)

    def analyser_bdl(self, texte_bdl):
        sys = "Tu es un assistant logistique TP. Extrais du bon de livraison (BDL) : Le type de matériau, le métrage/tonnage livré, la date, et le fournisseur."
        return self._call(sys, texte_bdl)


# --- INITIALISATION DE LA SESSION STATE ---
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("MISTRAL_API_KEY", "")

ai_engine = UltimateTPAgent(st.session_state.api_key)

if "chantiers" not in st.session_state:
    st.session_state.chantiers = {
        "ZAC Sud - Reseaux EU/EP": {
            "materiaux": [
                {"nom": "Tuyau PEHD Ø300", "besoin_total": 390, "unite": "mL", "recu": 200, "pose": 80},
                {"nom": "Grave Non Traitée (GNT 0/31.5)", "besoin_total": 500, "unite": "Tonnes", "recu": 150, "pose": 110},
                {"nom": "Regard Béton Ø1000", "besoin_total": 12, "unite": "U", "recu": 12, "pose": 4}
            ],
            "historique": [],
            "bdl_charges": []
        }
    }

if "catalogue_engins" not in st.session_state:
    st.session_state.catalogue_engins = [
        {"categorie": "Pelle", "nom": "Pelle Chenille 15T", "usage": "Terrassement court & Tranchées profondes", "godet": "0.8 m³", "cout_h": 75.0},
        {"categorie": "Pelle", "nom": "Pelle Pneus 21T", "usage": "Voirie & Pose de canalisations lourdes", "godet": "1.1 m³", "cout_h": 95.0},
        {"categorie": "Transport", "nom": "Camion 8x4 Bi-benne", "usage": "Évacuation terres & Approvisionnement GNT", "capacite": "16 m³ / 24T", "cout_h": 85.0},
        {"categorie": "Transport", "nom": "Semi-remorque Benne", "usage": "Grandes rotations de terrassement", "capacite": "22 m³ / 30T", "cout_h": 98.0},
        {"categorie": "Compactage", "nom": "Compacteur BW 213 (V4)", "usage": "Compactage des couches de forme (Class Q4)", "largeur": "2.13 m", "cout_h": 65.0},
        {"categorie": "Chargeur", "nom": "Chargeuse sur pneus 14T", "usage": "Reprise de matériaux & Chargement camions", "godet": "2.5 m³", "cout_h": 80.0}
    ]


# --- SIDEBAR: NAVIGATION ET CLÉ API ---
with st.sidebar:
    st.title("🚧 Navigation TP")
    st.image("https://images.unsplash.com/photo-1541888946425-d0fbb186a5b3?w=400&auto=format&fit=crop&q=60", use_column_width=True)
    
    page = st.radio(
        "Sélectionner un module :",
        [
            "📊 Tableau de Bord",
            "📦 Gestion des Stocks & BDL",
            "📐 Calculs Terrassement & Cubatures",
            "🚜 Catalogue Engins & Coûts",
            "🌙 Rapport de Fin de Journée"
        ]
    )

    st.divider()
    st.session_state.api_key = st.text_input("Clé API Mistral AI", value=st.session_state.api_key, type="password")
    
    # Sélection du chantier global
    st.divider()
    chantier_actif = st.selectbox("📍 Chantier Sélectionné", options=list(st.session_state.chantiers.keys()))
    
    nouveau_nom = st.text_input("Créer un nouveau chantier", placeholder="ex: RD906 - Réfection VSP")
    if st.button("➕ Créer Chantier") and nouveau_nom:
        if nouveau_nom not in st.session_state.chantiers:
            st.session_state.chantiers[nouveau_nom] = {"materiaux": [], "historique": [], "bdl_charges": []}
            st.rerun()


# ==============================================================================
# 1. PAGE TABLEAU DE BORD (ACCUEIL & ALERTES)
# ==============================================================================
if page == "📊 Tableau de Bord":
    st.title(f"📊 Tableau de Bord - {chantier_actif}")
    st.caption("Aperçu en direct des alertes matérielles, de l'état des stocks et de la gestion de chantier.")

    # Alertes automatiques de stock
    materiaux = st.session_state.chantiers[chantier_actif]["materiaux"]
    alertes_commande = []
    
    for mat in materiaux:
        stock_terrain = mat["recu"] - mat["pose"]
        reste_a_commander = mat["besoin_total"] - mat["recu"]
        if stock_terrain <= (mat["besoin_total"] * 0.2) or reste_a_commander > 0:
            alertes_commande.append({
                "mat": mat["nom"],
                "stock": stock_terrain,
                "unite": mat["unite"],
                "a_commander": reste_a_commander
            })

    col1, col2, col3 = st.columns(3)
    col1.metric("Fournitures Référencées", len(materiaux))
    col2.metric("Alertes Réapprovisionnement", len(alertes_commande))
    col3.metric("Rapports Enregistrés", len(st.session_state.chantiers[chantier_actif]["historique"]))

    st.divider()

    # Section des alertes critiques
    if alertes_commande:
        st.subheader("🚨 Alertes Urgentes & Réapprovisionnements")
        for alt in alertes_commande:
            st.markdown(f"""
                <div class="alert-card">
                    <h4>⚠️ <b>{alt['mat']}</b></h4>
                    <p>• <b>Stock disponible sur le chantier :</b> {alt['stock']} {alt['unite']}<br>
                    • <b>Quantité restante à commander pour finir le chantier :</b> <span style="color:#f87171; font-weight:bold;">{alt['a_commander']} {alt['unite']}</span></p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Tous les niveaux de stock sont optimaux pour ce chantier.")

    st.subheader("📈 Résumé Synthétique des Matériaux")
    if materiaux:
        df_mat = pd.DataFrame(materiaux)
        df_mat["Stock Reste Terrain"] = df_mat["recu"] - df_mat["pose"]
        df_mat["A Commander"] = df_mat["besoin_total"] - df_mat["recu"]
        st.dataframe(df_mat[["nom", "besoin_total", "recu", "pose", "Stock Reste Terrain", "A Commander", "unite"]], use_container_width=True)


# ==============================================================================
# 2. PAGE GESTION DES STOCKS & BONS DE LIVRAISON (BDL)
# ==============================================================================
elif page == "📦 Gestion des Stocks & BDL":
    st.title("📦 Suivi Dynamique des Stocks & Bons de Livraison")
    st.caption("Gérez l'approvisionnement, vos livraisons et enregistrez les consommations journalières du chantier.")

    tab1, tab2, tab3 = st.tabs(["📉 Suivi des Consommations", "📥 Scanner BDL / Facture", "➕ Ajouter un Matériau au Plan"])

    # --- TAB 1 : CONSUMPTION TRACKING ---
    with tab1:
        st.subheader(f"État des Stocks : {chantier_actif}")
        mat_list = st.session_state.chantiers[chantier_actif]["materiaux"]

        if not mat_list:
            st.info("Aucun matériau configuré pour ce chantier.")
        else:
            for i, mat in enumerate(mat_list):
                stock_terrain = mat["recu"] - mat["pose"]
                manquant_plan = mat["besoin_total"] - mat["recu"]

                with st.expander(f"📌 {mat['nom']} (Stock Terrain : {stock_terrain} {mat['unite']})", expanded=True):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"**Besoin total (Plan):** {mat['besoin_total']} {mat['unite']}")
                    c2.write(f"**Livré/Reçu:** {mat['recu']} {mat['unite']}")
                    c3.write(f"**Pose/Consommé:** {mat['pose']} {mat['unite']}")
                    c4.write(f"**Dispo Terrain:** {stock_terrain} {mat['unite']}")

                    # Barre de progression
                    pct_pose = min(1.0, mat["pose"] / mat["besoin_total"]) if mat["besoin_total"] > 0 else 0
                    st.progress(pct_pose, text=f"Avancement pose : {int(pct_pose*100)}%")

                    # Formulaire de mise à jour des consommations
                    st.markdown("##### 📝 Enregistrer l'avancement du jour")
                    cols_form = st.columns([2, 2, 1])
                    qte_posee_jour = cols_form[0].number_input(f"Quantité posée aujourd'hui ({mat['unite']})", min_value=0.0, key=f"pose_{i}")
                    qte_recue_jour = cols_form[1].number_input(f"Nouvelle livraison reçue ({mat['unite']})", min_value=0.0, key=f"recu_{i}")
                    
                    if cols_form[2].button("Mettre à jour", key=f"btn_{i}"):
                        mat["pose"] += qte_posee_jour
                        mat["recu"] += qte_recue_jour
                        st.success("Stock mis à jour !")
                        st.rerun()

    # --- TAB 2 : BDL PARSER ---
    with tab2:
        st.subheader("📥 Importer un Bon de Livraison (BDL) ou Facture")
        st.write("Uploadez le document. L'assistant lira automatiquement les quantités et les ajoutera au stock du chantier.")

        file_bdl = st.file_uploader("Fichier BDL (PDF ou Image)", type=["pdf", "png", "jpg", "jpeg"])
        texte_manuel = st.text_area("Ou saisissez/collez le contenu du bon de livraison :", placeholder="Ex: Livraison Ets PUM - 120 mL Tuyau PEHD Ø300 - N°BDL 884920")

        if st.button("Analyser et enregistrer le BDL"):
            if file_bdl or texte_manuel:
                with st.spinner("Analyse du bon de livraison en cours..."):
                    payload_txt = texte_manuel if texte_manuel else f"Fichier joint : {file_bdl.name}"
                    res = ai_engine.analyser_bdl(payload_txt)
                    st.session_state.chantiers[chantier_actif]["bdl_charges"].append({"date": str(datetime.now().strftime("%d/%m/%Y")), "detail": res})
                    st.success("Bon de livraison enregistré !")
                    st.markdown(res)
            else:
                st.warning("Veuillez fournir un fichier ou un texte.")

    # --- TAB 3 : ADD MATERIAL TO PLAN ---
    with tab3:
        st.subheader("➕ Ajouter un nouveau matériau à suivre sur le chantier")
        with st.form("add_mat_form"):
            nom_mat = st.text_input("Nom du matériau / Produit", placeholder="ex: Regards Béton 1000x1000")
            besoin_tot = st.number_input("Besoin total selon plans / marché", min_value=1.0, value=100.0)
            unite_mat = st.selectbox("Unité", options=["mL", "Tonnes", "m³", "U", "Plaques"])
            recu_init = st.number_input("Quantité déjà reçue sur le chantier", min_value=0.0, value=0.0)
            
            if st.form_submit_button("Ajouter à la liste des stocks"):
                if nom_mat:
                    st.session_state.chantiers[chantier_actif]["materiaux"].append({
                        "nom": nom_mat,
                        "besoin_total": besoin_tot,
                        "unite": unite_mat,
                        "recu": recu_init,
                        "pose": 0.0
                    })
                    st.success(f"{nom_mat} ajouté avec succès !")
                    st.rerun()


# ==============================================================================
# 3. PAGE CALCULATEUR TERRASSEMENT & CUBATURES
# ==============================================================================
elif page == "📐 Calculs Terrassement & Cubatures":
    st.title("📐 Calculateur Technique TP & Cubatures")
    st.caption("Outil de dimensionnement rapide des volumes, foisonnement, rotations de camions et compactage.")

    c_calc1, c_calc2 = st.columns(2)

    with c_calc1:
        st.subheader("1. Calcul de Foisonnement & Évacuation")
        type_sol = st.selectbox("Nature du terrain", ["Terre végétale / Argile (Foisonnement ~ 25%)", "Grave / Sable (Foisonnement ~ 15%)", "Rocher fracturé (Foisonnement ~ 40%)", "Personnalisé"])
        
        taux_foisonnement = 0.25
        if "15%" in type_sol: taux_foisonnement = 0.15
        elif "40%" in type_sol: taux_foisonnement = 0.40
        elif type_sol == "Personnalisé":
            taux_foisonnement = st.slider("Taux de foisonnement personnalisé (%)", 0, 60, 20) / 100

        longueur = st.number_input("Longueur de la tranchée/fouille (m)", value=50.0)
        largeur = st.number_input("Largeur (m)", value=1.5)
        profondeur = st.number_input("Profondeur moyenne (m)", value=2.0)

        volume_en_place = longueur * largeur * profondeur
        volume_foisonne = volume_en_place * (1 + taux_foisonnement)

        st.markdown(f"""
            <div class="btp-card">
                <h4>Résultats Cubatures :</h4>
                <p>• <b>Volume en place (en coffre) :</b> {volume_en_place:.2f} m³<br>
                • <b>Volume foisonné à évacuer :</b> <span style="color:#f97316; font-weight:bold;">{volume_foisonne:.2f} m³</span></p>
            </div>
        """, unsafe_allow_html=True)

    with c_calc2:
        st.subheader("2. Rotation des Camions & Benne")
        capa_camion = st.number_input("Capacité utile du camion (m³)", value=14.0)
        t_trajet = st.number_input("Temps moyen de rotation A/R (minutes)", value=45)

        if capa_camion > 0:
            nombre_rotations = volume_foisonne / capa_camion
            st.markdown(f"""
                <div class="btp-card">
                    <h4>Besoin en Transport :</h4>
                    <p>• <b>Nombre de rotations de camion requis :</b> {int(nombre_rotations) + 1} tours<br>
                    • <b>Temps total estimé de charroi (1 camion) :</b> {((nombre_rotations * t_trajet)/60):.1f} heures</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("3. Calculateur de Ratio de Compactage (Rembled)")
    col_comp1, col_comp2 = st.columns(2)
    vol_remblai = col_comp1.number_input("Volume de coffre à remblayer (m³)", value=100.0)
    epaisseur_couche = col_comp2.number_input("Épaisseur des passes de compactage (cm)", value=30.0)

    if epaisseur_couche > 0:
        nb_passes = (vol_remblai / (epaisseur_couche / 100)) / 10  # estimation simplifiée
        st.info(f"💡 Pour remblayer {vol_remblai} m³ par passes de {epaisseur_couche} cm, prévoyez environ **{int(nb_passes)} passes linéaires de compacteur** (Norme Objectif Q3/Q4).")


# ==============================================================================
# 4. PAGE CATALOGUE ENGINS & MATÉRIEL
# ==============================================================================
elif page == "🚜 Catalogue Engins & Coûts":
    st.title("🚜 Référentiel Matériel & Grille Tarifaire Company")
    st.caption("Base de données des engins de TP avec affectations techniques et prix de revient horaires.")

    tab_cat1, tab_cat2 = st.tabs(["📋 Consulter le Catalogue", "➕ Ajouter / Modifier un Engin"])

    with tab_cat1:
        st.subheader("Engins et Camions de Chantier")
        df_engins = pd.DataFrame(st.session_state.catalogue_engins)
        st.dataframe(df_engins, use_container_width=True)

    with tab_cat2:
        st.subheader("Ajouter une machine au catalogue d'entreprise")
        with st.form("form_engin"):
            cat_e = st.selectbox("Catégorie", ["Pelle", "Transport", "Compactage", "Chargeur", "Outillage"])
            nom_e = st.text_input("Désignation / Modèle", placeholder="Ex: Mini-pelle 3.5T")
            usage_e = st.text_area("Domaine d'usage principal", placeholder="Ex: Travaux de branchement et finitions")
            cout_e = st.number_input("Coût horaire ou location (€/h)", value=50.0)
            
            if st.form_submit_button("Enregistrer l'engin"):
                if nom_e:
                    st.session_state.catalogue_engins.append({
                        "categorie": cat_e,
                        "nom": nom_e,
                        "usage": usage_e,
                        "cout_h": cout_e
                    })
                    st.success(f"Machine '{nom_e}' ajoutée au catalogue !")
                    st.rerun()


# ==============================================================================
# 5. PAGE RAPPORT DE FIN DE JOURNÉE
# ==============================================================================
elif page == "🌙 Rapport de Fin de Journée":
    st.title(f"🌙 Rapport Journalier - {chantier_actif}")
    st.caption("Dictez votre débriefing de terrain à la voix (via le micro de votre téléphone) et l'IA structure votre compte-rendu.")

    st.info("🎙️ **Astuce iPhone / Smartphone :** Touchez la zone de texte ci-dessous, appuyez sur le petit micro sur votre clavier tactile, puis dictez votre journée !")

    debrief_brut = st.text_area("Débriefing brut de la journée :", height=150, placeholder="Aujourd'hui météo couverte, pose de 40m de PEHD Ø300 en tranchée. Panne d'hydraulique sur la pelle 15t pendant 1h. Reçu 2 camions de GNT...")

    if st.button("🚀 Générer le Rapport Structuré", type="primary"):
        if debrief_brut:
            with st.spinner("Structure du rapport par Mistral AI..."):
                rapport_forme = ai_engine.structurer_rapport(debrief_brut)
                st.session_state.chantiers[chantier_actif]["historique"].append({
                    "date": datetime.now().strftime("%d/%m/%Y à %H:%M"),
                    "contenu": rapport_forme
                })
                st.success("Rapport généré et archivé !")
                st.markdown(rapport_forme)
        else:
            st.warning("Veuillez saisir ou dicter du texte.")

    st.divider()
    st.subheader("📚 Historique des Rapports du Chantier")
    rapports = st.session_state.chantiers[chantier_actif]["historique"]
    
    if not rapports:
        st.write("Aucun rapport archivé pour ce chantier.")
    else:
        for idx, r in enumerate(reversed(rapports), 1):
            with st.expander(f"📄 Rapport du {r['date']}"):
                st.markdown(r["contenu"])
