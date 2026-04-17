from fastapi import FastAPI
import sqlite3
import pandas as pd
from pydantic import BaseModel
import numpy as np

app = FastAPI()

def init_db():
    conn = sqlite3.connect('sante.db')
    # Structure complète : Nom, Prénom, Age, Maladie + Tension [cite: 4]
    conn.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (nom TEXT, prenom TEXT, age INTEGER, maladie TEXT, tension INTEGER)''')
    conn.close()

init_db()

class Patient(BaseModel):
    nom: str
    prenom: str
    age: int
    maladie: str
    tension: int

@app.post("/patients/")
def create_patient(patient: Patient):
    conn = sqlite3.connect('sante.db')
    conn.execute('INSERT INTO patients VALUES (?,?,?,?,?)', 
                 (patient.nom, patient.prenom, patient.age, patient.maladie, patient.tension))
    conn.commit()
    conn.close()
    return {"message": "Données enregistrées"}

@app.get("/stats/")
def get_stats():
    conn = sqlite3.connect('sante.db')
    df = pd.read_sql_query('SELECT * FROM patients', conn)
    conn.close()
    
    if df.empty or len(df) < 2: 
        return {"error": "Pas assez de données"}
    
    # Calcul de la pente (a) et de l'interception (b)
    X = df['age'].values
    y = df['tension'].values
    a, b = np.polyfit(X, y, 1)
    
    # Phrase d'interprétation 
    tendance = "augmente" if a > 0 else "diminue"
    interpretation = f"En moyenne, la tension {tendance} de {abs(round(a, 2))} mmHg par année d'âge."

    return {
        "data": df.to_dict(orient="records"),
        "moyenne": round(float(df['tension'].mean()), 2),
        "mediane": round(float(df['tension'].median()), 2),
        "variance": round(float(df['tension'].var()), 2),
        "ecart_type": round(float(df['tension'].std()), 2),
        "reg_x": X.tolist(),
        "reg_y": (a * X + b).tolist(),
        "analyse_texte": interpretation # Nouvelle donnée envoyée
    }
