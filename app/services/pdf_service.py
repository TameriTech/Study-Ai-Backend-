def process_pdf(filename: str, content_base64: str):
     # Fake traitement du PDF
    print(f"Traitement du fichier : {filename}")
    return {
        "filename": filename,
        "nb_pages": 2,
        "concepts_detected": ["Deep Learning", "Regression"]
    }