import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Configuration et Style
st.set_page_config(page_title="TP INF232 - Santé", page_icon="🩺")

# Injection de CSS pour un fond Noir et Gris (Dark Mode Pro)
st.markdown("""
    <style>
    /* Fond principal : dégradé noir vers gris foncé */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #2c3e50 100%);
        background-attachment: fixed;
    }
    
    /* Rendre le texte principal blanc pour la lisibilité */
    h1, h2, h3, p, label, .stMarkdown {
        color: #ffffff !important;
    }

    /* Style de la barre latérale (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: rgba(30, 30, 30, 0.8);
    }
    
    /* Ajustement des widgets pour le mode sombre */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1e1e1e;
        color: white;
    }
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

# 3. INTERFACE DE DÉPART
st.title("📲 APPLICATION DE COLLECTE ET D'ANALYSE")

with st.sidebar:
    st.header("ENREGISTREMENT")
    with st.form("form_patient", clear_on_submit=True):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        age = st.number_input("Âge", min_value=0, max_value=120, value=25)
        tension = st.number_input("Tension (mmHg)", min_value=40, max_value=250, value=120)
        
        liste_maladies = [
            "Aucune (RAS)", "Diarrhée", "Diabète Type 1", "Diabète Type 2", 
            "Paludisme", "Drépanocytose", "Asthme", "Obésité", 
            "Insuffisance Rénale", "Toux", "Grippe", "Autre..."
        ]
        maladie_sel = st.selectbox("Sélectionner la Maladie", liste_maladies)
        
        maladie_finale = maladie_sel
        if maladie_sel == "Autre...":
            maladie_precision = st.text_input("Précisez la maladie")
            maladie_finale = maladie_precision if maladie_precision else "Autre"
            
        envoyer = st.form_submit_button("Enregistrer le Patient")

    if envoyer:
        if nom and prenom:
            conn = sqlite3.connect('sante_finale.db')
            conn.execute('INSERT INTO patients VALUES (?,?,?,?,?)', (nom, prenom, age, maladie_finale, tension))
            conn.commit()
            conn.close()
            st.success(f"Patient {prenom} ajouté !")
            st.rerun()
        else:
            st.error("Veuillez remplir le nom et le prénom.")

    st.divider()
    if st.button("📴 SORTIR"):
        st.warning("Session terminée.")
        st.stop()

# 4. AFFICHAGE ET ANALYSE
conn = sqlite3.connect('sante_finale.db')
df = pd.read_sql_query('SELECT * FROM patients', conn)
conn.close()

if not df.empty:
    # Diagnostic automatique
    def verifier_tension(t):
        return "Normale" if t < 140 else "Élevée (Attention)"
    
    df['État Tension'] = df['tension'].apply(verifier_tension)

    st.subheader("LISTE DES PATIENTS")
    # Affichage du tableau (le mode sombre de Streamlit l'adaptera automatiquement)
    st.dataframe(df, use_container_width=True)
    
    # Export CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger le registre (CSV)",
        data=csv,
        file_name='registre_patients.csv',
        mime='text/csv',
    )

    if len(df) >= 2:
        st.divider()
        st.subheader("ANALYSE DES STATISTIQUE")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Moyenne Tension", f"{df['tension'].mean():.1f}")
        col2.metric("Médiane", f"{df['tension'].median():.1f}")
        col3.metric("Variance", f"{df['tension'].var():.1f}")
        col4.metric("Écart-type", f"{df['tension'].std():.1f}")

        st.write("### VISUALISATION DES GRAPHIQUES")
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("**Distribution**")
            fig1, ax1 = plt.subplots()
            # On force le graphique à être lisible sur fond sombre
            fig1.patch.set_facecolor('#2c3e50')
            ax1.set_facecolor('#2c3e50')
            sns.histplot(df['tension'], kde=True, ax=ax1, color="cyan")
            ax1.tick_params(colors='white')
            st.pyplot(fig1)
            
        with g2:
            st.write("**Régression Âge/Tension**")
            fig2, ax2 = plt.subplots()
            fig2.patch.set_facecolor('#2c3e50')
            ax2.set_facecolor('#2c3e50')
            sns.regplot(x=df['age'], y=df['tension'], ax=ax2, color="orange")
            ax2.tick_params(colors='white')
            st.pyplot(fig2)
            
            a, b = np.polyfit(df['age'], df['tension'], 1)
            st.info(f"Tendance : +{a:.2f} mmHg par an.")
else:
    st.info(" Enregistrez un patient pour voir les analyses.")
    # --- PIED DE PAGE (FOOTER) ---
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        text-align: center;
        padding: 10px;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 14px;
        letter-spacing: 1px;
    }
    </style>
    <div class="footer">
        <p>Développé  <b>GEOVANNY ESSINDI VICTOR</b> | TP INF232 - 2026</p>
    </div>
    """, unsafe_allow_html=True)
