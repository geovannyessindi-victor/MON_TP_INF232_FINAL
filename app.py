import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Configuration et Style
st.set_page_config(page_title="TP INF232 - Santé", page_icon="🩺️")
# 2. Base de données
def init_db():
    conn = sqlite3.connect('sante_finale.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (nom TEXT, prenom TEXT, age INTEGER, maladie TEXT, tension INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# 3. INTERFACE DE DÉPART (Même classement)
st.title(" 📲️ APPLICATION DE COLLECTE DE DONNE EN LIGNE DES PATIENTS")

# Formulaire de saisie (Sidebar comme avant)
with st.sidebar:
    st.header("ENREGISTRER VOUS ")
    with st.form("form_patient", clear_on_submit=True):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        age = st.number_input("Âge")
        tension = st.number_input("Tension (mmHg)")
        # Liste de maladies prédéfinies
        liste_maladies = [
            "Aucune (RAS)", 
            "Diarhee", 
            "Diabète Type 1", 
            "Diabète Type 2", 
            "Paludisme", 
            "Drépanocytose",
            "Asthme",
            "Obésité",
            "Insuffisance Rénale",
            "Toux",
            "Grippe",
            "Autre..."
        ]
        
        # Utilisation d'une boîte de sélection
        maladie = st.selectbox("Sélectionner la Maladie", liste_maladies)
        
        # Si l'utilisateur choisit "Autre...", on peut lui laisser taper à la main
        if maladie == "Autre...":
            maladie_precision = st.text_input("Précisez la maladie")
            maladie = maladie_precision if maladie_precision else "Autre"
        envoyer = st.form_submit_button("Enregistrer le Patient")

    if envoyer:
        conn = sqlite3.connect('sante_finale.db')
        conn.execute('INSERT INTO patients VALUES (?,?,?,?,?)', (nom, prenom, age, maladie, tension))
        conn.commit()
        conn.close()
        st.success("Patient ajouté avec succès !")

    st.divider()
    # BOUTON DE SORTIE (Arrête l'application ou affiche un message de fin)
    if st.button("📴️ SORTIR"):
        st.warning("Session terminée. Vous pouvez fermer cet onglet.")
        st.stop()

# 4. AFFICHAGE ET ANALYSE (Corps principal)
conn = sqlite3.connect('sante_finale.db')
df = pd.read_sql_query('SELECT * FROM patients', conn)
conn.close()

if not df.empty:
    st.subheader(" Registre des Patients")
    st.dataframe(df, use_container_width=True)
    
    # BOUTON DE TÉLÉCHARGEMENT (CSV)
    st.write("---")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les données (CSV)",
        data=csv,
        file_name='registre_patients.csv',
        mime='text/csv',
    )

    if len(df) >= 2:
        st.divider()
        st.subheader(" Statistiques Descriptives")
        
        # Métriques
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Moyenne Tension", f"{df['tension'].mean():.2f}")
        m2.metric("Médiane", f"{df['tension'].median():.2f}")
        m3.metric("Variance", f"{df['tension'].var():.2f}")
        m4.metric("Écart-type", f"{df['tension'].std():.2f}")

        # Graphiques
        st.write("###  Visualisations")
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("**Distribution de la Tension**")
            fig1, ax1 = plt.subplots()
            sns.histplot(df['tension'], kde=True, ax=ax1, color="skyblue")
            st.pyplot(fig1)
            
        with g2:
            st.write("**Corrélation Âge / Tension**")
            fig2, ax2 = plt.subplots()
            sns.regplot(x=df['age'], y=df['tension'], ax=ax2, line_kws={"color": "red"})
            st.pyplot(fig2)
            
            # Analyse mathématique
            a, b = np.polyfit(df['age'], df['tension'], 1)
            st.info(f"Analyse : Pour chaque année, la tension augmente de {a:.2f} mmHg.")
else:
    st.info("La base de données est vide. Utilisez le formulaire à gauche pour commencer.")
