import json
import os

BASE_PATH = os.path.dirname(__file__)
TRANSLATIONS = {}

def load_translations():
    global TRANSLATIONS
    languages = ["en", "fr"]
    for lang in languages:
        path = os.path.join(BASE_PATH, f"../translations/{lang}.json")
        with open(path, encoding="utf-8") as f:
            TRANSLATIONS[lang] = json.load(f)

load_translations()

def translate(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

def get_lang_from_request(request):
    accept_lang = request.headers.get("accept-language", "en")
    return "fr" if "fr" in accept_lang.lower() else "en"
