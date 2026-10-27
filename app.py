import os
import requests
import streamlit as st

st.set_page_config(
    page_title="Chef de Chantier AI",
    page_icon="🏗️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- MOTEUR IA INTÉGRÉ DIRECTEMENT ---
class UltimateTPAgent:

  def __init__(self, api_key):
    self.api_key = api_key
    self.api_url = "https://api.mistral.ai/v1/chat/completions"

  def _call(self, system_prompt, user_msg):
    if not self.api_key or self.api_key == "METS_TA_CLE_MISTRAL_ICI":
      return "⚠️ Erreur : Clé API Mistral non configurée."

    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.3,
    }
    try:
      res = requests.post(
          self.api_url, headers=headers, json=payload, timeout=30
      )
      if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
      return f"Erreur API ({res.status_code}): {res.text}"
    except Exception as e:
      return f"Erreur réseau : {str(e)}"

  def simuler_atelier(self, ressources, tache):
    sys = (
        "Tu es un ingénieur méthodes et conducteur de travaux TP chevronné."
        " Analyse les ressources et la tâche pour fournir : 1. Les cadences et"
        " rendements journaliers prévisionnels. 2. Le dimensionnement exact de"
        " l'atelier. 3. Les points de vigilance technique, coactivité et"
        " sécurité."
    )
    return self._call(sys, f"Ressources : {ressources}\nTâche : {tache}")

  def structurer_rapport(self, brut):
    sys = (
        "Tu es un assistant de gestion de chantier TP. Rédige un rapport de fin"
        " de journée professionnel structuré ainsi : 1. Météo & Conditions, 2."
        " Avancement réel vs prévisionnel, 3. Aléas ou pannes, 4. Reste à faire."
    )
    return self._call(sys, brut)

  def analyser_document_ou_photo(self, nom_fichier, description_contexte):
    sys = (
        "Tu es un expert technique en travaux publics. Analyse ce document ou"
        " cette photo transmise sur le chantier, identifie les éléments clés"
        " (risques, cotes, contraintes techniques, observations) et fais un"
        " résumé pro pour le chef de chantier."
    )
    return self._call(
        sys,
        f"Fichier joint : {nom_fichier}\nContexte/Notes du chef de chantier"
        f" : {description_contexte}",
    )


# Récupération de la clé API (via les secrets Streamlit ou variable d'env)
API_KEY = os.getenv("MISTRAL_API_KEY", "METS_TA_CLE_MISTRAL_ICI")
ai = UltimateTPAgent(API_KEY)

st.title("🏗️ Chef de Chantier AI")

if "chantiers" not in st.session_state:
  st.session_state.chantiers = {
      "Terrassement ZAC Sud": {"historique": [], "documents": []},
  }

c1, c2 = st.columns([2, 1])
with c1:
  chantier_actif = st.selectbox(
      "📍 Chantier actif", options=list(st.session_state.chantiers.keys())
  )
with c2:
  nouveau = st.text_input("Nouveau", placeholder="Nom chantier...")
  if st.button("Créer") and nouveau:
    st.session_state.chantiers[nouveau] = {"historique": [], "documents": []}
    st.rerun()

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["🚀 Prévisionnel", "🌙 Bilan du Soir", "📁 Plans & Photos", "📚 Archives"]
)

with tab1:
  st.subheader("Préparation & Rendements")
  ressources = st.text_area(
      "Moyens (Ex: 1 pelle 15t, 2 camions 8x4, 3 ouvriers)", height=80
  )
  tache = st.text_area("Tâche du jour (Ex: Fouille en tranchée EU)", height=80)

  if st.button("Lancer l'analyse technique", type="primary"):
    if ressources and tache:
      with st.spinner("Analyse en cours..."):
        st.markdown(ai.simuler_atelier(ressources, tache))
    else:
      st.warning("Remplis les ressources et la tâche.")

with tab2:
  st.subheader("Rapport journalier")
  st.info(
      "🎙️ Utilise le micro de ton clavier iPhone pour dicter ton débrief ici."
  )
  brut = st.text_area("Raconte ta journée (réalisé, pannes, aléas...)", height=150)

  if st.button("Générer le rapport pro & Archiver", type="primary"):
    if brut:
      with st.spinner("Mise en forme..."):
        rapport = ai.structurer_rapport(brut)
        st.session_state.chantiers[chantier_actif]["historique"].append(rapport)
        st.success("Rapport archivé avec succès !")
        st.markdown(rapport)
    else:
      st.warning("Le compte-rendu est vide.")

with tab3:
  st.subheader(f"📸 / 📄 Stockage & Analyse - {chantier_actif}")
  st.write(
      "Envoie une photo de chantier ou un PDF (plan, CCTP, rapport G2). Il"
      " sera rattaché **uniquement** à ce chantier."
  )

  fichier_charge = st.file_uploader(
      "Importer une photo ou un PDF", type=["jpg", "png", "jpeg", "pdf"]
  )
  commentaire_doc = st.text_input(
      "Notes ou question sur ce document (ex: 'Regarder la cote de radier...')"
  )

  if st.button("Analyser et ranger dans ce chantier", type="primary"):
    if fichier_charge:
      with st.spinner(
          f"Analyse du fichier pour le chantier '{chantier_actif}'..."
      ):
        analyse_resultat = ai.analyser_document_ou_photo(
            fichier_charge.name, commentaire_doc
        )
        doc_item = {
            "nom": fichier_charge.name,
            "type": fichier_charge.type,
            "analyse": analyse_resultat,
        }
        st.session_state.chantiers[chantier_actif]["documents"].append(doc_item)
        st.success(
            f"Fichier '{fichier_charge.name}' analysé et stocké dans le"
            f" chantier {chantier_actif} !"
        )
        st.markdown("### 🤖 Diagnostic de l'IA :")
        st.markdown(analyse_resultat)
    else:
      st.warning("Sélectionne d'abord une photo ou un PDF.")

  st.divider()
  st.markdown("### Documents et photos déjà stockés pour ce chantier :")
  docs_chantier = st.session_state.chantiers[chantier_actif]["documents"]
  if not docs_chantier:
    st.write("Aucun document pour l'instant.")
  else:
    for idx, d in enumerate(docs_chantier, 1):
      with st.expander(f"📎 {d['nom']}"):
        st.markdown(d["analyse"])

with tab4:
  st.subheader(f"📚 Historique global : {chantier_actif}")
  historique = st.session_state.chantiers[chantier_actif]["historique"]
  docs_chantier = st.session_state.chantiers[chantier_actif]["documents"]

  if not historique and not docs_chantier:
    st.write("Rien pour l'instant sur ce chantier.")
  else:
    st.markdown("#### 📄 Rapports journaliers :")
    for i, rap in enumerate(reversed(historique), 1):
      with st.expander(f"Rapport #{len(historique) - i + 1}"):
        st.markdown(rap)
