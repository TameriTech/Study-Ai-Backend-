# Study-Ai-Backend-
Bienvenu dans le Study Ai Backend 
🔐 Pour accéder à certaines fonctionnalités, configurez les clés API (OpenAI, Google Speech, etc.) dans un fichier .env.

📌 Auteurs & Contribution
Développé par Tameri Tech
Contact : contact@tameri-tech.com


# 📚 Study AI – Plateforme d'apprentissage intelligente

**Study AI** est une application innovante développée par Tameri Tech visant à transformer l'apprentissage des étudiants en automatisant l'analyse de documents PDF et de vidéos de cours. Grâce à l’intelligence artificielle, l’application génère des fiches de révision et des quiz personnalisés à partir du contenu importé.

---

## 🚀 Objectifs

- Offrir une solution complète et interactive pour aider les étudiants à réviser efficacement.
- Générer automatiquement des supports pédagogiques à partir de documents et vidéos.
- Améliorer la pertinence des contenus via l’intelligence artificielle et les retours utilisateurs.

---

## 🧠 Fonctionnalités principales

- 📄 **Importation de documents PDF**  
  - Extraction de texte et de code source.
  - Analyse du contenu pédagogique.

- 🎥 **Analyse de vidéos de cours**  
  - Traitement d’image et reconnaissance vocale.
  - Extraction de concepts clés.

- 📝 **Génération automatique de contenus**  
  - Fiches de révision synthétiques.
  - Quiz personnalisés.

- 🤖 **Intelligence Artificielle & Feedback**  
  - Amélioration continue des quiz.
  - Système de retour utilisateur intégré.

- 📊 **Tableau de bord interactif**  
  - Accès aux fichiers, fiches et quiz.
  - Visualisation des performances.

---

## 🛠️ Technologies utilisées

| Composant       | Technologies                                                  |
|-----------------|---------------------------------------------------------------|
| Backend         | Python, FastAPI                                               |
| Frontend        | Kotlin (Java)                                                 |
| Base de données | PostgreSQL                                                    |
| PDF             | PDFMiner, Apache Tika                                         |
| Vidéo & Audio   | OpenCV, Google/Azure Speech-to-Text                           |
| Intelligence Artificielle | OpenAI API (GPT-4), TensorFlow / PyTorch               |

---

## 📐 Architecture du projet

L'application suit une **architecture en couches** modulaire avec séparation claire entre :
- Modules de traitement (PDF/Vidéo)
- Moteur de génération
- Système IA & feedback
- Interfaces utilisateur

## 📁 Structure de projet StudyAI
studyai/
├── app/                         # Code de l'application principale
│   ├── main.py                  # Point d’entrée de l'application FastAPI
│   ├── config.py                # Configuration de l'app (DB, API keys...)
│   ├── routers/                 # Routes FastAPI (controllers)
│   │   ├── pdf_router.py
│   │   ├── video_router.py
│   │   ├── quiz_router.py
│   │   ├── feedback_router.py
│   │   └── user_router.py
│   ├── services/                # Logique métier (modules fonctionnels)
│   │   ├── pdf_service.py
│   │   ├── video_service.py
│   │   ├── quiz_generator.py
│   │   ├── feedback_service.py
│   │   └── ai_engine.py
│   ├── models/                  # Modèles de données SQLAlchemy
│   │   ├── user.py
│   │   ├── quiz.py
│   │   ├── feedback.py
│   │   └── document.py
│   ├── schemas/                 # Schémas Pydantic (entrées/sorties API)
│   │   ├── user_schema.py
│   │   ├── pdf_schema.py
│   │   ├── quiz_schema.py
│   │   └── feedback_schema.py
│   ├── utils/                   # Fonctions utilitaires (OCR, NLP, etc.)
│   │   ├── ocr_tools.py
│   │   ├── nlp_tools.py
│   │   └── speech_to_text.py
│   └── database/                # Connexion à la BDD, ORM
│       ├── session.py
│       └── init_db.py
│
├── frontend/                    # (optionnel) Kotlin ou HTML/JS
│   └── ...
├── data/                        # Fichiers de test ou exemples PDF/vidéos
├── tests/                       # Tests unitaires et d’intégration
│   ├── test_pdf.py
│   ├── test_video.py
│   └── test_quiz.py
├── .env                         # Variables d’environnement
├── requirements.txt             # Dépendances Python
├── README.md                    # Présentation du projet
└── alembic/                     # Migrations de base de données


> Diagrammes UML disponibles dans le rapport d’analyse.

---

## ⚠️ Contraintes & défis

- Gestion des formats PDF variés (code inclus)
- Qualité hétérogène des vidéos (bruit, résolution)
- Temps de traitement pour gros fichiers
- Interface à la fois intuitive et complète

---

## ✅ Critères de validation

| Fonctionnalité      | Critère attendu                                     |
|---------------------|-----------------------------------------------------|
| PDF                 | Taux de précision > 95%                             |
| Vidéo               | Concepts extraits correctement > 90% des cas        |
| Quiz                | Cohérence et pertinence du contenu généré           |
| Performances        | Temps de réponse rapide, même avec des fichiers lourds |
| Feedback utilisateur| Interface accessible et encouragée                  |

---

## 🧪 Tests

- 🔬 **Tests unitaires** : PDFImporter, VideoAnalyzer, QuizGenerator, FeedbackSystem
- 🔗 **Tests d’intégration** : flux complet (import → quiz)
- 🧭 **Tests fonctionnels** : cas d’usage étudiants simulés
- 📈 **Tests de performance** : scalabilité et temps de réponse
- 👥 **Tests utilisateurs** : feedback réel pour itération

---

## 🏁 Lancement rapide (dev)

```bash
# Cloner le projet
git clone https://github.com/TameriTech/Study-Ai-Backend-.git
cd study-ai

# Créer l'environnement virtuel
python -m venv env
source env/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
uvicorn main:app --reload

