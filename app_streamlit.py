import streamlit as st
import time

# Configuration de la page Streamlit
st.set_page_config(page_title="Démo Client-Serveur", page_icon="🖥️", layout="centered")

st.title("🖥️ Démo Client-Serveur & Gestion Mémoire")
st.write("Interface interactive de démonstration pour le projet Python.")

# Section d'état de la mémoire / serveur
st.subheader("1. État du Serveur")
if "server_active" not in st.session_state:
    st.session_state.server_active = False

col1, col2 = st.columns(2)
with col1:
    if st.button("Démarrer le Serveur"):
        st.session_state.server_active = True
with col2:
    if st.button("Arrêter le Serveur"):
        st.session_state.server_active = False

if st.session_state.server_active:
    st.success("Statut : Serveur en ligne — Écoute sur la mémoire partagée.")
else:
    st.error("Statut : Serveur hors ligne.")

# Section interaction Client
st.subheader("2. Envoi de requête Client")
message = st.text_input("Message à envoyer au serveur :", placeholder="Ex: GET_MEMORY_STATUS")

if st.button("Envoyer la requête"):
    if not st.session_state.server_active:
        st.warning("Impossible d'envoyer : Le serveur est hors ligne.")
    elif not message:
        st.warning("Veuillez saisir un message.")
    else:
        with st.spinner("Transmission au serveur..."):
            time.sleep(0.8) # Simulation du délai réseau/mémoire
        st.info(f"**Client** -> Réponse reçue du serveur pour : *'{message}'*")
        st.json({
            "status": 200,
            "payload_received": message,
            "memory_address": "0x7ffeefbff5c0",
            "bytes_processed": len(message)
        })
