import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import base64

# --- 1. CONNESSIONE SUPABASE (MODIFICA QUI!) ---
# Incolla qui la stringa che hai copiato (quella col Transaction Pooler)
# Ricordati di mettere la tua password al posto di [YOUR-PASSWORD]
DB_URL = "postgresql://postgres.ghiozicwizhjhplheyva:[Invsicuro26]@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DB_URL)

def esegui_query(query, params=None, commit=False):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        if commit:
            conn.commit()
        return result

# Creazione automatica della tabella nel Cloud
esegui_query('''
    CREATE TABLE IF NOT EXISTS oggetti (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        quantita TEXT,
        unita TEXT,
        immagine TEXT
    )
''', commit=True)

# --- 2. IMPOSTAZIONI PAGINA ---
st.set_page_config(page_title="Inventario Cloud", page_icon="📦", layout="wide")
st.title("📦 Il mio Inventario Cloud Immortale")

# --- 3. FUNZIONI ---
def aggiorna_database():
    res = esegui_query("SELECT id, quantita, unita, nome, immagine FROM oggetti ORDER BY nome ASC")
    return res.fetchall()

def elimina_oggetto(id_oggetto):
    esegui_query("DELETE FROM oggetti WHERE id=:id", {"id": id_oggetto}, commit=True)
    st.rerun()

def modifica_quantita(id_oggetto, qta_attuale, variazione):
    nuova_qta = max(0, int(qta_attuale) + variazione)
    esegui_query("UPDATE oggetti SET quantita=:qta WHERE id=:id", {"qta": str(nuova_qta), "id": id_oggetto}, commit=True)
    st.rerun()

# --- 4. SEZIONE AGGIUNGI ---
with st.expander("➕ Aggiungi / Aggiorna Oggetto", expanded=False):
    res_nomi = esegui_query("SELECT DISTINCT nome FROM oggetti")
    nomi_esistenti = [row[0] for row in res_nomi.fetchall()]
    
    with st.form("form_aggiungi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.radio("Tipo oggetto:", ["Nuovo", "Esistente"])
            if tipo == "Esistente" and nomi_esistenti:
                nome = st.selectbox("Scegli oggetto:", nomi_esistenti)
            else:
                nome = st.text_input("Nome nuovo oggetto:")
        with col2:
            quantita = st.number_input("Quantità:", min_value=0, value=1)
            unita = st.selectbox("Unità:", ["Pezzi", "Pacchi", "Scatole", "Paia", "Litri"])
            foto = st.file_uploader("Carica foto:", type=["png", "jpg", "jpeg"])
            
        if st.form_submit_button("Salva nel Cloud"):
            img_b64 = ""
            if foto:
                img_b64 = base64.b64encode(foto.read()).decode("utf-8")
            
            esegui_query("INSERT INTO oggetti (nome, quantita, unita, immagine) VALUES (:n, :q, :u, :i)", 
                         {"n": nome, "q": str(quantita), "u": unita, "i": img_b64}, commit=True)
            st.success("Dati salvati per sempre!")
            st.rerun()

# --- 5. LISTA OGGETTI ---
oggetti = aggiorna_database()
if not oggetti:
    st.info("L'inventario è vuoto.")
else:
    c_img, c_qta, c_nome, c_azz = st.columns([1, 1, 3, 2])
    c_img.write("**Foto**")
    c_qta.write("**Q.tà**")
    c_nome.write("**Nome**")
    c_azz.write("**Azioni**")
    st.divider()

    for o in oggetti:
        id_o, qta, uni, nom, img = o
        col_img, col_qta, col_nom, col_btn = st.columns([1, 1, 3, 2])
        
        with col_img:
            if img:
                img_b = base64.b64decode(img)
                st.image(img_b, width=50)
                with st.popover("🔍"):
                    st.image(img_b, use_container_width=True)
            else:
                st.write("📷 No")
        
        col_qta.write(f"**{qta}** {uni}")
        col_nom.write(nom)
        
        with col_btn:
            b1, b2, b3 = st.columns(3)
            if b1.button("➕", key=f"p{id_o}"): modifica_quantita(id_o, qta, 1)
            if b2.button("➖", key=f"m{id_o}"): modifica_quantita(id_o, qta, -1)
            if b3.button("🗑️", key=f"d{id_o}"): elimina_oggetto(id_o)