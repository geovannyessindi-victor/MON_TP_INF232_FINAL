import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Configuration et Style Dark Mode
st.set_page_config(page_title="Santé Privée - INF232", page_icon="🩺")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #2c3e50 100%);
        background-attachment: fixed;
    }
    h1, h2, h3, p, label { color: #ffffff !important; }
    [data-testid="stSidebar"] { background-color: rgba(30, 30, 30, 0.8); }
    </style>
    """, unsafe_allow_html=True)

# 2. Base de données
def init_db():
    conn = sqlite3.connect('sante_finale.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (nom TEXT, prenom TEXT, age INTEGER, maladie TEXT, tension INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# 3. SIDEBAR (Saisie + Accès Sécurisé)
with st.sidebar:
    st.header(" ACCÈS MÉDICAL")
    code_secret = st.text_input("Code Docteur (Secret)", type="password")
    acces_autorise = (code_secret == "1234") 

    st.divider()
    st.header(" ENREGISTREMENT")
    with st.form("form_patient", clear_on_submit=True):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        age = st.number_input("Âge", 0, 120, 25)
        tension = st.number_input("Tension (mmHg)", 40, 250, 120)
        liste_maladies = ["Aucune (RAS)", "Paludisme", "Diabète", "Hypertension", "Grippe", "Toux", "Autre..."]
        maladie_choisie = st.selectbox("Maladie", liste_maladies)
        envoyer = st.form_submit_button("Enregistrer")

    if envoyer and nom:
        conn = sqlite3.connect('sante_finale.db')
        conn.execute('INSERT INTO patients VALUES (?,?,?,?,?)', (nom, prenom, age, maladie_choisie, tension))
        conn.commit()
        conn.close()
        st.success("Données enregistrées !")
        st.rerun()

# 4. AFFICHAGE ET SECRET MÉDICAL
st.title("📲 GESTION ET ANALYSE DES PATIENTS")

conn = sqlite3.connect('sante_finale.db')
df = pd.read_sql_query('SELECT * FROM patients', conn)
conn.close()

if not df.empty:
    # Diagnostic de tension (visible)
    df['État Tension'] = df['tension'].apply(lambda t: " Normale" if t < 140 else " Élevée")

    st.subheader(" Registre des Consultations")
    df_affichage = df.copy()
    if not acces_autorise:
        df_affichage['maladie'] = " CONFIDENTIEL"
        st.info(" Mode Public : Les diagnostics sont masqués par le secret médical.")
    else:
        st.warning(" Mode Docteur : Accès aux diagnostics autorisé.")

    st.dataframe(df_affichage, use_container_width=True)

    # --- ANALYSES STATISTIQUES ---
    if len(df) >= 2:
        st.divider()
        st.subheader(" Analyses Descriptives et Régression")
        
        # Métriques
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Moyenne Tension", f"{df['tension'].mean():.1f}")
        col_m2.metric("Âge Moyen", f"{df['age'].mean():.1f}")
        correlation = df['age'].corr(df['tension'])
        col_m3.metric("Corrélation", f"{correlation:.2f}")

        # Graphiques
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("**Distribution (Histogramme)**")
            fig1, ax1 = plt.subplots()
            fig1.patch.set_facecolor('#2c3e50')
            ax1.set_facecolor('#2c3e50')
            sns.histplot(df['tension'], kde=True, ax=ax1, color="cyan")
            ax1.tick_params(colors='white')
            st.pyplot(fig1)
            
        with g2:
            st.write("**Régression (Âge / Tension)**")
            fig2, ax2 = plt.subplots()
            fig2.patch.set_facecolor('#2c3e50')
            ax2.set_facecolor('#2c3e50')
            sns.regplot(x=df['age'], y=df['tension'], ax=ax2, color="orange", line_kws={"color": "red"})
            ax2.tick_params(colors='white')
            st.pyplot(fig2)

        # Explication mathématique
        pente, inter = np.polyfit(df['age'], df['tension'], 1)
        st.write("###  Analyse de la Régression")
        st.latex(f"y = {pente:.2f}x + {inter:.2f}")
        st.info(f"Interprétation : La tension augmente de {pente:.2f} mmHg par année d'âge.")
else:
    st.info("La base est vide. Enregistrez des patients pour voir les graphiques.")

# --- FOOTER ---
st.markdown(f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(0,0,0,0.8); text-align: center; padding: 8px;">
        <p style="margin:0; color: white; font-size: 14px;">
            Développé par <b>GEOVANNY ESSINDI VICTOR</b> | TP INF232 - 2026 🔒
        </p>
    </div>
    """, unsafe_allow_html=True)
