Application de Collecte et d'Analyse Descriptive (TP INF232)

1- Description du Projet

   Ce projet a été réalisé dans le cadre du TP de l'UE INF232. Il s'agit d'une application complète de collecte de données médicales et d'analyse descriptive en temps réel.
  L'application permet d'enregistrer des patients (Nom, Prénom, Âge, Maladie, Tension Artérielle) via une interface moderne, de stocker ces données dans une base SQLite, et de générer automatiquement des statistiques (moyenne, variance, etc.) ainsi qu'une régression linéaire corrélant l'âge et la tension.

2- Technologies Utilisées

  Pour garantir la robustesse et l'efficacité, nous avons utilisé :

  Backend : FastAPI (Python) pour la gestion de l'API REST.

  Frontend : Streamlit pour l'interface utilisateur interactive.

  Base de Données : SQLite3 pour le stockage local persistant.

  Analyse de Données : Pandas et NumPy.

  Visualisation : Matplotlib et Seaborn.

3- Fonctionnalités Clés

  Formulaire Intelligent : Saisie sécurisée avec réinitialisation automatique après envoi.

  Statistiques Automatiques : Calcul en temps réel de la Moyenne, Médiane, Variance et Écart-type.

  Visualisation Graphique :

  Histogramme de distribution des tensions.

  Graphique de Régression Linéaire montrant l'évolution de la tension par rapport à l'âge.

  Export de Données : Bouton permettant de télécharger le registre des patients au format CSV.

  Interprétation  : Analyse textuelle automatique des résultats de la régression.

4- Installation et Exécution

  Pour faire fonctionner ce projet sur une autre machine (Linux, Windows ou Mac), suivez ces étapes :

   a).Cloner le projet
    Bash

      git clone https://github.com/geovannyessindi-victor/MON_TP_INF232_FINAL.git
    cd MON_TP_INF232_FINAL
   b) Créer l'environnement virtuel et installer les dépendances
    Bash

    python3 -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    pip install -r requirements.txt
  c) Lancer le Backend (API)
  Ouvrez un premier terminal et lancez le serveur FastAPI :

    Bash

    uvicorn main:app --reload
    L'API sera disponible sur : http://127.0.0.1:8000

d)Lancer le Frontend (Interface)
  Ouvrez un second terminal et lancez l'interface Streamlit :

  Bash

    streamlit run app.py
    L'interface s'ouvrira automatiquement dans votre navigateur.

Auteur : Geovanny Essindi Victor

Contact : 692705083 Email: geovanny.essindi@facsciences-uy1.cm

Projet rendu à : Dr NDOM (rollinfrancis28@gmail.com)

NB Comment l'ajouter sur github
Crée le fichier : nano README.md.

 inserrer votre readme

Enregistre (Ctrl+O, Entrée, Ctrl+X).

Envoie-le sur GitHub :

Bash

    git add README.md
    git commit -m "Ajout du README complet"
    git push origin main
