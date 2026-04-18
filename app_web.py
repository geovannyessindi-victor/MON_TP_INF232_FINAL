import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- CONFIGURATION & BD ---
st.set_page_config(page_title="Analyse Santé - TP INF232", layout="wide")

def init_db():
    conn = sqlite3.connect('sante_web.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (nom TEXT, prenom TEXT, age INTEGER, maladie TEXT, tension INTEGER)''')
    conn.close()

init_db()

# --- INTERFACE ---
st.title("🏨️ Système de Collecte et d'Analyse Descriptive")

with st.sidebar:
    st.header(" Saisie Patient")
    with st.form("form_web", clear_on_submit=True):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        age = st.number_input("Âge", 1, 100, 25)
        tension = st.number_input("Tension (mmHg)", 50, 200, 120)
        maladie = st.text_input("Maladie")
        if st.form_submit_button("Enregistrer"):
            conn = sqlite3.connect('sante_web.db')
            conn.execute('INSERT INTO patients VALUES (?,?,?,?,?)', (nom, prenom, age, maladie, tension))
            conn.commit()
            conn.close()
            st.success("Enregistré !")

# --- LOGIQUE DE CALCUL ---
conn = sqlite3.connect('sante_web.db')
df = pd.read_sql_query('SELECT * FROM patients', conn)
conn.close()

if len(df) >= 2:
    # Tableau
    st.subheader(" Registre des Patients")
    st.dataframe(df, use_container_width=True)
    
    # Stats
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Moyenne Tension", f"{df['tension'].mean():.2f}")
    m2.metric("Médiane", f"{df['tension'].median():.2f}")
    m3.metric("Variance", f"{df['tension'].var():.2f}")
    m4.metric("Écart-type", f"{df['tension'].std():.2f}")

    # Graphiques
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        fig1, ax1 = plt.subplots()
        sns.histplot(df['tension'], kde=True, ax=ax1, color="green")
        st.pyplot(fig1)
    with col2:
        fig2, ax2 = plt.subplots()
        sns.regplot(x=df['age'], y=df['tension'], ax=ax2, line_kws={"color": "red"})
        st.pyplot(fig2)
        a, b = np.polyfit(df['age'], df['tension'], 1)
        st.info(f"Analyse : La tension augmente de {a:.2f} mmHg par an.")
else:
    st.info("Ajoutez au moins 2 patients pour voir les analyses.")
