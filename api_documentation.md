# 📘 Documentation de l'API StudyAI

Cette documentation décrit les principales routes de l'API du backend StudyAI, développée avec **FastAPI**. Elle permet l'upload et le traitement de fichiers pédagogiques (PDF, vidéo) afin de générer des contenus adaptés à l'apprentissage : fiches de révision, quiz, etc.

---

## 🔗 Base URL

```
http://localhost:8000
```

---

## 📄 POST `/pdf/upload-pdf`

**Description :** Upload d'un fichier PDF encodé en base64 pour traitement automatique.

### 🔸 Requête
- Méthode : `POST`
- Headers : `Content-Type: application/json`
- Corps de la requête :

```json
{
  "filename": "exemple.pdf",
  "content_base64": "<contenu encodé en base64>"
}
```

### 🔸 Réponse (200 OK)
```json
{
  "message": "PDF traité avec succès",
  "details": {
    "filename": "exemple.pdf",
    "nb_pages": 12,
    "concepts_detected": [
      "Machine Learning",
      "Réseaux de neurones",
      "Analyse de texte"
    ]
  }
}
```

---

## 🎥 POST `/video/upload`

**Description :** Upload d'une vidéo pédagogique pour transcription et analyse de concepts (à venir).

### 🔸 Requête
```json
{
  "filename": "cours_ai.mp4",
  "content_base64": "<base64_video>"
}
```

### 🔸 Réponse attendue
```json
{
  "message": "Vidéo reçue",
  "status": "Traitement en cours"
}
```

---

## 🧠 GET `/quiz/generate?document_id=123`

**Description :** Génére un quiz automatiquement basé sur un document analysé.

### 🔸 Réponse exemple
```json
{
  "quiz": [
    {
      "question": "Qu'est-ce que le Machine Learning ?",
      "choices": ["Apprentissage automatique", "Traitement d'image", "Compilation"],
      "answer": "Apprentissage automatique"
    },
    {
      "question": "Quel outil est utilisé pour extraire le texte d'un PDF ?",
      "choices": ["OpenCV", "PDFMiner", "FastAPI"],
      "answer": "PDFMiner"
    }
  ]
}
```

---

## 🗣️ POST `/feedback/send`

**Description :** Permet aux utilisateurs de soumettre des retours sur les fiches ou quiz générés.

### 🔸 Requête
```json
{
  "user_id": 1,
  "document_id": 12,
  "message": "Très utile, mais il manque la partie sur le deep learning."
}
```

### 🔸 Réponse
```json
{
  "message": "Merci pour votre retour !"
}
```

---

## 🛡️ Authentification (à venir)
Certaines routes nécessiteront une authentification par token JWT : login, gestion des utilisateurs, etc.

---

## 🧪 Accès aux docs interactives

- Swagger UI : [`/docs`](http://localhost:8000/docs)
- ReDoc : [`/redoc`](http://localhost:8000/redoc)
- OpenAPI : [`/openapi.json`](http://localhost:8000/openapi.json)

---

> 🧬 Cette documentation est amenée à évoluer en fonction des nouvelles fonctionnalités ajoutées à StudyAI.

