# 📚 Study AI – Plateforme d'apprentissage intelligente

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Status](https://img.shields.io/badge/status-en%20cours-yellow)

---

## 📑 Table des matières

- [Présentation](#-study-ai--plateforme-dapprentissage-intelligente)
- [Objectifs](#-objectifs)
- [Fonctionnalités](#-fonctionnalités-principales)
- [Technologies](#-technologies-utilisées)
- [Architecture](#-architecture-du-projet)
- [Structure](#-structure-du-projet-studyai)
- [Contraintes](#-contraintes--défis)
- [Critères de validation](#-critères-de-validation)
- [Tests](#-tests)
- [Installation & Lancement](#-lancement-rapide-dev)
- [Fichier .env](#-exemple-de-fichier-env)
- [Contribution](#-contribuer)
- [Contact](#-auteurs--contribution)

---

## 🧠 Présentation

**Study AI** est une application innovante développée par **Tameri Tech** pour transformer l'apprentissage des étudiants. Elle permet d'automatiser l'analyse de contenus pédagogiques (PDF, vidéos) grâce à l'intelligence artificielle, et génère des fiches de révision et des quiz personnalisés.

---

## 🚀 Objectifs

- Offrir une solution interactive pour réviser efficacement
- Générer automatiquement des contenus à partir de documents/vidéos
- Améliorer la pertinence via l'IA et les retours utilisateurs

---

## 🧩 Fonctionnalités principales

- 📄 **PDF** : Importation, extraction, analyse de contenu
- 🎥 **Vidéos** : Traitement image, reconnaissance vocale
- 🖋️ **Génération automatique** : Fiches de révision, quiz personnalisés
- 🤖 **IA & Feedback** : Amélioration continue, retours utilisateurs
- 📊 **Dashboard interactif** : Accès aux fichiers, fiches et statistiques

---

## 🛠️ Technologies utilisées

| Composant       | Technologies                                                  |
|----------------|---------------------------------------------------------------|
| Backend         | Python, FastAPI                                               |
| Frontend        | Kotlin (Java) *(optionnel)*                                   |
| Base de données | PostgreSQL                                                    |
| PDF             | PDFMiner, Apache Tika                                         |
| Vidéo & Audio   | OpenCV, Google/Azure Speech-to-Text                           |
| IA              | OpenAI API (GPT-4), TensorFlow / PyTorch                      |

---

## 📊 Architecture du projet

L'application suit une **architecture modulaire en couches** :

- Routes FastAPI (pdf, vidéos, quiz, feedback, user)
- Services de traitement (OCR, NLP, IA, audio)
- Moteur de génération de quiz & fiches
- Système de feedback
- Base de données et modèles ORM

---

## 📁 Structure du projet StudyAI

```bash
studyai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   └── database/
├── frontend/
├── data/
├── tests/
├── .env
├── requirements.txt
├── README.md
└── alembic/
```

---

## ⚠️ Contraintes & défis

- Gestion de PDF variés (avec code, images, etc.)
- Qualité des vidéos/audio parfois faible
- Temps de traitement de gros fichiers
- Interface à la fois intuitive et riche

---

## ✅ Critères de validation

| Fonctionnalité       | Critère attendu                                     |
|----------------------|------------------------------------------------------|
| PDF                  | Précision > 95%                                     |
| Vidéo               | Concepts extraits dans > 90% des cas                 |
| Quiz                 | Pertinence du contenu généré                       |
| Performance          | Temps de réponse acceptable (même fichiers lourds)   |
| Feedback utilisateur | Système intuitif, utilisé activement                |

---

## 🧪 Tests

- 🔬 **Unitaires** : PDFImporter, VideoAnalyzer, QuizGenerator
- 🔗 **Intégration** : Chaîne complète (import → quiz)
- 🔍 **Fonctionnels** : Cas d’usage réels
- 📊 **Performance** : Scalabilité, charge
- 👥 **Utilisateurs** : Feedback humain pour ajustement

---

## 🏁 Lancement rapide (dev)

```bash
# Cloner le projet
git clone https://github.com/TameriTech/Study-Ai-Backend-.git
cd study-ai

# Créer l'environnement virtuel
python -m venv env
source env/Scripts/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
uvicorn app.main:app --reload
```

---

## 🔐 Exemple de fichier `.env`

```env
OPENAI_API_KEY=sk-xxx
GOOGLE_SPEECH_API_KEY=xxx
DATABASE_URL=postgresql://user:password@localhost/studyai
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

- Forkez le repo
- Créez une branche (`git checkout -b feature/ma-feature`)
- Commitez vos changements
- Push (`git push origin feature/ma-feature`)
- Ouvrez une pull request 🚀

---

## 📢 Auteurs & Contribution

**Développé par :** Tameri Tech  
**Contact :** [tameri.tech25@gmail.com](mailto:tameri.tech25@gmail.com)

> Diagrammes UML disponibles dans le rapport d’analyse officiel du projet.

---

**✨ Rejoignez la révolution de l'apprentissage intelligent avec Study AI.**

