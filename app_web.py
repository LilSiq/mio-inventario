import streamlit as st
import sqlite3
import pandas as pd
import base64

# --- 1. IMPOSTAZIONI DELLA PAGINA WEB ---
st.set_page_config(page_title="Il mio Inventario", page_icon="📦", layout="wide")
st.title("📦 Il mio Inventario di Casa Web (Con Foto!)")

# --- 2. CONNESSIONE AL DATABASE ---
conn = sqlite3.connect("inventario.db", check_same_thread=False)
c = conn.cursor()

# Ci assicuriamo che la tabella esista e abbia la colonna "immagine"
c.execute('''
    CREATE TABLE IF NOT EXISTS oggetti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        quantita TEXT,
        unita TEXT,
        immagine TEXT
    )
''')
conn.commit()

# --- 3. FUNZIONI DEL DATABASE ---
def aggiorna_database():
    c.execute("SELECT id, quantita, unita, nome, immagine FROM oggetti")
    return c.fetchall()

def elimina_oggetto(id_oggetto):
    c.execute("DELETE FROM oggetti WHERE id=?", (id_oggetto,))
    conn.commit()
    st.rerun()

def modifica_quantita(id_oggetto, qta_attuale, variazione):
    nuova_qta = qta_attuale + variazione
    if nuova_qta < 0: nuova_qta = 0
    c.execute("UPDATE oggetti SET quantita=? WHERE id=?", (str(nuova_qta), id_oggetto))
    conn.commit()
    st.rerun()

# --- 4. SEZIONE: AGGIUNGI OGGETTO ---
with st.expander("➕ Aggiungi un nuovo oggetto all'inventario", expanded=False):
    c.execute("SELECT DISTINCT nome FROM oggetti")
    nomi_esistenti = [row[0] for row in c.fetchall()]
    
    with st.form("form_aggiungi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_inserimento = st.radio("Che tipo di oggetto è?", ["Nuovo (mai inserito)", "Esistente (già in lista)"])
            
            if tipo_inserimento == "Esistente (già in lista)" and nomi_esistenti:
                nome = st.selectbox("Scegli dai suggerimenti:", nomi_esistenti)
            else:
                nome = st.text_input("Scrivi il nome del nuovo oggetto:")
                
        with col2:
            quantita = st.number_input("Quantità:", min_value=0, value=1, step=1)
            unita = st.selectbox("Unità di misura:", ["Pezzi", "Pacchi", "Scatole", "Paia", "Litri"])
            
            # IL NUOVO PULSANTE PER LE FOTO
            foto_caricata = st.file_uploader("Carica una foto dell'oggetto (Opzionale)", type=["png", "jpg", "jpeg"])
            
        bottone_salva = st.form_submit_button("Salva nel Database")
        
        if bottone_salva and nome:
            # Se l'utente ha caricato una foto, la trasformiamo in testo (Base64)
            img_b64 = ""
            if foto_caricata is not None:
                img_b64 = base64.b64encode(foto_caricata.read()).decode("utf-8")
                
            c.execute("INSERT INTO oggetti (nome, quantita, unita, immagine) VALUES (?, ?, ?, ?)", 
                      (nome, str(quantita), unita, img_b64))
            conn.commit()
            st.success(f"✅ {quantita} {unita} di {nome} aggiunti con successo!")
            st.rerun()

# --- 5. SEZIONE: LA LISTA DEGLI OGGETTI ---
st.write("### La tua dispensa attuale:")
oggetti = aggiorna_database()

if not oggetti:
    st.info("L'inventario è vuoto. Inizia ad aggiungere qualcosa usando il pannello qui sopra!")
else:
    col_foto, col_qta, col_nome, col_azioni = st.columns([1, 1, 3, 2])
    col_foto.write("**Foto**")
    col_qta.write("**Quantità**")
    col_nome.write("**Nome Oggetto**")
    col_azioni.write("**Azioni**")
    
    st.divider()
    
    for oggetto in oggetti:
        id_ogg = oggetto[0]
        qta = int(oggetto[1])
        unita = oggetto[2]
        nome = oggetto[3]
        img_b64 = oggetto[4] # Questa è la foto salvata
        
        c1, c2, c3, c4 = st.columns([1, 1, 3, 2])
        
        with c1:
            # Se c'è una foto salvata, la decodifichiamo e la mostriamo in piccolo
            if img_b64:
                img_bytes = base64.b64decode(img_b64)
                st.image(img_bytes, width=60)
            else:
                st.write("📷 Nessuna")
                
        with c2:
            st.write(f"**{qta}** {unita}")
        with c3:
            st.write(nome)
        with c4:
            b1, b2, b3 = st.columns(3)
            if b1.button("➕", key=f"piu_{id_ogg}"):
                modifica_quantita(id_ogg, qta, 1)
            if b2.button("➖", key=f"meno_{id_ogg}"):
                modifica_quantita(id_ogg, qta, -1)
            if b3.button("🗑️", key=f"del_{id_ogg}"):
                elimina_oggetto(id_ogg)