import os
import requests
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Chef de Chantier AI - Pro Edition",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { padding: 1rem; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; color: white; }
    .alert-box { background-color: #7f1d1d; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; }
    .ok-box { background-color: #065f46; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; }
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
        "model": "mistral-tiny",  # Modèle allégé pour éviter les saturations 429
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
            "⚠️ **Trop de requêtes (Erreur 429)** : L'API Mistral sature. Attends"
            " 15 secondes et réessaie."
        )
      else:
        return f"Erreur API ({res.status_code}): {res.text}"
    except Exception as e:
      return f"Erreur réseau : {str(e)}"

  def preparer_chantier(self, type_travaux, contraintes, moyens):
    sys = (
        "Tu es un conducteur de travaux principal TP senior. Rédige une note de"
        " préparation de chantier ultra-précise et professionnelle.\n\nREGLE"
        " D'OR : Si les informations fournies sont insuffisantes, dis"
        " clairement : '⚠️ Information manquante : il me manque [X] pour"
        " répondre précisément' au lieu d'inventer."
    )
    user_msg = (
        f"Type de travaux : {type_travaux}\nContraintes terrain/météo :"
        f" {contraintes}\nMoyens envisagés : {moyens}"
    )
    return self._call(sys, [{"role": "user", "content": user_msg}])

  def discuter_probleme(self, historique_chat):
    sys = (
        "Tu es un conducteur de travaux TP chevronné. Tu réponds aux questions"
        " du chef de chantier sur le terrain.\n\nRÈGLES D'OR :\n1. Donne des"
        " conseils pratiques et sécurisés.\n2. SI TU NE SAIS PAS ou si tu manques"
        " de données, DIS CLAIREMENT que tu n'as pas l'information."
    )
    return self._call(sys, historique_chat)

  def analyser_document_ou_photo(self, nom_fichier, description_contexte):
    sys = (
        "Tu es un expert technique TP. Analyse la description et les données du"
        " fichier transmis et donne ton diagnostic technique et tes"
        " recommandations."
    )
    user_msg = (
        f"Nom du document : {nom_fichier}\nContexte/Question du chef de"
        f" chantier : {description_contexte}"
    )
    return self._call(sys, [{"role": "user", "content": user_msg}])


# --- CLÉ API INTÉGRÉE EN DUR ---
API_KEY = "mstrl_vMSBfYr10D2KBnRWjRLVPS0gLsspL7Yg_0q5fTA"
ia_engine = TPExpertEngine(API_KEY)

# --- INITIALISATION DE LA SESSION STATE ---
if "chantiers" not in st.session_state:
  st.session_state.chantiers = {
      "Réseau EU & EP ZAC Nord": {
          "historique_chat": [],
          "documents": [],
          "rapports": [],
          "stocks": {
              "Tuyau PEHD Ø300": {
                  "requis": 390,
                  "recu": 200,
                  "pose": 80,
                  "unite": "mL",
              },
              "Bordure T2": {
                  "requis": 500,
                  "recu": 500,
                  "pose": 320,
                  "unite": "mL",
              },
          },
      }
  }

if "catalog_engins" not in st.session_state:
  st.session_state.catalog_engins = [
      {
          "nom": "Pelle chenilles 15-18 Tonnes",
          "usage": "Terrassement principal, tranchées profondes, pose de réseaux",
          "cout": 75,
      },
      {
          "nom": "Bobcat / Chargeuse compacte",
          "usage": "Nettoyage, régalage de matériaux, manutention sur petite surface",
          "cout": 45,
      },
      {
          "nom": "Camion 8x4 Bi-benne",
          "usage": "Évacuation de déblais, approvisionnement en granulats (capacité 14m³)",
          "cout": 85,
      },
      {
          "nom": "Compacteur Tandem V2/V3",
          "usage": "Compactage de fonds de forme et couches de roulement",
          "cout": 55,
      },
  ]

# --- NAVIGATION LATÉRALE ---
st.sidebar.title("🏗️ Chef de Chantier AI")
st.sidebar.caption("L'assistant terrain ultime TP")

chantier_actif = st.sidebar.selectbox(
    "📍 Chantier actif", options=list(st.session_state.chantiers.keys())
)

nouveau_chantier = st.sidebar.text_input(
    "➕ Nouveau chantier", placeholder="Nom du chantier..."
)
if st.sidebar.button("Créer le chantier") and nouveau_chantier:
  st.session_state.chantiers[nouveau_chantier] = {
      "historique_chat": [],
      "documents": [],
      "rapports": [],
      "stocks": {},
  }
  st.rerun()

st.sidebar.divider()

menu = st.sidebar.radio(
    "Menu Navigation",
    [
        "📊 Dashboard & Alertes",
        "🛠️ Préparation & Méthodes",
        "💬 Assistant TP (Chat & Prob.)",
        "📦 Stocks & Matériaux",
        "📐 Calculs Cubatures & Comp.",
        "🚜 Catalogue Matériel",
        "📁 Plans & Photos",
        "🌙 Bilan de Journée",
    ],
)

data_chantier = st.session_state.chantiers[chantier_actif]

# ==========================================
# 1. DASHBOARD & ALERTES
# ==========================================
if menu == "📊 Dashboard & Alertes":
  st.header(f"📊 Tableau de Bord : {chantier_actif}")

  alertes = []
  for item, vals in data_chantier["stocks"].items():
    stock_sur_chantier = vals["recu"] - vals["pose"]
    reste_a_poser = vals["requis"] - vals["pose"]
    manquant_a_commander = vals["requis"] - vals["recu"]

    if reste_a_poser > stock_sur_chantier and manquant_a_commander > 0:
      alertes.append({
          "item": item,
          "stock_terrain": stock_sur_chantier,
          "reste_a_poser": reste_a_poser,
          "a_commander": manquant_a_commander,
          "unite": vals["unite"],
      })

  if alertes:
    for al in alertes:
      st.markdown(
          f"""<div class="alert-box">
            🚨 ALERTE STOCK : {al['item']}<br>
            • En stock terrain : {al['stock_terrain']} {al['unite']}<br>
            • Reste à poser : {al['reste_a_poser']} {al['unite']}<br>
            ⚠️ <b>RÉAPPROVISIONNEMENT NÉCESSAIRE : Commandez d'urgence {al['a_commander']} {al['unite']} supplémentaires !</b>
            </div>""",
          unsafe_allow_html=True,
      )
  else:
    st.markdown(
        """<div class="ok-box">✅ Aucun problème de stock détecté pour ce chantier.</div>""",
        unsafe_allow_html=True,
    )

  col1, col2, col3 = st.columns(3)
  col1.metric("Documents & Plans", len(data_chantier["documents"]))
  col2.metric("Rapports rédigés", len(data_chantier["rapports"]))
  col3.metric("Articles suivis en stock", len(data_chantier["stocks"]))

# ==========================================
# 2. PRÉPARATION & MÉTHODES
# ==========================================
elif menu == "🛠️ Préparation & Méthodes":
  st.header(f"🛠️ Préparation de Chantier : {chantier_actif}")
  type_travaux = st.text_input(
      "Type de travaux à réaliser",
      placeholder="Ex: Pose de réseau d'eau potable PEHD 220",
  )
  contraintes = st.text_area(
      "Contraintes spécifiques (Terrain, météo, circulation, réseaux)",
      placeholder=(
          "Ex: Sol rocheux / présence d'eau / présence réseaux sensibles"
      ),
  )
  moyens = st.text_area(
      "Moyens envisagés", placeholder="Ex: 1 Pelle 15t, 2 ouvriers"
  )

  if st.button("Lancer l'analyse de préparation", type="primary"):
    if type_travaux:
      with st.spinner("Analyse technique en cours..."):
        res = ia_engine.preparer_chantier(type_travaux, contraintes, moyens)
        st.markdown("### 📋 Plan d'Attaque & Préconisations :")
        st.markdown(res)
    else:
      st.warning("Veuillez renseigner le type de travaux.")

# ==========================================
# 3. ASSISTANT TP (CHAT DIRECT)
# ==========================================
elif menu == "💬 Assistant TP (Chat & Prob.)":
  st.header("💬 Assistant TP - Résolution de Problèmes en Direct")
  for msg in data_chantier["historique_chat"]:
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

  prompt = st.chat_input("Pose ta question terrain ici...")
  if prompt:
    data_chantier["historique_chat"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("Réflexion..."):
        reponse = ia_engine.discuter_probleme(data_chantier["historique_chat"])
        st.markdown(reponse)
        data_chantier["historique_chat"].append(
            {"role": "assistant", "content": reponse}
        )

# ==========================================
# 4. STOCKS & MATÉRIAUX
# ==========================================
elif menu == "📦 Stocks & Matériaux":
  st.header(f"📦 Gestion des Stocks : {chantier_actif}")

  st.subheader("➕ Ajouter un matériau au suivi")
  c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
  nom_mat = c1.text_input("Nom du matériau (Ex: Regard béton 100x100)")
  req_mat = c2.number_input("Métré Total Prévu", min_value=0.0, value=50.0)
  recu_mat = c3.number_input("Reçu sur chantier", min_value=0.0, value=0.0)
  unite_mat = c4.selectbox("Unité", ["mL", "m3", "Tonnes", "Unités", "m2"])

  if st.button("Enregistrer le matériau"):
    if nom_mat:
      data_chantier["stocks"][nom_mat] = {
          "requis": req_mat,
          "recu": recu_mat,
          "pose": 0.0,
          "unite": unite_mat,
      }
      st.success(f"{nom_mat} ajouté !")
      st.rerun()

  st.divider()
  st.subheader("📋 Suivi, Consommation & Suppression")

  if not data_chantier["stocks"]:
    st.write("Aucun matériau suivi pour l'instant.")
  else:
    for item, vals in list(data_chantier["stocks"].items()):
      with st.expander(
          f"📦 {item} (Stock dispo : {vals['recu'] - vals['pose']} {vals['unite']})"
      ):
        c_recu, c_pose, c_del = st.columns([2, 2, 1])

        nouveau_recu = c_recu.number_input(
            f"Reçu cumulé",
            value=float(vals["recu"]),
            key=f"recu_{item}",
        )
        nouveau_pose = c_pose.number_input(
            f"Posé / Consommé",
            value=float(vals["pose"]),
            key=f"pose_{item}",
        )

        data_chantier["stocks"][item]["recu"] = nouveau_recu
        data_chantier["stocks"][item]["pose"] = nouveau_pose

        stock_dispo = nouveau_recu - nouveau_pose
        manquant = vals["requis"] - nouveau_recu

        st.write(f"• Reste à poser : {vals['requis'] - nouveau_pose} {vals['unite']}")

        if (vals["requis"] - nouveau_pose) > stock_dispo:
          st.error(
              f"⚠️ ALERTE : Manque {manquant} {vals['unite']} à commander !"
          )
        else:
          st.success("✅ Stock suffisant.")

        if c_del.button("🗑️ Supprimer", key=f"del_mat_{item}"):
          del data_chantier["stocks"][item]
          st.success(f"Matériau {item} supprimé avec succès !")
          st.rerun()

# ==========================================
# 5. CALCULS CUBATURES & COMPACTAGE
# ==========================================
elif menu == "📐 Calculs Cubatures & Comp.":
  st.header("📐 Calculateur Technique Terrassement")
  tab_terr, tab_comp = st.tabs(
      ["🚛 Foisonnement & Camions", "🚜 Ratios de Compactage"]
  )

  with tab_terr:
    v_en_place = st.number_input(
        "Volume en place (m³)", min_value=1.0, value=100.0
    )
    mat_type = st.selectbox(
        "Nature du sol",
        [
            "Terre végétale (Foisonnement 20%)",
            "Argile / Marne (Foisonnement 30%)",
            "Grave / Sable (Foisonnement 15%)",
            "Rocher abattu (Foisonnement 50%)",
        ],
    )
    coeff_dict = {
        "Terre végétale (Foisonnement 20%)": 1.20,
        "Argile / Marne (Foisonnement 30%)": 1.30,
        "Grave / Sable (Foisonnement 15%)": 1.15,
        "Rocher abattu (Foisonnement 50%)": 1.50,
    }
    v_foisonne = v_en_place * coeff_dict[mat_type]
    capa_camion = st.number_input(
        "Capacité utile du camion (m³)", min_value=1.0, value=10.0
    )
    nb_rotations = int(v_foisonne / capa_camion) + (
        1 if v_foisonne % capa_camion > 0 else 0
    )
    st.success(f"**Volume foisonné :** {v_foisonne:.1f} m³")
    st.info(f"**Rotations nécessaires :** {nb_rotations} camions")

  with tab_comp:
    epaisseur_couche = st.number_input(
        "Épaisseur couche (cm)", min_value=5, value=20
    )
    object_q = st.selectbox(
        "Objectif",
        ["Q4 (Remblai courant)", "Q3 (Assise de chaussée / Tranchée voirie)"],
    )
    if epaisseur_couche > 30:
      st.warning("⚠️ Prévoir compacteur lourd et 6 à 8 passes.")
    else:
      st.info("Prévoir 4 à 6 passes croisées.")

# ==========================================
# 6. CATALOGUE MATÉRIEL
# ==========================================
elif menu == "🚜 Catalogue Matériel":
  st.header("🚜 Catalogue Engins & Coûts Horaires")

  with st.expander("➕ Ajouter un nouvel engin au catalogue"):
    nom_engin = st.text_input("Nom de la machine (Ex: Tombereau articulé)")
    usage_engin = st.text_input(
        "Usage principal (Ex: Transport de terre en grande distance)"
    )
    cout_engin = st.number_input(
        "Coût horaire estimé (€/h)", min_value=0.0, value=65.0
    )
    if st.button("Ajouter l'engin au catalogue"):
      if nom_engin:
        st.session_state.catalog_engins.append({
            "nom": nom_engin,
            "usage": usage_engin,
            "cout": cout_engin,
        })
        st.success(f"'{nom_engin}' ajouté avec succès !")
        st.rerun()

  st.divider()
  st.subheader("📋 Liste des engins enregistrés")

  for idx, item in enumerate(st.session_state.catalog_engins):
    with st.expander(f"⚙️ {item['nom']} ({item['cout']} €/h)"):
      st.write(f"**Usage :** {item['usage']}")
      if st.button(f"🗑️ Supprimer l'engin", key=f"del_engin_{idx}"):
        st.session_state.catalog_engins.pop(idx)
        st.success("Engin supprimé !")
        st.rerun()

# ==========================================
# 7. PLANS & PHOTOS
# ==========================================
elif menu == "📁 Plans & Photos":
  st.header(f"📁 Analyse de Documents : {chantier_actif}")
  fichier = st.file_uploader(
      "Glisser une photo ou un PDF", type=["jpg", "png", "jpeg", "pdf"]
  )
  question_doc = st.text_input("Question sur le document")

  if st.button("Analyser", type="primary"):
    if fichier:
      with st.spinner("Analyse..."):
        res_doc = ia_engine.analyser_document_ou_photo(
            fichier.name, question_doc
        )
        data_chantier["documents"].append(
            {"nom": fichier.name, "analyse": res_doc}
        )
        st.success("Analysé et sauvegardé !")
        st.markdown(res_doc)
    else:
      st.warning("Choisis un fichier.")

  for doc in data_chantier["documents"]:
    with st.expander(f"📎 {doc['nom']}"):
      st.markdown(doc["analyse"])

# ==========================================
# 8. BILAN DE JOURNÉE
# ==========================================
elif menu == "🌙 Bilan de Journée":
  st.header(f"🌙 Rapport Journalier : {chantier_actif}")
  debrief = st.text_area("Débrief brut de la journée", height=150)

  if st.button("Générer le rapport structuré", type="primary"):
    if debrief:
      with st.spinner("Rédaction..."):
        sys_rap = (
            "Tu es un chef de chantier TP. Rédige un rapport structuré : 1."
            " Météo, 2. Travaux réalisés, 3. Consommation, 4. Imprévus, 5."
            " Programme demain."
        )
        rap = ia_engine._call(sys_rap, [{"role": "user", "content": debrief}])
        data_chantier["rapports"].append(rap)
        st.success("Rapport archivé !")
        st.markdown(rap)
    else:
      st.warning("Écris ton bilan.")
