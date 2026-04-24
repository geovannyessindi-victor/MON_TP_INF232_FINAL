import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Santé Privée - INF232", page_icon="🩺", layout="wide")

st.markdown("""
   

   <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                   url('https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* BOUTONS MÊME TAILLE MENU */
    .stButton > button {
        width: 400px !important;
        min-width: 400px !important;
        max-width: 400px !important;
        height: 85px !important; 
        font-size: 22px !important;
        font-weight: 800 !important;
        border-radius: 10px !important; 
        background: linear-gradient(45deg, #2c3e50, #3498db) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        text-transform: uppercase;
        transition: 0.3s;
        display: block !important;
        margin: 8px auto !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        border-color: #f1c40f !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }

    /* BOUTON RETOUR ROUGE */
    .retour-container div.stButton > button {
        height: 50px !important;
        background: linear-gradient(45deg, #c0392b, #e74c3c) !important;
        width: 100% !important;
        padding: 0 40px !important;
        font-size: 18px !important;
        color: white !important;
        border: 2px solid #e74c3c !important;
    }

    .retour-container div.stButton > button:hover {
        background: linear-gradient(45deg, #a93226, #c0392b) !important;
        border-color: #ff6b6b !important;
    }
    
    /* TITRE CLIGNOTANT */
    @keyframes clignoter {
        0%   { color: red; }
        20%  { color: blue; }
        40%  { color: green; }
        60%  { color: orange; }
        80%  { color: brown; }
        100% { color: red; }
    }

    h1 { 
        text-align: center; 
        font-size: 55px !important; 
        font-weight: 900; 
        animation: clignoter 1.5s infinite;
    }

    /* ÉCRITURES EN GRAS */
    h2 { color: #3498db !important; text-align: center; font-size: 28px !important; font-weight: bold !important; }
    p, div, span, label { font-weight: bold !important; }
    .stMetric { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if 'page' not in st.session_state: st.session_state.page = 'MENU'
if 'auth' not in st.session_state: st.session_state.auth = False
if 'form_key' not in st.session_state: st.session_state.form_key = 0

def init_db():
    conn = sqlite3.connect('sante_finale.db')
    cursor = conn.cursor()
    # Création de la table
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prenom TEXT, age INTEGER,sexe TEXT, maladie TEXT, tension INTEGER, statut TEXT)''')
    
    # Vérification si la table est vide
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    
    # Si la table est vide (0 nom), on ajoute les 4 patients par défaut
    if count == 0:
        patients_test = [
            ('ESSINDI', 'Geovanny', 22, 'masculin','Aucune', 120, 'Consulté'),
            ('NDONGO', 'Marie', 45, 'feminin','Hypertension', 155, 'En attente'),
            ('BEKONO', 'Jean', 30,'masculin', 'Paludisme', 110, 'Consulté'),
            ('ABENA', 'Alice', 60,'feminin', 'Diabète', 135, 'En attente')
        ]
        cursor.executemany('''INSERT INTO patients (nom, prenom, age,sexe, maladie, tension, statut) 
                              VALUES (?, ?, ?, ?,?, ?, ?)''', patients_test)
        
    conn.commit()
    conn.close()

init_db()

def bouton_retour():
    st.markdown('<div class="retour-container">', unsafe_allow_html=True)
    if st.button("⬅️ RETOUR AU MENU PRINCIPAL"):
        st.session_state.page = 'MENU'; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. PAGES ---

def menu_principal():
    st.title("🏨️ SYSTÈME DE GESTION MÉDICALE")
    st.write("###🩺️ La sante notre priorite")
    st.write("---")
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button(" INSCRIPTION"): st.session_state.page = 'INSCRIPTION'; st.rerun()
        if st.button(" ANALYSES & STATS"): st.session_state.page = 'ANALYSE'; st.rerun()
    with col2:
        if st.button(" SESSIONS PATIENTS"): st.session_state.page = 'SESSION'; st.rerun()
        if st.button(" RÉGRESSION & PROGRÈS"): st.session_state.page = 'PROGRES'; st.rerun()
            
    st.write("---")
    _, center, _ = st.columns([1,1,1])
    with center:
        st.write("<p style='text-align:center;'> ZONE DOCTEUR</p>", unsafe_allow_html=True)
        code = st.text_input("", type="password", placeholder="Code secret...")
        st.session_state.auth = (code == "1234")

def page_analyse():
    bouton_retour()
    st.header("📊 ANALYSES STATISTIQUES DÉTAILLÉES")
    conn = sqlite3.connect('sante_finale.db')
    df = pd.read_sql_query('SELECT * FROM patients', conn); conn.close()
    
    if not df.empty:
        # --- BLOC DES MÉTRIQUES (MOYENNE, VARIANCE, ÉCART-TYPE) ---
        st.subheader("I-) Indicateurs de la Tension (mmHg)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Moyenne Tension", f"{df['tension'].mean():.2f}")
        c2.metric("Variance Tension", f"{df['tension'].var():.2f}")
        c3.metric("Écart-Type Tension", f"{df['tension'].std():.2f}")

        st.subheader("II-) Indicateurs de l'Âge (ans)")
        a1, a2, a3 = st.columns(3)
        a1.metric("Moyenne Âge", f"{df['age'].mean():.2f}")
        a2.metric("Variance Âge", f"{df['age'].var():.2f}")
        a3.metric("Écart-Type Âge", f"{df['age'].std():.2f}")

        st.write("---")
        # --- GRAPHIQUES (HISTOGRAMME + CAMEMBERT) ---
        col_hist, col_pie = st.columns(2)
        
        with col_hist:
            st.write("### 📊️ Distribution (Histogramme)")
            fig1, ax1 = plt.subplots()
            fig1.patch.set_facecolor('none')
            sns.histplot(df['tension'], kde=True, ax=ax1, color="#3498db")
            ax1.tick_params(colors='white')
            st.pyplot(fig1)
            
        with col_pie:
            st.write("### 🔴️ Répartition des Maladies")
            fig2, ax2 = plt.subplots()
            fig2.patch.set_facecolor('none')
            df['maladie'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax2, textprops={'color':"w"})
            st.pyplot(fig2)
    else:
        st.info("La base de données est vide. Ajoutez des patients pour voir les analyses.")

def page_inscription():
    bouton_retour()
    st.header("📑️ INSCRIPTION NOUVEAU PATIENT")
    maladies = [
        "Aucune", "Paludisme", "Typhoïde", "Hypertension", "Diabète", 
        "Grippe", "Anémie", "Gastrite", "Asthme", "Infection Urinaire",
        "Bronchite", "Rhumatisme", "Hépatite B", "Tuberculose", "Dengue"
    ]
    with st.form(key=f"form_patient_{st.session_state.form_key}"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("NOM", placeholder="ex:LEWELL...")
        prenom = c2.text_input("PRÉNOM", placeholder="ex: LUCAS...")
        age = c1.number_input("ÂGE",placeholder="ex:24" )
        tension = c2.number_input("TENSION (Systolique)", placeholder="120")
        sexe = st.selectbox("SEXE", ["votre sexe...","Masculin", "Féminin"])
        maladie = st.selectbox("DIAGNOSTIC", maladies)
        statut = st.selectbox("STATUT", ["Choisir un statut","Urgent","En attente", "Consulté"])
        if st.form_submit_button("💾 ENREGISTRER LE PATIENT"):
            if nom and prenom:
                conn = sqlite3.connect('sante_finale.db')
                conn.execute('INSERT INTO patients (nom, prenom, age, sexe, maladie, tension, statut) VALUES (?,?,?,?,?,?,?)', (nom,prenom,age,sexe,maladie,tension,statut))
                conn.commit(); conn.close()
                st.success(" bienvenue M/Mme !")
                st.session_state.form_key += 1
                st.rerun()
            else: st.error("Veuillez remplir le nom et le prénom.")

def page_session():
    bouton_retour()
    st.header("📋 REGISTRE ET EXPORTATION")
    
    conn = sqlite3.connect('sante_finale.db')
    df = pd.read_sql_query('SELECT * FROM patients', conn)
    conn.close()

    if not df.empty:
        # Gestion de la confidentialité
        df_display = df.copy()
        if not st.session_state.auth:
            df_display['maladie'] = " CONFIDENTIEL"
        
        # Affichage du tableau
        st.dataframe(df_display, use_container_width=True)

        st.write("---")
        st.subheader("📥 Télécharger les données")
        st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] > button {
            background: linear-gradient(45deg, #1a6fc4, #2196F3) !important;
            color: white !important;
            border: 2px solid #2196F3 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            background: linear-gradient(45deg, #1558a0, #1a6fc4) !important;
            border-color: #64b5f6 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        col_csv, col_json = st.columns(2)
        with col_csv:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📊 Télécharger en CSV (Excel)", data=csv_data, file_name='liste_patients.csv', mime='text/csv', use_container_width=True)
        with col_json:
            json_data = df.to_json(orient='records', force_ascii=False, indent=4)
            st.download_button(label="{ } Télécharger en JSON", data=json_data, file_name='liste_patients.json', mime='application/json', use_container_width=True)

        st.write("---")

        # --- MODIFICATION 4 : MODIFIER LES INFOS D'UN PATIENT ---
        st.subheader("✏️ MODIFIER LES INFORMATIONS D'UN PATIENT")
        options = [f"ID {row['id']} - {row['nom']} {row['prenom']}" for _, row in df.iterrows()]
        choix = st.selectbox("Sélectionner un patient à modifier", options)
        patient_id = int(choix.split(" ")[1])
        patient = df[df['id'] == patient_id].iloc[0]
        maladies_list = ["Aucune","Paludisme","Typhoïde","Hypertension","Diabète","Grippe","Anémie","Gastrite","Asthme","Infection Urinaire","Bronchite","Rhumatisme","Hépatite B","Tuberculose","Dengue"]
        with st.form(key="form_modifier"):
            c1, c2 = st.columns(2)
            new_nom = c1.text_input("NOM", value=patient['nom'], placeholder="Entrez le nom...")
            new_prenom = c2.text_input("PRÉNOM", value=patient['prenom'], placeholder="Entrez le prénom...")
            new_age = c1.number_input("ÂGE", 0, 120, int(patient['age']))
            new_tension = c2.number_input("TENSION (Systolique)", 0, 250, int(patient['tension']))
            new_sexe = st.selectbox("SEXE", ["Masculin", "Féminin"], index=0 if patient['sexe'] == "Masculin" else 1)
            idx_maladie = maladies_list.index(patient['maladie']) if patient['maladie'] in maladies_list else 0
            new_maladie = st.selectbox("DIAGNOSTIC", maladies_list, index=idx_maladie)
            idx_statut = ["En attente","Consulté"].index(patient['statut']) if patient['statut'] in ["En attente","Consulté"] else 0
            new_statut = st.selectbox("STATUT", ["En attente","Consulté"], index=idx_statut)
            if st.form_submit_button("💾 SAUVEGARDER LES MODIFICATIONS"):
                if new_nom and new_prenom:
                    conn2 = sqlite3.connect('sante_finale.db')
                    conn2.execute('UPDATE patients SET nom=?, prenom=?, age=?, sexe=?, maladie=?, tension=?, statut=? WHERE id=?',
              (new_nom, new_prenom, new_age, new_sexe, new_maladie, new_tension, new_statut, patient_id))
                    conn2.commit(); conn2.close()
                    st.success(f" Informations de {new_nom} {new_prenom} mises à jour !")
                    st.rerun()
                else:
                    st.error("Le nom et le prénom sont obligatoires.")


    else:
        st.info("Le registre est vide.")

def page_progres():
    bouton_retour()
    st.header("📈 ANALYSE DE LA RÉGRESSION")
    conn = sqlite3.connect('sante_finale.db')
    df = pd.read_sql_query('SELECT * FROM patients', conn); conn.close()
    if len(df) >= 2:
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('none')
        sns.regplot(x=df['age'], y=df['tension'], ax=ax, color="#f1c40f", line_kws={"color": "red"})
        ax.tick_params(colors='white')
        st.pyplot(fig)
        
        pente, inter = np.polyfit(df['age'], df['tension'], 1)
        st.latex(f"y = {pente:.2f}x + {inter:.2f}")
        st.write(f"**Analyse :** Pour chaque année, la tension augmente de **{pente:.2f} mmHg**.")
    else: st.warning("Données insuffisantes pour calculer la régression.")

# --- 4. NAVIGATION ---
if st.session_state.page == 'MENU': menu_principal()
elif st.session_state.page == 'INSCRIPTION': page_inscription()
elif st.session_state.page == 'SESSION': page_session()
elif st.session_state.page == 'ANALYSE': page_analyse()
elif st.session_state.page == 'PROGRES': page_progres()
st.markdown(f'<div style="position:fixed;bottom:0;width:100%;text-align:center;color:white;background:rgba(0,0,0,0.9);padding:5px;"><b>GEOVANNY ESSINDI VICTOR</b> | TP INF232 - 2026</div>', unsafe_allow_html=True)

