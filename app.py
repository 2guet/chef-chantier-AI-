import os
import requests
import streamlit as st

# --- CONFIGURATION DE LA PAGE PRO ---
st.set_page_config(
    page_title="Chef de Chantier TP - Pro OS",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Design industriel, sombre, lisible et ultra-pro
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; padding: 1.5rem; }
    .stButton button { width: 100%; border-radius: 6px; font-weight: 600; height: 2.8em; background-color: #2563eb; color: white; border: none; }
    .stButton button:hover { background-color: #1d4ed8; }
    .card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 15px; }
    .alert-card { background-color: #450a0a; border: 1px solid #991b1b; padding: 15px; border-radius: 8px; color: #f87171; margin-bottom: 15px; font-weight: 600; }
    .success-card { background-color: #064e3b; border: 1px solid #065f46; padding: 15px; border-radius: 8px; color: #34d399; margin-bottom: 15px; font-weight: 600; }
    h1, h2, h3 { color: #f0f6fc; }
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
        " préparation de chantier ultra-précise, technique et structurée.\n\nREGLE"
        " D'OR STRICTE : Si les informations fournies sont insuffisantes pour"
        " donner des chiffres ou des cadences exactes, écris clairement :"
        " '⚠️ Information manquante : il me manque [X] pour répondre"
        " précisément' au lieu d'inventer des hypothèses."
    )
    user_msg = (
        f"Type de travaux : {type_travaux}\nContraintes terrain :"
        f" {contraintes}\nMoyens : {moyens}"
    )
    return self._call(sys, [{"role": "user", "content": user_msg}])

  def discuter_probleme(self, historique_chat):
    sys = (
        "Tu es un conducteur de travaux TP chevronné. Tu réponds aux questions"
        " techniques du chef de chantier.\n\nRÈGLES D'OR :\n1. Donne des"
        " solutions de terrain pratiques et sécurisées.\n2. SI TU NE SAIS PAS ou"
        " si tu manques de données critiques, DIS CLAIREMENT que tu n'as pas"
        " l'information."
    )
    return self._call(sys, historique_chat)


# --- CLÉ API EN DUR ---
API_KEY = "mstrl_vMSBfYr10D2KBnRWjRLVPS0gLsspL7Yg_0q5fTA"
ia_engine = TPExpertEngine(API_KEY)

# --- INITIALISATION DE LA SESSION ---
if "chantiers" not in st.session_state:
  st.session_state.chantiers = {
      "Assistant TP (Chantier Actif)": {
          "historique_chat": [],
          "preparations": [],
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

# --- MENU LATÉRAL PRO & ÉPURÉ ---
st.sidebar.title("🏗️ CHEF DE CHANTIER OS")
st.sidebar.caption("Version Pro Terrain")

chantier_actif = st.sidebar.selectbox(
    "📍 Chantier en cours", options=list(st.session_state.chantiers.keys())
)

nouveau_c = st.sidebar.text_input(
    "➕ Ajouter un chantier", placeholder="Nom du chantier..."
)
if st.sidebar.button("Créer") and nouveau_c:
  st.session_state.chantiers[nouveau_c] = {
      "historique_chat": [],
      "preparations": [],
      "stocks": {},
  }
  st.rerun()

st.sidebar.divider()

module = st.sidebar.radio(
    "Navigation Pro",
    [
        "⚡ Tableau de Bord",
        "🛠️ Préparation & Méthodes",
        "📦 Stocks & Matériaux",
        "🧮 Calculs & Ateliers (TP / Enrobés)",
        "🚜 Parc & Matériel",
        "💬 Assistant Expert Terrain",
    ],
)

data_c = st.session_state.chantiers[chantier_actif]

# ==========================================
# 1. TABLEAU DE BORD (SYNTHÈSE DIRECTE)
# ==========================================
if module == "⚡ Tableau de Bord":
  st.title(f"⚡ Synthèse : {chantier_actif}")
  st.markdown("---")

  # Analyse des alertes stocks
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

  col1, col2, col3 = st.columns(3)
  col1.metric("Articles suivis en stock", len(data_c["stocks"]))
  col2.metric("Notes de prépa enregistrées", len(data_c["preparations"]))
  col3.metric("Engins au catalogue", len(st.session_state.catalog_engins))

# ==========================================
# 2. PRÉPARATION & MÉTHODES (IA EXPERT)
# ==========================================
elif module == "🛠️ Préparation & Méthodes":
  st.title("🛠️ Préparation de Chantier & Méthodes")
  st.caption(
      "Générez une note d'ingénierie méthodes avec validation des contraintes"
      " terrain."
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
    st.markdown("### 📚 Historique des notes de préparation")
    for p in reversed(data_c["preparations"]):
      with st.expander(f"📋 {p['titre']}"):
        st.markdown(p["contenu"])

# ==========================================
# 3. STOCKS & MATÉRIAUX (SUIVI DYNAMIQUE)
# ==========================================
elif module == "📦 Stocks & Matériaux":
  st.title("📦 Suivi des Stocks & Fournitures")
  st.caption(
      "Gestion des métrés prévisionnels, livraisons BDL et alertes automatiques"
      " chantier."
  )
  st.markdown("---")

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

  st.markdown("### 📊 État des stocks en temps réel")
  if not data_c["stocks"]:
    st.info("Aucun matériau suivi.")
  else:
    for item, vals in list(data_c["stocks"].items()):
      with st.expander(
          f"📦 {item} (Dispo : {vals['recu'] - vals['pose']} {vals['unite']})"
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

        dispo = nr - np
        reste = vals["requis"] - np
        manque = vals["requis"] - nr

        st.write(f"• Reste à poser pour finir : {reste} {vals['unite']}")
        if reste > dispo and manque > 0:
          st.error(f"⚠️ Alerte : Il manque {manque} {vals['unite']} à commander.")
        else:
          st.success("✅ Stock suffisant.")

        if c_d.button("🗑️ Supprimer", key=f"del_{item}"):
          del data_c["stocks"][item]
          st.rerun()

# ==========================================
# 4. CALCULS & ATELIERS (TERRASSEMENT & ENROBÉS)
# ==========================================
elif module == "🧮 Calculs & Ateliers (TP / Enrobés)":
  st.title("🧮 Centre de Calculs & Ateliers Métier")
  st.caption(
      "Terrassement, cubatures, rotations camions, enrobés et ateliers de"
      " fraisage."
  )
  st.markdown("---")

  mode_calc = st.selectbox(
      "Sélectionner le type de calcul",
      [
          "🚛 Terrassement & Foisonnement",
          "🛣️ Pose d'Enrobés & Tonnages",
          "⚙️ Rabotage & Fraisage",
      ],
  )
  st.markdown("---")

  if "Terrassement" in mode_calc:
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
        • Volume foisonné à évacuer : <b>{v_fois:.1f} m³</b><br>
        • Rotations de camions ({cap_c} m³) : <b>{rot} rotations</b>
        </div>""",
        unsafe_allow_html=True,
    )

  elif "Enrobés" in mode_calc:
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
        • <b>Dimensionnement d'atelier :</b> {"⚠️ Gros tonnage (>300t) : Prévoir un alimentateur + atelier de compactage renforcé (1 pneus + 1 tandem)." if tonnage > 300 else "✅ Chantier standard : 1 finisseur et 1 atelier classique suffisent."}
        </div>""",
        unsafe_allow_html=True,
    )

  else:
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
        • <b>Choix de raboteuse :</b> {"⚠️ Grande surface (>1500m²) : Prévoir une W2000 ou W2500 grand rendement." if s_rab > 1500 else "✅ Raboteuse type W1500 adaptée pour une journée de production."}
        </div>""",
        unsafe_allow_html=True,
    )

# ==========================================
# 5. PARC & MATÉRIEL
# ==========================================
elif module == "🚜 Parc & Matériel":
  st.title("🚜 Référentiel Matériel & Coûts Horaires")
  st.caption("Gestion des engins, pelles, camions et coûts internes entreprise.")
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
# 6. ASSISTANT EXPERT TERRAIN (CHAT DIRECT)
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
