import os
import requests
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Chef de Chantier TP - Pro OS",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Design "BTP Premium" : Moderne, épuré, contrasté, touches jaune chantier (#f59e0b) et acier
st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; padding: 1.5rem; }
    .stButton button { width: 100%; border-radius: 6px; font-weight: 600; height: 2.8em; background-color: #1e293b; color: white; border: none; }
    .stButton button:hover { background-color: #334155; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .alert-card { background-color: #fef2f2; border: 1px solid #fca5a5; padding: 15px; border-radius: 8px; color: #991b1b; margin-bottom: 15px; font-weight: 600; }
    .success-card { background-color: #f0fdf4; border: 1px solid #86efac; padding: 15px; border-radius: 8px; color: #166534; margin-bottom: 15px; font-weight: 600; }
    h1, h2, h3 { color: #0f172a; }
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
        " tableau structuré (Tâche, Durée, Semaine de réalisation, Impact des"
        " aléas si précisés)."
    )
    user_msg = (
        f"Descriptif / Tâches du chantier : {description_chantier}\nAléa ou"
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
# GESTION DES CHANTIERS & SÉCURITÉ (PAS DE DÉFAUT)
# ==========================================
st.sidebar.title("🏗️ CHEF DE CHANTIER OS")
st.sidebar.caption("Interface Pro Terrain")
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
          "planning_taches": [
              {
                  "tache": "Réseaux secs (AEP / EP)",
                  "duree": "3 semaines",
                  "semaine": "S1 à S3",
              },
              {
                  "tache": "Préparation pose bordures",
                  "duree": "2 semaines",
                  "semaine": "S4 à S5",
              },
              {
                  "tache": "Pose de bordures",
                  "duree": "2 semaines",
                  "semaine": "S6 à S7",
              },
              {
                  "tache": "Préparation enrobé / GNT",
                  "duree": "1 semaine",
                  "semaine": "S8",
              },
              {
                  "tache": "Pose d'enrobés",
                  "duree": "2 jours",
                  "semaine": "S9",
              },
          ],
          "compagnons": ["Thomas (Pelliste)", "Marc", "Lucas", "Kevin"],
          "ateliers": [
              {
                  "nom": "Atelier Réseaux & Terrassement",
                  "membres": ["Thomas (Pelliste)", "Marc"],
                  "tache_affectee": "Réseaux secs",
              },
              {
                  "nom": "Atelier Finitions & Pose",
                  "membres": ["Lucas", "Kevin"],
                  "tache_affectee": "Préparation & Bordures",
              },
          ],
      }
      st.rerun()
  st.title("🏗️ Bienvenue sur votre Assistant Chef de Chantier")
  st.info(
      "👈 Veuillez créer votre premier chantier dans le menu latéral pour"
      " accéder aux modules."
  )
  st.stop()

# Sélection obligatoire du chantier actif
chantier_actif = st.sidebar.selectbox(
    "📍 Sélectionner un chantier", options=liste_chantiers
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

st.sidebar.markdown("---")
module = st.sidebar.radio(
    "🧭 Navigation Principale",
    [
        "⚡ Tableau de Bord",
        "📅 Planning & Sous-Ateliers",
        "🛠️ Préparation & Méthodes",
        "📦 Stocks & Récapitulatif BDL",
        "🧮 Calculs & Ateliers Métier",
        "🚜 Parc & Matériel",
        "💬 Assistant Expert Terrain",
    ],
)

data_c = st.session_state.chantiers[chantier_actif]

# ==========================================
# 1. TABLEAU DE BORD (SYNTHÈSE & BLOC NOTES)
# ==========================================
if module == "⚡ Tableau de Bord":
  st.title(f"⚡ Tableau de Bord : {chantier_actif}")
  st.markdown("---")

  col_info1, col_info2 = st.columns(2)
  with col_info1:
    st.markdown(
        f"""<div class='card'>
        <b>📋 Résumé du Projet Épinglé :</b><br>
        {data_c.get('projet_infos', 'Aucune note injectée.')}
        </div>""",
        unsafe_allow_html=True,
    )
  with col_info2:
    st.markdown(
        f"""<div class='card'>
        <b>🛒 À commander / Pré-requis :</b><br>
        {data_c.get('achats_urgents', 'Aucun pré-requis spécifié.')}
        </div>""",
        unsafe_allow_html=True,
    )

  st.markdown("### 📝 Bloc-Notes Rapide Terrain")
  notes_actuelles = data_c.get("notes_rapides", "")
  nouveau_texte_notes = st.text_area(
      "Notes instantanées (sauvegarde automatique)",
      value=notes_actuelles,
      height=100,
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
# 2. PLANNING & SOUS-ATELIERS (NOUVEAU MODULE PRO)
# ==========================================
elif module == "📅 Planning & Sous-Ateliers":
  st.title(f"📅 Pilotage du Planning & Dispatching Équipe : {chantier_actif}")
  st.caption(
      "Gérez vos tâches, intégrez vos aléas (ex: reprise de mur) et"
      " répartissez vos compagnons par sous-ateliers."
  )
  st.markdown("---")

  # Sous-onglets professionnels pour le planning
  sub_pl1, sub_pl2, sub_pl3 = st.tabs([
      "📊 Visualisation & Aléas Planning",
      "👥 Gestion des Compagnons",
      "🛠️ Dispatching des Sous-Ateliers",
  ])

  # --- SOUS-ONGLET 1 : PLANNING & ALÉAS ---
  with sub_pl1:
    st.markdown("### 🗓️ Chronogramme des Tâches du Chantier")

    if not data_c.get("planning_taches"):
      st.info("Aucune tâche enregistrée. Ajoutez-en une ci-dessous.")
    else:
      # Affichage sous forme de tableau pro
      st.dataframe(data_c["planning_taches"], use_container_width=True)

    st.markdown("---")
    st.markdown("### ⚡ Gestion des Aléas & Réajustement Intelligent")
    st.write(
        "Un imprévu sur le terrain ? (Ex: Mur à reprendre en S3, intempéries,"
        " retard fournisseur). Décrivez l'aléa, l'IA va réajuster le planning."
    )

    col_a1, col_a2 = st.columns([3, 1])
    desc_alea = col_a1.text_input(
        "Description de l'aléa",
        placeholder="Ex: Intervention reprise de mur imprévue à la 3e semaine",
    )
    if col_a2.button("Réajuster le Planning"):
      if desc_alea:
        with st.spinner("Recalcul du planning et décalage des tâches..."):
          texte_taches = str(data_c["planning_taches"])
          res_ia_planning = ia_engine.generer_planning_ia(
              texte_taches, desc_alea
          )
          st.success("Planning réajusté avec succès !")
          st.markdown(
              f"<div class='card'>{res_ia_planning}</div>",
              unsafe_allow_html=True,
          )
      else:
        st.warning("Veuillez décrire l'aléa.")

    with st.expander("➕ Ajouter manuellement une tâche au planning"):
      c_t1, c_t2, c_t3 = st.columns([3, 2, 2])
      nt = c_t1.text_input("Nom de la tâche")
      dur = c_t2.text_input("Durée (ex: 2 semaines)")
      sem = c_t3.text_input("Période (ex: S4 à S5)")
      if st.button("Ajouter la tâche"):
        if nt:
          data_c["planning_taches"].append(
              {"tache": nt, "duree": dur, "semaine": sem}
          )
          st.success("Tâche ajoutée !")
          st.rerun()

  # --- SOUS-ONGLET 2 : COMPAGNONS ---
  with sub_pl2:
    st.markdown("### 👷 Référentiel des Compagnons sur le Chantier")
    st.write("Enregistrez les noms de vos ouvriers pour vous y retrouver.")

    col_c1, col_c2 = st.columns([3, 1])
    nouveau_comp = col_c1.text_input(
        "Nom et spécialité du compagnon",
        placeholder="Ex: Thomas (Pelliste), Marc (Chef d'équipe)...",
    )
    if col_c2.button("Ajouter l'ouvrier"):
      if nouveau_comp:
        if "compagnons" not in data_c:
          data_c["compagnons"] = []
        data_c["compagnons"].append(nouveau_comp)
        st.success(f"{nouveau_comp} ajouté à l'équipe !")
        st.rerun()

    st.markdown("### 📋 Liste de l'équipe active")
    comps = data_c.get("compagnons", [])
    if not comps:
      st.info("Aucun compagnon enregistré.")
    else:
      for idx, c in enumerate(comps):
        col_name, col_del = st.columns([4, 1])
        col_name.markdown(f"• **{c}**")
        if col_del.button("Supprimer", key=f"del_comp_{idx}"):
          comps.pop(idx)
          st.rerun()

  # --- SOUS-ONGLET 3 : SOUS-ATELIERS ---
  with sub_pl3:
    st.markdown("### 🛠️ Organisation des Sous-Ateliers de Chantier")
    st.write(
        "Divisez votre équipe en sous-ateliers (ex: Atelier Réseaux, Atelier"
        " Finitions/Bordures) et affectez les compagnons."
    )

    with st.expander("➕ Créer un nouveau sous-atelier"):
      nom_atelier = st.text_input(
          "Nom de l'atelier (ex: Atelier Pose de Bordures)"
      )
      tache_liee = st.text_input("Tâche du planning associée")
      
      comps_dispos = data_c.get("compagnons", [])
      membres_choisis = st.multiselect(
          "Sélectionner les ouvriers pour cet atelier", options=comps_dispos
      )

      if st.button("Enregistrer le sous-atelier"):
        if nom_atelier:
          if "ateliers" not in data_c:
            data_c["ateliers"] = []
          data_c["ateliers"].append({
              "nom": nom_atelier,
              "membres": membres_choisis,
              "tache_affectee": tache_liee,
          })
          st.success("Sous-atelier créé avec succès !")
          st.rerun()

    st.markdown("### 🏢 Ateliers Actifs & Dispatching des Effectifs")
    ateliers = data_c.get("ateliers", [])
    if not ateliers:
      st.info("Aucun sous-atelier configuré.")
    else:
      for idx, at in enumerate(ateliers):
        membres_str = (
            ", ".join(at["membres"]) if at["membres"] else "Aucun membre affecté"
        )
        st.markdown(
            f"""<div class='card'>
            <b>🛠️ {at['nom']}</b><br>
            • <b>Tâche liée :</b> {at['tache_affectee']}<br>
            • <b>Compagnons affectés :</b> {membres_str}
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("🗑️ Supprimer cet atelier", key=f"del_at_{idx}"):
          ateliers.pop(idx)
          st.rerun()

# ==========================================
# 3. PRÉPARATION & MÉTHODES
# ==========================================
elif module == "🛠️ Préparation & Méthodes":
  st.title("🛠️ Préparation de Chantier & Méthodes")
  st.caption(
      "Générez une note d'ingénierie et injectez-la directement sur le tableau"
      " de bord."
  )
  st.markdown("---")

  col_p1, col_p2 = st.columns(2)
  with col_p1:
    type_t = st.text_input(
        "Type de travaux", placeholder="Ex: Pose de 400m de réseau EU en Ø300"
    )
    contraintes_t = st.text_area(
        "Contraintes (Sol, eau, circulation, réseaux)",
        placeholder="Ex: Présence nappe phréatique à 1m50, sol argileux",
    )
  with col_p2:
    moyens_t = st.text_area(
        "Moyens disponibles", placeholder="Ex: Pelle 18t, blindage de tranchée"
    )

  if st.button("Lancer l'analyse technique IA"):
    if type_t:
      with st.spinner("Analyse par l'expert méthodes en cours..."):
        res = ia_engine.preparer_chantier(type_t, contraintes_t, moyens_t)
        data_c["preparations"].append({"titre": type_t, "contenu": res})
        st.success("Note enregistrée dans l'historique.")
        st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)
    else:
      st.warning("Veuillez renseigner le type de travaux.")

  if data_c["preparations"]:
    st.markdown("### 📚 Historique & Validation pour le Tableau de Bord")
    for idx, p in enumerate(reversed(data_c["preparations"])):
      with st.expander(f"📋 {p['titre']}"):
        st.markdown(p["contenu"])
        if st.button(
            "📌 Épingler ce projet sur le Tableau de Bord",
            key=f"ping_{idx}",
        ):
          data_c["projet_infos"] = (
              f"<b>Projet :</b> {p['titre']}<br><b>Analyse validée par"
              " l'IA</b>"
          )
          data_c["achats_urgents"] = (
              "Vérifier les pré-requis listés dans la note de préparation"
              f" '{p['titre']}'."
          )
          st.success("✅ Projet épinglé avec succès sur votre Tableau de Bord !")

# ==========================================
# 4. STOCKS & TABLEAU RÉCAPITULATIF BDL
# ==========================================
elif module == "📦 Stocks & Récapitulatif BDL":
  st.title("📦 Suivi des Stocks & Tableaux Récapitulatifs")
  st.caption(
      "Visualisez en un clin d'œil l'état complet du chantier (métrés plans,"
      " reçus BDL, stock terrain et restes à commander)."
  )
  st.markdown("---")

  sub_s1, sub_s2 = st.tabs(
      ["📊 Tableau Récapitulatif Global", "⚙️ Gestion & Saisie BDL"]
  )

  with sub_s1:
    st.markdown("### 📋 Tableau de Bord des Matériaux")
    if not data_c["stocks"]:
      st.info(
          "Aucun matériau enregistré. Ajoutez-en via l'onglet de gestion."
      )
    else:
      tableau_data = []
      for item, vals in data_c["stocks"].items():
        dispo = vals["recu"] - vals["pose"]
        reste = vals["requis"] - vals["pose"]
        manque = max(0, vals["requis"] - vals["recu"])
        tableau_data.append({
            "Matériau": item,
            "Prévu Plan": f"{vals['requis']} {vals['unite']}",
            "Reçu BDL": f"{vals['recu']} {vals['unite']}",
            "Posé / Consommé": f"{vals['pose']} {vals['unite']}",
            "Stock Terrain Dispo": f"{dispo} {vals['unite']}",
            "À Commander d'Urgence": f"{manque} {vals['unite']}",
        })
      st.dataframe(tableau_data, use_container_width=True)

  with sub_s2:
    with st.expander("➕ Ajouter un matériau au suivi chantier"):
      c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
      n_mat = c1.text_input("Désignation (Ex: Regard béton)")
      req_m = c2.number_input("Métré plan", min_value=0.0, value=50.0)
      rec_m = c3.number_input("Reçu BDL", min_value=0.0, value=0.0)
      uni_m = c4.selectbox("Unité", ["mL", "m3", "Tonnes", "Unités", "m2"])
      if st.button("Enregistrer"):
        if n_mat:
          data_c["stocks"][n_mat] = {
              "requis": req_m,
              "recu": rec_m,
              "pose": 0.0,
              "unite": uni_m,
          }
          st.success("Ajouté avec succès.")
          st.rerun()

    st.markdown("### ✏️ Mises à jour journalières")
    for item, vals in list(data_c["stocks"].items()):
      with st.expander(
          f"📦 {item} (Dispo terrain : {vals['recu'] - vals['pose']}"
          f" {vals['unite']})"
      ):
        c_r, c_p, c_d = st.columns([2, 2, 1])
        nr = c_r.number_input(
            "Reçu cumulé", value=float(vals["recu"]), key=f"r_{item}"
        )
        np = c_p.number_input(
            "Posé / Consommé", value=float(vals["pose"]), key=f"p_{item}"
        )
        data_c["stocks"][item]["recu"] = nr
        data_c["stocks"][item]["pose"] = np

        if c_d.button("🗑️ Supprimer", key=f"del_{item}"):
          del data_c["stocks"][item]
          st.rerun()

# ==========================================
# 5. CALCULS & ATELIERS (AVEC GRAPHIQUES)
# ==========================================
elif module == "🧮 Calculs & Ateliers Métier":
  st.title("🧮 Centre de Calculs & Graphiques Métier")
  st.caption("Terrassement, enrobés, rabotage avec visualisation graphique.")
  st.markdown("---")

  sub_c1, sub_c2, sub_c3 = st.tabs(
      [
          "🚛 Terrassement & Cubatures",
          "🛣️ Enrobés & Tonnages",
          "⚙️ Rabotage & Fraisage",
      ]
  )

  with sub_c1:
    c1, c2 = st.columns(2)
    v_pl = c1.number_input("Volume en place (m³)", min_value=1.0, value=200.0)
    sol_t = c2.selectbox(
        "Nature du sol",
        [
            "Terre végétale (Foisonnement 20%)",
            "Argile / Marne (Foisonnement 30%)",
            "Grave / Sable (Foisonnement 15%)",
            "Rocher abattu (Foisonnement 50%)",
        ],
    )
    coeffs = {
        "Terre végétale (Foisonnement 20%)": 1.20,
        "Argile / Marne (Foisonnement 30%)": 1.30,
        "Grave / Sable (Foisonnement 15%)": 1.15,
        "Rocher abattu (Foisonnement 50%)": 1.50,
    }
    v_fois = v_pl * coeffs[sol_t]
    cap_c = st.number_input(
        "Capacité utile benne camion (m³)", min_value=1.0, value=12.0
    )
    rot = int(v_fois / cap_c) + (1 if v_fois % cap_c > 0 else 0)

    st.markdown(
        f"""<div class='card'>
        <b>Résultats Terrassement :</b><br>
        • Volume en place : <b>{v_pl} m³</b><br>
        • Volume foisonné à évacuer : <b>{v_fois:.1f} m³</b><br>
        • Rotations de camions ({cap_c} m³) : <b>{rot} rotations</b>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("### 📊 Répartition Visuelle des Volumes")
    st.bar_chart({"Volume (m3)": {"En Place": v_pl, "Foisonné": v_fois}})

  with sub_c2:
    c1, c2 = st.columns(2)
    surf = c1.number_input("Surface du chantier (m²)", min_value=10.0, value=1500.0)
    ep = c2.number_input("Épaisseur moyenne (cm)", min_value=1.0, value=6.0)
    dens = st.selectbox(
        "Type d'enrobé",
        [
            "BBSG / Enrobé standard (Densité 2.40)",
            "BBME / Module élevé (Densité 2.45)",
            "BBTM / Très mince (Densité 2.35)",
        ],
    )
    d_val = 2.40 if "2.40" in dens else (2.45 if "2.45" in dens else 2.35)
    tonnage = surf * (ep / 100.0) * d_val
    nb_semis = int(tonnage / 25.0) + (1 if tonnage % 25.0 > 0 else 0)

    st.markdown(
        f"""<div class='card'>
        <b>Résultats Enrobés :</b><br>
        • Tonnage total estimé : <b>{tonnage:.1f} Tonnes</b><br>
        • Semi-remorques (25t) nécessaires : <b>{nb_semis} camions</b><br>
        • <b>Dimensionnement d'atelier :</b> {"⚠️ Gros tonnage (>300t) : Prévoir un alimentateur + compactage renforcé." if tonnage > 300 else "✅ Chantier standard : 1 finisseur + atelier classique."}
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("### 📊 Analyse Tonnage & Logistique Camions")
    st.bar_chart({
        "Tonnage / Camions": {
            "Tonnage Total (t)": tonnage,
            "Nombre Camions (x25t)": nb_semis,
        }
    })

  with sub_c3:
    c1, c2 = st.columns(2)
    s_rab = c1.number_input("Surface à raboter (m²)", min_value=10.0, value=1000.0)
    p_rab = c2.number_input(
        "Profondeur de fraisage (cm)", min_value=1.0, value=5.0
    )
    v_fr = s_rab * (p_rab / 100.0)
    p_fr = v_fr * 2.1

    st.markdown(
        f"""<div class='card'>
        <b>Résultats Rabotage :</b><br>
        • Volume de fraiseat : <b>{v_fr:.1f} m³</b><br>
        • Poids total des déblais : <b>{p_fr:.1f} Tonnes</b><br>
        • <b>Choix de raboteuse :</b> {"⚠️ Grande surface (>1500m²) : Prévoir une W2000 ou W2500." if s_rab > 1500 else "✅ Raboteuse type W1500 adaptée."}
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("### 📊 Volume & Poids du Fraiseat")
    st.bar_chart({"Fraisage": {"Volume (m3)": v_fr, "Poids (Tonnes)": p_fr}})

# ==========================================
# 6. PARC & MATÉRIEL
# ==========================================
elif module == "🚜 Parc & Matériel":
  st.title("🚜 Référentiel Matériel & Coûts Horaires")
  st.caption("Gestion des engins et coûts internes entreprise.")
  st.markdown("---")

  with st.expander("➕ Ajouter un engin au catalogue"):
    n_e = st.text_input("Nom de la machine")
    u_e = st.text_input("Usage principal")
    c_e = st.number_input("Coût horaire (€/h)", min_value=0.0, value=65.0)
    if st.button("Ajouter l'engin"):
      if n_e:
        st.session_state.catalog_engins.append(
            {"nom": n_e, "usage": u_e, "cout": c_e}
        )
        st.success("Enregistré.")
        st.rerun()

  st.markdown("### ⚙️ Liste des machines actives")
  for idx, engin in enumerate(st.session_state.catalog_engins):
    with st.expander(f"⚙️ {engin['nom']} ({engin['cout']} €/h)"):
      st.write(f"**Usage :** {engin['usage']}")
      if st.button("🗑️ Supprimer", key=f"del_eng_{idx}"):
        st.session_state.catalog_engins.pop(idx)
        st.rerun()

# ==========================================
# 7. ASSISTANT EXPERT TERRAIN
# ==========================================
elif module == "💬 Assistant Expert Terrain":
  st.title("💬 Assistant Expert Terrain")
  st.caption(
      "Posez vos questions techniques en direct. L'IA applique des consignes"
      " strictes de prudence et d'exactitude."
  )
  st.markdown("---")

  for m in data_c["historique_chat"]:
    with st.chat_message(m["role"]):
      st.markdown(m["content"])

  user_q = st.chat_input("Ex: Fond de fouille argileux détrempé, on fait quoi ?")
  if user_q:
    data_c["historique_chat"].append({"role": "user", "content": user_q})
    with st.chat_message("user"):
      st.markdown(user_q)

    with st.chat_message("assistant"):
      with st.spinner("Analyse technique en cours..."):
        rep = ia_engine.discuter_probleme(data_c["historique_chat"])
        st.markdown(rep)
        data_c["historique_chat"].append({"role": "assistant", "content": rep})
