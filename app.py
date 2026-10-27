import os
import requests
import streamlit as st
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Chef de Chantier TP - Pro OS",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Design "Best-Seller BTP" : Dark mode épuré, typographie moderne, finitions industrielles
st.markdown(
    """
    <style>
    .main { background-color: #0b0f19; padding: 1rem; color: #f8fafc; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: 600; height: 2.8em; background-color: #f59e0b; color: #0b0f19; border: none; }
    .stButton button:hover { background-color: #d97706; }
    .card { background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1f2937; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2); margin-bottom: 15px; }
    .alert-card { background-color: #450a0a; border: 1px solid #991b1b; padding: 15px; border-radius: 8px; color: #f87171; margin-bottom: 15px; font-weight: 600; }
    .success-card { background-color: #064e3b; border: 1px solid #065f46; padding: 15px; border-radius: 8px; color: #34d399; margin-bottom: 15px; font-weight: 600; }
    h1, h2, h3 { color: #ffffff !important; }
    p, span, label { color: #9ca3af !important; }
    /* Style pour les onglets principaux */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #111827; padding: 6px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { height: 40px; border-radius: 6px; color: #9ca3af; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #f59e0b !important; color: #0b0f19 !important; }
    </style>
""",
    unsafe_allow_html=True,
)


# --- MOTEUR IA TP EXPERT ---
class TPExpertEngine:

  def __init__(self, api_key):
    self.api_key = api_key
    self.api_url = "https://api.mistral.ai/v1/chat/completions"

  def _call(self, system_prompt, messages_history):
    if not self.api_key:
      return "⚠️ Erreur : Clé API non définie."
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-tiny",
        "messages": [{"role": "system", "content": system_prompt}]
        + messages_history,
        "temperature": 0.2,
    }
    try:
      res = requests.post(
          self.api_url, headers=headers, json=payload, timeout=35
      )
      if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
      elif res.status_code == 429:
        return (
            "⚠️ **Surcharge API (Erreur 429)** : Attends 15 secondes et réessaie."
        )
      else:
        return f"Erreur API ({res.status_code}): {res.text}"
    except Exception as e:
      return f"Erreur réseau : {str(e)}"

  def preparer_chantier(self, type_travaux, contraintes, moyens):
    sys = (
        "Tu es un conducteur de travaux principal TP senior. Rédige une note de"
        " préparation de chantier ultra-précise et structurée.\n\nREGLE D'OR"
        " STRICTE : Si les informations fournies sont insuffisantes, écris"
        " clairement : '⚠️ Information manquante : il me manque [X] pour"
        " répondre précisément'."
    )
    user_msg = (
        f"Type de travaux : {type_travaux}\nContraintes terrain :"
        f" {contraintes}\nMoyens : {moyens}"
    )
    return self._call(sys, [{"role": "user", "content": user_msg}])

  def generer_planning_ia(self, description_chantier, alea):
    sys = (
        "Tu es un conducteur de travaux principal expert en VRD. Génère un"
        " planning de chantier détaillé par semaines/jours sous forme de"
        " recommandations d'adaptation suite à un aléa."
    )
    user_msg = (
        f"Planning actuel / Tâches : {description_chantier}\nAléa ou"
        f" modification à intégrer : {alea}"
    )
    return self._call(sys, [{"role": "user", "content": user_msg}])

  def discuter_probleme(self, historique_chat):
    sys = (
        "Tu es un conducteur de travaux TP chevronné. Tu réponds aux questions"
        " techniques du chef de chantier.\n\nRÈGLES D'OR :\n1. Donne des"
        " solutions pratiques et sécurisées.\n2. SI TU NE SAIS PAS ou si tu manques"
        " de données critiques, DIS CLAIREMENT que tu n'as pas l'information."
    )
    return self._call(sys, historique_chat)


# --- CLÉ API EN DUR ---
API_KEY = "mstrl_vMSBfYr10D2KBnRWjRLVPS0gLsspL7Yg_0q5fTA"
ia_engine = TPExpertEngine(API_KEY)

# --- INITIALISATION DE LA SESSION ---
if "chantiers" not in st.session_state:
  st.session_state.chantiers = {}

if "catalog_engins" not in st.session_state:
  st.session_state.catalog_engins = [
      {
          "nom": "Pelle chenilles 15t",
          "usage": "Terrassement & fouilles",
          "cout": 75,
      },
      {
          "nom": "Bobcat compact",
          "usage": "Régalage & propreté",
          "cout": 45,
      },
      {
          "nom": "Camion 8x4 Bi-benne",
          "usage": "Évacuation / Appros",
          "cout": 85,
      },
      {
          "nom": "Finisseur d'enrobés",
          "usage": "Pose tapis enrobé",
          "cout": 120,
      },
  ]

# ==========================================
# BARRE LATÉRALE : GESTION DES CHANTIERS UNIQUEMENT
# ==========================================
st.sidebar.title("🏗️ CHEF DE CHANTIER OS")
st.sidebar.caption("Pilotage Terrain Haute Performance")
st.sidebar.markdown("---")

liste_chantiers = list(st.session_state.chantiers.keys())

if not liste_chantiers:
  st.sidebar.warning("⚠️ Aucun chantier actif. Créez-en un pour commencer.")
  nouveau_c_init = st.sidebar.text_input(
      "Nouveau Chantier", placeholder="Ex: ZAC Nord - VRD"
  )
  if st.sidebar.button("Créer le chantier"):
    if nouveau_c_init:
      st.session_state.chantiers[nouveau_c_init] = {
          "historique_chat": [],
          "preparations": [],
          "stocks": {},
          "projet_infos": "Aucune note validée.",
          "achats_urgents": "RAS",
          "notes_rapides": "",
          "planning_taches": [],
          "compagnons": [],
          "ateliers": [],
      }
      st.rerun()
  st.title("🏗️ Bienvenue sur votre Assistant Chef de Chantier")
  st.info(
      "👈 Veuillez créer votre premier chantier dans le menu latéral pour"
      " déverrouiller l'application."
  )
  st.stop()

chantier_actif = st.sidebar.selectbox(
    "📍 Chantier en cours", options=liste_chantiers
)

with st.sidebar.expander("➕ Créer un autre chantier"):
  autre_c = st.text_input("Nom du chantier", placeholder="Nom...")
  if st.button("Ajouter"):
    if autre_c:
      st.session_state.chantiers[autre_c] = {
          "historique_chat": [],
          "preparations": [],
          "stocks": {},
          "projet_infos": "Aucune note validée.",
          "achats_urgents": "RAS",
          "notes_rapides": "",
          "planning_taches": [],
          "compagnons": [],
          "ateliers": [],
      }
      st.rerun()

data_c = st.session_state.chantiers[chantier_actif]

# En-tête principal épuré
st.title(f"🏗️ {chantier_actif}")
st.markdown("---")

# ==========================================
# NAVIGATION PRINCIPALE PAR ONGLETS HAUT (STYLE BEST-SELLER)
# ==========================================
(
    tab_dash,
    tab_plan,
    tab_prep,
    tab_stock,
    tab_calc,
    tab_mat,
    tab_ai,
) = st.tabs([
    "⚡ Tableau de Bord",
    "📅 Planning & Ateliers",
    "🛠️ Préparation IA",
    "📦 Stocks & BDL",
    "🧮 Calculs & Ateliers",
    "🚜 Matériel & Coûts",
    "💬 Assistant Expert",
])

# ==========================================
# 1. TABLEAU DE BORD
# ==========================================
with tab_dash:
  st.subheader("⚡ Vue Synthétique & Flux Chantier")

  col_info1, col_info2 = st.columns(2)
  with col_info1:
    st.markdown(
        f"""<div class='card'>
        <b>📋 Projet Épinglé :</b><br>
        {data_c.get('projet_infos', 'Aucune note injectée.')}
        </div>""",
        unsafe_allow_html=True,
    )
  with col_info2:
    st.markdown(
        f"""<div class='card'>
        <b>🛒 Pré-requis / Achats :</b><br>
        {data_c.get('achats_urgents', 'Aucun pré-requis.')}
        </div>""",
        unsafe_allow_html=True,
    )

  st.markdown("### 📝 Bloc-Notes Rapide Terrain")
  notes_actuelles = data_c.get("notes_rapides", "")
  nouveau_texte_notes = st.text_area(
      "Notes instantanées (sauvegarde automatique)",
      value=notes_actuelles,
      height=90,
  )
  if nouveau_texte_notes != notes_actuelles:
    data_c["notes_rapides"] = nouveau_texte_notes

  st.markdown("---")
  st.markdown("### 🚨 Alertes Stocks & Flux")
  alertes = []
  for item, vals in data_c["stocks"].items():
    dispo = vals["recu"] - vals["pose"]
    reste = vals["requis"] - vals["pose"]
    manque = vals["requis"] - vals["recu"]
    if reste > dispo and manque > 0:
      alertes.append((item, dispo, reste, manque, vals["unite"]))

  if alertes:
    for item, dispo, reste, manque, unite in alertes:
      st.markdown(
          f"""<div class="alert-card">
            🚨 RUPTURE IMMINENTE : {item}<br>
            • En stock terrain : {dispo} {unite} | Reste à poser : {reste} {unite}<br>
            👉 <b>Action requise : Commander d'urgence {manque} {unite} supplémentaires !</b>
            </div>""",
          unsafe_allow_html=True,
      )
  else:
    st.markdown(
        """<div class="success-card">✅ Flux des matériaux sous contrôle. Aucun réapprovisionnement critique en retard.</div>""",
        unsafe_allow_html=True,
    )

# ==========================================
# 2. PLANNING & SOUS-ATELIERS
# ==========================================
with tab_plan:
  st.subheader("📅 Pilotage du Planning & Dispatching Équipe")

  sub_pl1, sub_pl2, sub_pl3 = st.tabs([
      "📊 Éditeur de Planning & Aléas",
      "👥 Gestion des Compagnons",
      "🛠️ Dispatching Sous-Ateliers",
  ])

  with sub_pl1:
    st.markdown("### 🗓️ Tableau Interactif des Tâches")
    if not data_c["planning_taches"]:
      data_c["planning_taches"] = [
          {"Tâche / Lot": "Réseaux secs (AEP / EP)", "Durée": "3 semaines", "Période": "S1 à S3"},
          {"Tâche / Lot": "Préparation pose bordures", "Durée": "2 semaines", "Période": "S4 à S5"},
      ]

    df_planning = pd.DataFrame(data_c["planning_taches"])
    edited_df = st.data_editor(
        df_planning, num_rows="dynamic", use_container_width=True
    )

    if st.button("Enregistrer les modifications du planning"):
      data_c["planning_taches"] = edited_df.to_dict("records")
      st.success("✅ Planning mis à jour avec succès !")

    st.markdown("---")
    st.markdown("### ⚡ Analyse d'Aléa par l'IA")
    desc_alea = st.text_input(
        "Décris un imprévu (ex: Intervention mur en S3)",
        placeholder="Ex: Mur à reprendre en semaine 3",
    )
    if st.button("Consulter l'IA pour l'impact de l'aléa"):
      if desc_alea:
        with st.spinner("Analyse de l'impact..."):
          res_ia_planning = ia_engine.generer_planning_ia(
              str(data_c["planning_taches"]), desc_alea
          )
          st.markdown(
              f"<div class='card'>{res_ia_planning}</div>",
              unsafe_allow_html=True,
          )
      else:
        st.warning("Précise l'aléa.")

  with sub_pl2:
    st.markdown("### 👷 Référentiel des Compagnons")
    col_c1, col_c2 = st.columns([3, 1])
    nouveau_comp = col_c1.text_input(
        "Nom et spécialité du compagnon", placeholder="Ex: Thomas (Pelliste)"
    )
    if col_c2.button("Ajouter"):
      if nouveau_comp:
        data_c["compagnons"].append(nouveau_comp)
        st.rerun()

    for idx, c in enumerate(data_c.get("compagnons", [])):
      col_n, col_d = st.columns([4, 1])
      col_n.markdown(f"• **{c}**")
      if col_d.button("Supprimer", key=f"del_c_{idx}"):
        data_c["compagnons"].pop(idx)
        st.rerun()

  with sub_pl3:
    st.markdown("### 🛠️ Organisation des Sous-Ateliers")
    with st.expander("➕ Créer un sous-atelier"):
      nom_at = st.text_input("Nom de l'atelier (ex: Équipe Réseau)")
      tache_at = st.text_input("Tâche liée")
      membres_at = st.multiselect(
          "Compagnons affectés", options=data_c.get("compagnons", [])
      )
      if st.button("Enregistrer l'atelier"):
        if nom_at:
          data_c["ateliers"].append({
              "nom": nom_at,
              "membres": membres_at,
              "tache": tache_at,
          })
          st.success("Atelier créé !")
          st.rerun()

    for idx, at in enumerate(data_c.get("ateliers", [])):
      st.markdown(
          f"""<div class='card'>
          <b>🛠️ {at['nom']}</b><br>
          • Tâche : {at['tache']}<br>
          • Compagnons : {', '.join(at['membres']) if at['membres'] else 'Aucun'}
          </div>""",
          unsafe_allow_html=True,
      )
      if st.button("Supprimer l'atelier", key=f"del_at_{idx}"):
        data_c["ateliers"].pop(idx)
        st.rerun()

# ==========================================
# 3. PRÉPARATION IA
# ==========================================
with tab_prep:
  st.subheader("🛠️ Préparation de Chantier & Méthodes IA")

  col_p1, col_p2 = st.columns(2)
  with col_p1:
    type_t = st.text_input(
        "Type de travaux", placeholder="Ex: Réseau EU Ø300"
    )
    contraintes_t = st.text_area(
        "Contraintes terrain", placeholder="Ex: Nappe phréatique"
    )
  with col_p2:
    moyens_t = st.text_area("Moyens disponibles", placeholder="Ex: Pelle 18t")

  if st.button("Lancer l'analyse technique IA"):
    if type_t:
      with st.spinner("Analyse..."):
        res = ia_engine.preparer_chantier(type_t, contraintes_t, moyens_t)
        data_c["preparations"].append({"titre": type_t, "contenu": res})
        st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)

  for idx, p in enumerate(reversed(data_c["preparations"])):
    with st.expander(f"📋 {p['titre']}"):
      st.markdown(p["contenu"])
      if st.button("Épingler au Tableau de Bord", key=f"ping_{idx}"):
        data_c["projet_infos"] = f"<b>Projet :</b> {p['titre']}"
        st.success("Épinglé !")

# ==========================================
# 4. STOCKS & BDL
# ==========================================
with tab_stock:
  st.subheader("📦 Suivi des Stocks & BDL")

  sub_s1, sub_s2 = st.tabs(["📊 Tableau Global", "⚙️ Saisie BDL"])

  with sub_s1:
    if not data_c["stocks"]:
      st.info("Aucun matériau enregistré.")
    else:
      tableau_data = []
      for item, vals in data_c["stocks"].items():
        dispo = vals["recu"] - vals["pose"]
        reste = vals["requis"] - vals["pose"]
        manque = max(0, vals["requis"] - vals["recu"])
        tableau_data.append({
            "Matériau": item,
            "Prévu": f"{vals['requis']} {vals['unite']}",
            "Reçu": f"{vals['recu']} {vals['unite']}",
            "Posé": f"{vals['pose']} {vals['unite']}",
            "Dispo": f"{dispo} {vals['unite']}",
            "À Commander": f"{manque} {vals['unite']}",
        })
      st.dataframe(tableau_data, use_container_width=True)

  with sub_s2:
    with st.expander("➕ Ajouter un matériau"):
      c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
      n_mat = c1.text_input("Nom")
      req_m = c2.number_input("Prévu", value=50.0)
      rec_m = c3.number_input("Reçu", value=0.0)
      uni_m = c4.selectbox("Unité", ["mL", "m3", "Tonnes", "Unités", "m2"])
      if st.button("Enregistrer"):
        if n_mat:
          data_c["stocks"][n_mat] = {
              "requis": req_m,
              "recu": rec_m,
              "pose": 0.0,
              "unite": uni_m,
          }
          st.rerun()

    for item, vals in list(data_c["stocks"].items()):
      with st.expander(f"📦 {item}"):
        nr = st.number_input(
            "Reçu cumulé", value=float(vals["recu"]), key=f"r_{item}"
        )
        np = st.number_input("Posé", value=float(vals["pose"]), key=f"p_{item}")
        data_c["stocks"][item]["recu"] = nr
        data_c["stocks"][item]["pose"] = np
        if st.button("Supprimer", key=f"del_mat_{item}"):
          del data_c["stocks"][item]
          st.rerun()

# ==========================================
# 5. CALCULS & ATELIERS
# ==========================================
with tab_calc:
  st.subheader("🧮 Centre de Calculs Métier")

  sub_c1, sub_c2, sub_c3 = st.tabs([
      "🚛 Terrassement",
      "🛣️ Enrobés",
      "⚙️ Rabotage",
  ])

  with sub_c1:
    v_pl = st.number_input("Volume en place (m³)", value=200.0)
    v_fois = v_pl * 1.2
    st.markdown(
        f"<div class='card'>Volume foisonné : <b>{v_fois:.1f} m³</b></div>",
        unsafe_allow_html=True,
    )
    st.bar_chart({"Volume": {"En Place": v_pl, "Foisonné": v_fois}})

  with sub_c2:
    surf = st.number_input("Surface (m²)", value=1500.0)
    ep = st.number_input("Épaisseur (cm)", value=6.0)
    tonnage = surf * (ep / 100.0) * 2.4
    st.markdown(
        f"<div class='card'>Tonnage estimé : <b>{tonnage:.1f} Tonnes</b></div>",
        unsafe_allow_html=True,
    )
    st.bar_chart({"Tonnage": {"Total (t)": tonnage}})

  with sub_c3:
    s_rab = st.number_input("Surface rabotage (m²)", value=1000.0)
    p_rab = st.number_input("Profondeur (cm)", value=5.0)
    v_fr = s_rab * (p_rab / 100.0)
    st.markdown(
        f"<div class='card'>Volume fraiseat : <b>{v_fr:.1f} m³</b></div>",
        unsafe_allow_html=True,
    )
    st.bar_chart({"Fraisage": {"Volume (m3)": v_fr}})

# ==========================================
# 6. MATÉRIEL & COÛTS
# ==========================================
with tab_mat:
  st.subheader("🚜 Référentiel Matériel & Coûts")

  with st.expander("➕ Ajouter un engin"):
    n_e = st.text_input("Nom")
    u_e = st.text_input("Usage")
    c_e = st.number_input("Coût horaire (€/h)", value=65.0)
    if st.button("Ajouter"):
      if n_e:
        st.session_state.catalog_engins.append(
            {"nom": n_e, "usage": u_e, "cout": c_e}
        )
        st.rerun()

  for idx, engin in enumerate(st.session_state.catalog_engins):
    with st.expander(f"⚙️ {engin['nom']} ({engin['cout']} €/h)"):
      if st.button("Supprimer", key=f"del_eng_{idx}"):
        st.session_state.catalog_engins.pop(idx)
        st.rerun()

# ==========================================
# 7. ASSISTANT EXPERT
# ==========================================
with tab_ai:
  st.subheader("💬 Assistant Expert Terrain")

  for m in data_c["historique_chat"]:
    with st.chat_message(m["role"]):
      st.markdown(m["content"])

  user_q = st.chat_input("Pose ta question...")
  if user_q:
    data_c["historique_chat"].append({"role": "user", "content": user_q})
    with st.chat_message("user"):
      st.markdown(user_q)
    with st.chat_message("assistant"):
      rep = ia_engine.discuter_probleme(data_c["historique_chat"])
      st.markdown(rep)
      data_c["historique_chat"].append({"role": "assistant", "content": rep})
