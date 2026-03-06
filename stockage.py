import json
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

def lire_json(nom_fichier):
    chemin = os.path.join(DATA_DIR, nom_fichier)

    if not os.path.exists(chemin):
        return []

    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def ecrire_json(nom_fichier, donnees):
    chemin = os.path.join(DATA_DIR, nom_fichier)

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)
        