import streamlit as st
import requests
import pandas as pd
import time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Space Shooter Leaderboard",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- INDIRIZZO API ---
API_URL = "https://ffgame-1.onrender.com/leaderboard"

# --- STILE CSS PERSONALIZZATO (ARCADE THEME) ---
# Questo blocco trasforma l'aspetto di Streamlit per sembrara un videogioco
st.markdown("""
    <style>
    /* Sfondo Nero Totale */
    .stApp {
        background-color: #0e1117;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Titolo al neon */
    h1 {
        color: #00FF41 !important;
        text-shadow: 0 0 10px #00FF41;
        text-align: center;
        text-transform: uppercase;
        font-weight: 800;
    }

    /* Card del Punteggio */
    div.score-card {
        background-color: #1a1a1a;
        border: 2px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s;
    }
    div.score-card:hover {
        border-color: #00FF41;
        transform: scale(1.02);
    }

    /* Colori speciali per i primi 3 */
    div.rank-1 { border-color: #FFD700; box-shadow: 0 0 15px #FFD700; }
    div.rank-2 { border-color: #C0C0C0; }
    div.rank-3 { border-color: #CD7F32; }

    /* Testi */
    .player-name { font-size: 1.2rem; color: #fff; font-weight: bold; }
    .player-score { font-size: 1.5rem; color: #00FF41; font-family: monospace; font-weight: bold; }
    .rank-badge { font-size: 1.5rem; margin-right: 15px; }
    
    /* Bottone Refresh */
    .stButton button {
        width: 100%;
        background-color: #333;
        color: white;
        border: 1px solid #00FF41;
    }
    .stButton button:hover {
        background-color: #00FF41;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🏆 CLASSIFICA GENERALE 🏆")
st.markdown("<p style='text-align: center; color: #888;'>TOP 10 PILOTI DELLA GALASSIA</p>", unsafe_allow_html=True)

# --- LOGICA FETCH DATI ---
def get_data():
    try:
        # Aggiungiamo un parametro random per evitare la cache, per sicurezza
        r = requests.get(f"{API_URL}?t={int(time.time())}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Errore di connessione al Quartier Generale: {e}")
    return []

# --- INTERFACCIA ---
if st.button("🔄 AGGIORNA DATI"):
    st.rerun()

# Caricamento dati
with st.spinner("Ricezione trasmissione dati..."):
    data = get_data()

# --- VISUALIZZAZIONE ---
if not data:
    st.info("Nessun dato ricevuto o database vuoto.")
else:
    # Il server restituisce una lista di liste: [[nome, score], [nome, score]]
    # Oppure lista di dizionari. Gestiamo entrambi i casi per sicurezza.
    
    for i, entry in enumerate(data):
        rank = i + 1
        
        # Gestione formato dati (lista o dict)
        if isinstance(entry, dict):
            name = entry.get("name", "Sconosciuto")
            score = entry.get("score", 0)
        elif isinstance(entry, (list, tuple)):
            name = entry[0]
            score = entry[1]
        else:
            continue

        # Icone per i primi 3
        badge = ""
        css_class = ""
        if rank == 1:
            badge = "👑"
            css_class = "rank-1"
        elif rank == 2:
            badge = "🥈"
            css_class = "rank-2"
        elif rank == 3:
            badge = "🥉"
            css_class = "rank-3"
        else:
            badge = f"#{rank}"

        # Creiamo la CARD HTML
        html_card = f"""
        <div class="score-card {css_class}">
            <div style="display:flex; align-items:center;">
                <div class="rank-badge">{badge}</div>
                <div class="player-name">{name}</div>
            </div>
            <div class="player-score">{score}</div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #444; font-size: 0.8em;'>Powered by Python & Streamlit</div>", unsafe_allow_html=True)