import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

URL_API = "http://127.0.0.1:8000"

st.set_page_config(page_title="TP INF232 - Collecte Santé", layout="wide")
st.title("🏨️Application de Collecte et d'Analyse Descriptive")

# --- FORMULAIRE  ---
with st.sidebar:
    st.header(" Nouveau Patient")
    with st.form("my_form", clear_on_submit=True):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        age = st.number_input("Âge", 1, 100, 25)
        tension = st.number_input("Tension (mmHg)", 50, 200, 120)
        maladie = st.text_input("Maladie (ex: Paludisme)")
        
        if st.form_submit_button("Envoyer à l'API"):
            requests.post(f"{URL_API}/patients/", 
                         json={"nom":nom, "prenom":prenom, "age":age, "maladie":maladie, "tension":tension})
            st.success("Enregistré !")

# --- AFFICHAGE & ANALYSE ---
try:
    res = requests.get(f"{URL_API}/stats/").json()
    if "data" in res:
        df = pd.DataFrame(res['data'])
        # 3. Section Données & Téléchargement (Efficacité)
        st.divider()
        st.write("###  Registre des Patients")
        st.dataframe(df, use_container_width=True)
        
        # 1. Section Statistiques avec Design
        st.subheader("Indicateurs Clés (Tension)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Moyenne", f"{res['moyenne']} mmHg")
        m2.metric("Médiane", f"{res['mediane']} mmHg")
        m3.metric("Variance", res['variance'])
        m4.metric("Écart-type", res['ecart_type'])
        
        # 2. Section Graphiques (Esthétique : 2 colonnes)
        st.divider()
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("###  Distribution (Histogramme)")
            fig1, ax1 = plt.subplots()
            sns.histplot(df['tension'], kde=True, ax=ax1, color="#2ecc71") # Vert esthétique
            st.pyplot(fig1)
            
        with g2:
            st.write("###  Tendance (Régression)")
            fig2, ax2 = plt.subplots()
            sns.regplot(x=df['age'], y=df['tension'], ax=ax2, line_kws={"color": "red"})
            st.pyplot(fig2)
            st.info(f"**Interprétation :** {res['analyse_texte']}") # Affiche l'analyse du Backend
        
        # Bouton pour télécharger en CSV (Pratique pour le prof)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger les données (CSV)",
            data=csv,
            file_name='patients_data.csv',
            mime='text/csv',
        )
except:
    st.warning("L'API est en attente de données...")
