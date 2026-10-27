import base64
import json
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

# Style CSS pour une ergonomie optimale sur Mobile & PC
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
    if not self.api_key or self.api_key == "mstrl_vMSBfYr10D2KBnRWjRLVPS0gLsspL7Yg_0q5fTA":
      return "⚠️ Erreur : Clé API Mistral non configurée dans les paramètres."

    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "system", "content": system_prompt}]
        + messages_history,
        "temperature": 0.2,  # Température basse pour privilégier la précision technique
    }
    try:
      res = requests.post(
          self.api_url, headers=headers, json=payload, timeout=35
      )
      if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
      return f"Erreur API ({res.status_code}): {res.text}"
    except Exception as e:
      return f"Erreur réseau : {str(e)}"

  def preparer_chantier(self, type_travaux, contraintes, moyens):
    sys = (
        "Tu es un conducteur de travaux principal TP senior (30 ans"
        " d'expérience en terrassement, VRD, assainissement, ouvrages d'art)."
        " Rédige une note de préparation de chantier ultra-précise et"
        " professionnelle.\n\nREGLE D'OR ABSOLUE : Si les informations"
        " fournies par l'utilisateur sont insuffisantes pour faire un calcul"
        " exact ou donner un conseil sécurisé, dis clairement : '⚠️"
        " Information manquante : il me manque [X] pour répondre précisément'"
        " au lieu d'inventer des hypothèses sans fondement."
    )
    user_msg = (
        f"Type de travaux : {type_travaux}\nContraintes terrain/météo :"
        f" {contraintes}\nMoyens envisagés : {moyens}"
    )
    return self._call(sys, [{"role": "user", "content": user_msg}])

  def discuter_probleme(self, historique_chat):
    sys = (
        "Tu es un conducteur de travaux TP chevronné. Tu réponds aux questions"
        " du chef de chantier sur le terrain pour résoudre des problèmes"
        " imprévus (méthodes, pannes, litiges, sécurité, règles de l'art,"
        " réseaux DT-DICT, compactage).\n\nRÈGLES D'OR :\n1. Donne des conseils"
        " pratiques, sécurisés et directement applicables sur le chantier.\n2."
        " SI TU NE SAIS PAS ou si tu manques de données (nature de sol, cotes,"
        " classe de granulats), DIS CLAIREMENT que tu n'as pas l'information et"
        " demande au chef de chantier de vérifier l'élément exact."
    )
    return self._call(sys, historique_chat)

  def analyser_document_ou_photo(self, nom_fichier, description_contexte):
    sys = (
        "Tu es un expert technique TP. Analyse la description et les données du"
        " fichier transmis (plan, photo de fouille, CCTP, rapport G2,"
        " attestation d'essais de plaque) et donne ton diagnostic technique,"
        " les points de non-conformité potentiels et les recommandations pour"
        " le chef de chantier."
    )
    user_msg = (
        f"Nom du document : {nom_fichier}\nContexte/Question du chef de"
        f" chantier : {description_contexte}"
    )
    return self._call(sys, [{"role": "user", "content": user_msg}])


# Initialisation Clé API
API_KEY = os.getenv("MISTRAL_API_KEY", "METS_TA_CLE_MISTRAL_ICI")
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
              "Grave Non Traitée 0/31.5": {
                  "requis": 450,
                  "recu": 300,
                  "pose": 280,
                  "unite": "Tonnes",
              },
          },
      }
  }

# --- NAVIGATION LATÉRALE (MENU PRINCIPAL) ---
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

  # Calcul des alertes de réapprovisionnement automatique
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
# 2. PRÉPARATION & MÉTHODES (Nouvel Onglet Requis !)
# ==========================================
elif menu == "🛠️ Préparation & Méthodes":
  st.header(f"🛠️ Préparation de Chantier : {chantier_actif}")
  st.write(
      "Soumets un projet à venir ou une nouvelle phase de chantier pour"
      " obtenir l'analyse de méthodes, le dimensionnement d'atelier et les"
      " cadences."
  )

  type_travaux = st.text_input(
      "Type de travaux à réaliser",
      placeholder="Ex: Pose de réseau d'eau potable PEHD 220 en bord de D900",
  )
  contraintes = st.text_area(
      "Contraintes spécifiques (Terrain, météo, circulation, réseaux)",
      placeholder=(
          "Ex: Sol rocheux / présence d'eau à 1m50 / présence fibre optique /"
          " circulation alternée nécessaire"
      ),
  )
  moyens = st.text_area(
      "Moyens envisagés ou disponibles",
      placeholder="Ex: 1 Pelle 15t, 1 Bobcat, 2 ouvriers, 1 dumper",
  )

  if st.button("Lancer l'analyse de préparation", type="primary"):
    if type_travaux:
      with st.spinner("Analyse technique par l'ingénieur méthode..."):
        res = ia_engine.preparer_chantier(type_travaux, contraintes, moyens)
        st.markdown("### 📋 Plan d'Attaque & Préconisations Méthodes :")
        st.markdown(res)
    else:
      st.warning("Veuillez renseigner le type de travaux.")

# ==========================================
# 3. ASSISTANT TP (CHAT DIRECT & PROBLÈMES)
# ==========================================
elif menu == "💬 Assistant TP (Chat & Prob.)":
  st.header("💬 Assistant TP - Résolution de Problèmes en Direct")
  st.info(
      "💡 Pose n'importe quelle question terrain (panne, doute technique, sol"
      " instable, litige). Si l'IA n'a pas les éléments nécessaires, elle te"
      " le dira clairement sans inventer."
  )

  # Affichage de l'historique
  for msg in data_chantier["historique_chat"]:
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

  prompt = st.chat_input("Ex: J'ai un fond de fouille argileux détrempé, quelle couche de forme poser ?")
  if prompt:
    data_chantier["historique_chat"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner("Analyse technique en cours..."):
        reponse = ia_engine.discuter_probleme(data_chantier["historique_chat"])
        st.markdown(reponse)
        data_chantier["historique_chat"].append(
            {"role": "assistant", "content": reponse}
        )

# ==========================================
# 4. STOCKS & MATÉRIAUX (Logique Automatique)
# ==========================================
elif menu == "📦 Stocks & Matériaux":
  st.header(f"📦 Gestion des Stocks : {chantier_actif}")

  st.subheader("➕ Ajouter un matériau / fourniture au marché")
  c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
  nom_mat = c1.text_input("Nom du matériau (Ex: PEHD Ø300)")
  req_mat = c2.number_input(
      "Métré Total Prévu (Plans)", min_value=0.0, value=100.0
  )
  recu_mat = c3.number_input("Tonnage/Métré Reçu (BDL)", min_value=0.0, value=0.0)
  unite_mat = c4.selectbox("Unité", ["mL", "m3", "Tonnes", "Unités", "m2"])

  if st.button("Enregistrer le matériau"):
    if nom_mat:
      data_chantier["stocks"][nom_mat] = {
          "requis": req_mat,
          "recu": recu_mat,
          "pose": 0.0,
          "unite": unite_mat,
      }
      st.success(f"{nom_mat} ajouté au suivi des stocks !")
      st.rerun()

  st.divider()
  st.subheader("📋 Suivi de Consommation & Réceptions sur Chantier")

  for item, vals in list(data_chantier["stocks"].items()):
    with st.expander(f"📦 {item} (Unité : {vals['unite']})", expanded=True):
      c_recu, c_pose, c_etat = st.columns(3)

      # Mettre à jour la quantité reçue
      nouveau_recu = c_recu.number_input(
          f"Reçu sur chantier (Cumul BDL)",
          value=float(vals["recu"]),
          key=f"recu_{item}",
      )
      # Mettre à jour la quantité posée
      nouveau_pose = c_pose.number_input(
          f"Posé / Consommé terrain",
          value=float(vals["pose"]),
          key=f"pose_{item}",
      )

      data_chantier["stocks"][item]["recu"] = nouveau_recu
      data_chantier["stocks"][item]["pose"] = nouveau_pose

      stock_dispo = nouveau_recu - nouveau_pose
      manquant = vals["requis"] - nouveau_recu

      st.write(
          f"• **Stock physique disponible sur le terrain :** {stock_dispo}"
          f" {vals['unite']}"
      )
      st.write(
          f"• **Reste à poser pour finir le chantier :**"
          f" {vals['requis'] - nouveau_pose} {vals['unite']}"
      )

      if (vals["requis"] - nouveau_pose) > stock_dispo:
        st.error(
            f"⚠️ ALERTE : Il vous manque {manquant} {vals['unite']} à commander"
            " pour terminer la quantité prévue au plan !"
        )
      else:
        st.success("✅ Stock terrain suffisant pour les travaux en cours.")

# ==========================================
# 5. CALCULS CUBATURES & COMPACTAGE
# ==========================================
elif menu == "📐 Calculs Cubatures & Comp.":
  st.header("📐 Calculateur Technique Terrassement")

  tab_terr, tab_comp = st.tabs(
      ["🚛 Foisonnement & Camions", "🚜 Ratios de Compactage"]
  )

  with tab_terr:
    st.subheader("Calculateur de Foisonnement & Nbre de Camions")
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
    coeff = coeff_dict[mat_type]
    v_foisonne = v_en_place * coeff

    capa_camion = st.number_input(
        "Capacité utile du camion (m³)", min_value=1.0, value=10.0
    )
    nb_rotations = int(v_foisonne / capa_camion) + (
        1 if v_foisonne % capa_camion > 0 else 0
    )

    st.success(f"**Volume foisonné à évacuer :** {v_foisonne:.1f} m³")
    st.info(
        f"**Nombre de rotations nécessaires :** {nb_rotations} rotations de"
        f" {capa_camion} m³"
    )

  with tab_comp:
    st.subheader("Estimation des Passes de Compactage")
    epaisseur_couche = st.number_input(
        "Épaisseur de la couche à compacter (cm)", min_value=5, value=20
    )
    object_q = st.selectbox(
        "Objectif de compactage",
        ["Q4 (Remblai courant)", "Q3 (Assise de chaussée / Tranchée sous voirie)"],
    )
    st.write(
        f"Pour une couche de **{epaisseur_couche} cm** en objectif"
        f" **{object_q}** :"
    )
    if epaisseur_couche > 30:
      st.warning(
          "⚠️ Épaisseur importante : Prévoir un compacteur lourd (V3/V4) et"
          " réaliser au moins 6 à 8 passes."
      )
    else:
      st.info(
          "Prévoir 4 à 6 passes croisées avec un compacteur de classe V2/V3."
      )

# ==========================================
# 6. CATALOGUE MATÉRIEL
# ==========================================
elif menu == "🚜 Catalogue Matériel":
  st.header("🚜 Catalogue Engins & Coûts Horaires")
  st.write("Référentiel des machines, usages et coûts internes entreprise.")

  catalog = [
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

  for item in catalog:
    with st.expander(f"⚙️ {item['nom']}"):
      st.write(f"**Usage principal :** {item['usage']}")
      cout_custom = st.number_input(
          f"Coût horaire entreprise (€/h)",
          value=float(item["cout"]),
          key=f"cost_{item['nom']}",
      )
      st.caption(
          f"Coût estimé pour une journée de 8h : {cout_custom * 8:.2f} € HT"
      )

# ==========================================
# 7. PLANS & PHOTOS (Multimodal)
# ==========================================
elif menu == "📁 Plans & Photos":
  st.header(f"📁 Analyse de Documents & Photos : {chantier_actif}")

  fichier = st.file_uploader(
      "Glisser une photo de chantier ou un PDF",
      type=["jpg", "png", "jpeg", "pdf"],
  )
  question_doc = st.text_input(
      "Question sur le document (ex: 'Vérifier la cote du tampon sur le plan')"
  )

  if st.button("Analyser avec l'IA", type="primary"):
    if fichier:
      with st.spinner("Analyse par l'IA TP en cours..."):
        res_doc = ia_engine.analyser_document_ou_photo(
            fichier.name, question_doc
        )
        data_chantier["documents"].append(
            {"nom": fichier.name, "analyse": res_doc}
        )
        st.success("Fichier analysé et sauvegardé !")
        st.markdown("### 🤖 Diagnostic de l'Expert :")
        st.markdown(res_doc)
    else:
      st.warning("Sélectionne d'abord un fichier.")

  st.divider()
  st.subheader("Documents archivés sur ce chantier")
  for doc in data_chantier["documents"]:
    with st.expander(f"📎 {doc['nom']}"):
      st.markdown(doc["analyse"])

# ==========================================
# 8. BILAN DE JOURNÉE
# ==========================================
elif menu == "🌙 Bilan de Journée":
  st.header(f"🌙 Rapport Journalier : {chantier_actif}")
  st.info("🎙️ Utile le micro de ton clavier iPhone pour tout dicter en vrac.")

  debrief = st.text_area("Compte-rendu brut de la journée", height=150)

  if st.button("Générer le rapport structuré", type="primary"):
    if debrief:
      with st.spinner("Rédaction du rapport pro..."):
        sys_rap = (
            "Tu es un chef de chantier TP. Rédige un rapport de fin de journée"
            " structuré : 1. Météo & Conditions, 2. Travaux réalisés du jour,"
            " 3. Consommation de matériaux, 4. Imprévus/Pannes, 5. Programme pour"
            " demain."
        )
        rap = ia_engine._call(sys_rap, [{"role": "user", "content": debrief}])
        data_chantier["rapports"].append(rap)
        st.success("Rapport archivé avec succès !")
        st.markdown(rap)
    else:
      st.warning("Écris ou dicte d'abord le bilan de la journée.")
