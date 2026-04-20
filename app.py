import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prenom TEXT, age INTEGER, maladie TEXT, tension INTEGER, statut TEXT)''')
    conn.commit()
    conn.close()

init_db()
with st.sidebar:
    st.header("ACCÈS MÉDICAL")
    code_secret = st.text_input("Code Docteur (Secret)", type="password")
    acces_autorise = (code_secret == "1234") 

    st.divider()
    
    tab1, tab2 = st.tabs(["➕ Nouveau", " Modifier"])
    
    with tab1:
        st.header(" ENREGISTREMENT")
        with st.form("form_patient", clear_on_submit=True):
            nom = st.text_input("Nom", placeholder="Ex: ESSINDI")
            prenom = st.text_input("Prénom", placeholder="Ex: Geovanny")
            age = st.number_input("Âge", 0, 120, 25, help="Entrez l'âge du patient")
            tension = st.number_input("Tension (mmHg)", 40, 250, 120, help="Ex: 120")
            
            liste_maladies = ["Aucune (RAS)", "Paludisme", "Diabète", "Hypertension", "Grippe", "Toux", "Autre..."]
            maladie_choisie = st.selectbox("Maladie", liste_maladies)
            statut_inf = st.selectbox("Statut", ["En attente", "Consulté"])
            envoyer = st.form_submit_button("Enregistrer")

        if envoyer and nom:
            conn = sqlite3.connect('sante_finale.db')
            conn.execute('INSERT INTO patients (nom, prenom, age, maladie, tension, statut) VALUES (?,?,?,?,?,?)', 
                         (nom, prenom, age, maladie_choisie, tension, statut_inf))
            conn.commit()
            conn.close()
            st.success("Données enregistrées !")
            st.rerun()

    with tab2:
        st.header("MODIFICATION")
        conn = sqlite3.connect('sante_finale.db')
        df_edit = pd.read_sql_query('SELECT id, nom, prenom FROM patients', conn)
        conn.close()
        
        if not df_edit.empty:
            liste_p = {f"{row['id']} - {row['nom']}": row['id'] for _, row in df_edit.iterrows()}
            cible = st.selectbox("Patient à modifier", list(liste_p.keys()))
            nouveau_statut = st.selectbox("Changer le statut", ["En attente", "Consulté"])
            
            if st.button("Mettre à jour"):
                conn = sqlite3.connect('sante_finale.db')
                conn.execute('UPDATE patients SET statut = ? WHERE id = ?', (nouveau_statut, liste_p[cible]))
                conn.commit()
                conn.close()
                st.success("Statut mis à jour !")
                st.rerun()

# 4. AFFICHAGE ET SECRET MÉDICAL
st.title("📲 GESTION ET ANALYSE DES PATIENTS")

conn = sqlite3.connect('sante_finale.db')
df = pd.read_sql_query('SELECT * FROM patients', conn)
conn.close()

if not df.empty:
    search_term = st.text_input("🔍️ Rechercher un patient par son nom :", placeholder="Tapez un nom pour filtrer...")
    if search_term:
        df_filtered_view = df[df['nom'].str.contains(search_term, case=False)]
    else:
        df_filtered_view = df

    df['État Tension'] = df['tension'].apply(lambda t: " Normale" if t < 140 else "Élevée")

    st.subheader("Registre des Consultations")
    
    df_affichage = df_filtered_view.copy()
    if not acces_autorise:
        df_affichage['maladie'] = " CONFIDENTIEL"
        st.info(" Mode Public : Les diagnostics sont masqués par le secret médical.")
    else:
        st.warning(" Mode Docteur : Accès aux diagnostics autorisé.")

    st.dataframe(df_affichage, use_container_width=True)

    def export_pdf(data):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "RAPPORT MÉDICAL ")
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"Nombre de patients : {len(data)}")
        c.drawString(100, 710, f"Moyenne Tension : {data['tension'].mean():.1f} mmHg")
        y = 680
        for i, row in data.iterrows():
            c.drawString(100, y, f"- {row['nom']} {row['prenom']} | Tension: {row['tension']} | Statut: {row['statut']}")
            y -= 20
            if y < 50: break
        c.save()
        buf.seek(0)
        return buf

    st.download_button(
        label=" Générer le Rapport PDF",
        data=export_pdf(df),
        file_name="rapport_medical.pdf",
        mime="application/pdf"
    )

    if len(df) >= 2:
        st.divider()
        st.subheader(" Analyses Descriptives et Régression")
        
        st.write("**Statistiques de la Tension**")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Moyenne", f"{df['tension'].mean():.1f}")
        col_m2.metric("Variance", f"{df['tension'].var():.1f}")
        col_m3.metric("Écart-type", f"{df['tension'].std():.1f}")
        correlation = df['age'].corr(df['tension'])
        col_m4.metric("Corrélation (r)", f"{correlation:.2f}")
        
        st.write("**Statistiques de l'Âge**")
        col_a1, col_a2, col_a3 = st.columns(3)
        col_a1.metric("Moyenne Âge", f"{df['age'].mean():.1f}")
        col_a2.metric("Variance Âge", f"{df['age'].var():.1f}")
        col_a3.metric("Écart-type Âge", f"{df['age'].std():.1f}")

        g1, g2, g3 = st.columns(3)
        with g1:
            st.write("**Distribution**")
            fig1, ax1 = plt.subplots()
            fig1.patch.set_facecolor('#2c3e50')
            ax1.set_facecolor('#2c3e50')
            sns.histplot(df['tension'], kde=True, ax=ax1, color="cyan")
            ax1.tick_params(colors='white')
            st.pyplot(fig1)
        
        with g2:
            st.write("**🤮️Répartition Maladies**")
            fig_pie, ax_pie = plt.subplots()
            fig_pie.patch.set_facecolor('#2c3e50')
            counts = df['maladie'].value_counts()
            ax_pie.pie(counts, labels=counts.index, autopct='%1.1f%%', textprops={'color':"w"})
            st.pyplot(fig_pie)

        with g3:
            st.write("**〰️Régression**")
            fig2, ax2 = plt.subplots()
            fig2.patch.set_facecolor('#2c3e50')
            ax2.set_facecolor('#2c3e50')
            sns.regplot(x=df['age'], y=df['tension'], ax=ax2, color="orange", line_kws={"color": "red"})
            ax2.tick_params(colors='white')
            st.pyplot(fig2)

        pente, inter = np.polyfit(df['age'], df['tension'], 1)
        st.write("###  Analyse de la Régression")
        st.latex(f"y = {pente:.2f}x + {inter:.2f}")
        # --- BLOC ANALYSE DÉTAILLÉE (À AJOUTER) ---
        st.write("NB 🔍 Interprétation mathématique :")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            st.write(f"**La Pente ({pente:.2f}) :**")
            st.write(f"Cela signifie que statistiquement, pour chaque année d'âge supplémentaire, la tension augmente de **{pente:.2f} mmHg**.")
        with col_exp2:
            st.write(f"**L'ordonnée à l'origine ({inter:.2f}) :**")
            st.write(f"C'est la valeur théorique de la tension à l'âge 0. Ici, elle est de **{inter:.2f} mmHg**.")
        
        if pente > 0:
            st.success("1- Observation : Il existe une tendance à l'augmentation de la tension avec l'âge dans votre échantillon.")
        else:
            st.info("2- Observation : La tendance montre une légère baisse ou une stabilité de la tension avec l'âge.")
st.markdown(f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(0,0,0,0.8); text-align: center; padding: 8px;">
        <p style="margin:0; color: white; font-size: 14px;">
            Développé par <b>GEOVANNY ESSINDI VICTOR</b> | TP INF232 - 2026 
        </p>
    </div>
    """, unsafe_allow_html=True)
