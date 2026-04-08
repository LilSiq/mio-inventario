import streamlit as st
import sqlite3
import pandas as pd

# --- 1. IMPOSTAZIONI DELLA PAGINA WEB ---
st.set_page_config(page_title="Il mio Inventario", page_icon="📦", layout="wide")
st.title("📦 Il mio Inventario di Casa Web")

# --- 2. CONNESSIONE AL DATABASE ---
# Usiamo lo stesso database di prima, così non perdi i dati!
conn = sqlite3.connect("inventario.db", check_same_thread=False)
c = conn.cursor()

# --- 3. FUNZIONI DEL DATABASE ---
def aggiorna_database():
    c.execute("SELECT id, quantita, unita, nome FROM oggetti")
    return c.fetchall()

def elimina_oggetto(id_oggetto):
    c.execute("DELETE FROM oggetti WHERE id=?", (id_oggetto,))
    conn.commit()
    st.rerun() # Ricarica la pagina web

def modifica_quantita(id_oggetto, qta_attuale, variazione):
    nuova_qta = qta_attuale + variazione
    if nuova_qta < 0: nuova_qta = 0
    c.execute("UPDATE oggetti SET quantita=? WHERE id=?", (str(nuova_qta), id_oggetto))
    conn.commit()
    st.rerun()

# --- 4. SEZIONE: AGGIUNGI OGGETTO (Con Suggerimenti!) ---
with st.expander("➕ Aggiungi un nuovo oggetto all'inventario", expanded=False):
    # Cerchiamo tutti i nomi già presenti nel database per i suggerimenti
    c.execute("SELECT DISTINCT nome FROM oggetti")
    nomi_esistenti = [row[0] for row in c.fetchall()]
    
    with st.form("form_aggiungi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # IL SISTEMA DI SUGGERIMENTO
            tipo_inserimento = st.radio("Che tipo di oggetto è?", ["Nuovo (mai inserito)", "Esistente (già in lista)"])
            
            if tipo_inserimento == "Esistente (già in lista)" and nomi_esistenti:
                nome = st.selectbox("Scegli dai suggerimenti:", nomi_esistenti)
            else:
                nome = st.text_input("Scrivi il nome del nuovo oggetto:")
                
        with col2:
            quantita = st.number_input("Quantità:", min_value=0, value=1, step=1)
            unita = st.selectbox("Unità di misura:", ["Pezzi", "Pacchi", "Scatole", "Paia", "Litri"])
            
        bottone_salva = st.form_submit_button("Salva nel Database")
        
        if bottone_salva and nome:
            c.execute("INSERT INTO oggetti (nome, quantita, unita, immagine) VALUES (?, ?, ?, ?)", 
                      (nome, str(quantita), unita, ""))
            conn.commit()
            st.success(f"✅ {quantita} {unita} di {nome} aggiunti con successo!")
            st.rerun()

# --- 5. SEZIONE: LA LISTA DEGLI OGGETTI ---
st.write("### La tua dispensa attuale:")
oggetti = aggiorna_database()

if not oggetti:
    st.info("L'inventario è vuoto. Inizia ad aggiungere qualcosa usando il pannello qui sopra!")
else:
    # Creiamo le colonne per impaginare bene i dati come in un vero sito
    col_qta, col_nome, col_azioni = st.columns([1, 3, 2])
    col_qta.write("**Quantità**")
    col_nome.write("**Nome Oggetto**")
    col_azioni.write("**Azioni**")
    
    st.divider() # Linea di separazione
    
    for oggetto in oggetti:
        id_ogg = oggetto[0]
        qta = int(oggetto[1])
        unita = oggetto[2]
        nome = oggetto[3]
        
        c1, c2, c3 = st.columns([1, 3, 2])
        
        with c1:
            st.write(f"**{qta}** {unita}")
        with c2:
            st.write(nome)
        with c3:
            # Creiamo i bottoncini + , - e Elimina in orizzontale
            b1, b2, b3 = st.columns(3)
            if b1.button("➕", key=f"piu_{id_ogg}"):
                modifica_quantita(id_ogg, qta, 1)
            if b2.button("➖", key=f"meno_{id_ogg}"):
                modifica_quantita(id_ogg, qta, -1)
            if b3.button("🗑️", key=f"del_{id_ogg}"):
                elimina_oggetto(id_ogg)