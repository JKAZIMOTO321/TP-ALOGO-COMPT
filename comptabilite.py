from datetime import datetime
from stockage import lire_json, ecrire_json


FICHIER_OPERATIONS = "operations.json"
FICHIER_JOURNAL = "journal.json"


def charger_operations():
    return lire_json(FICHIER_OPERATIONS)


def obtenir_nouveau_numero():
    journal = lire_json(FICHIER_JOURNAL)

    if not journal:
        return 1

    return journal[-1]["numero"] + 1


def calculer_montants(operation, valeurs):

    if operation["type_tva"] == "avec_tva":

        ht = float(valeurs.get("montant_ht", 0))
        taux = float(valeurs.get("taux_tva", 0))
        tva = ht * taux / 100
        ttc = ht + tva

        return ht, tva, ttc

    else:
        montant = list(valeurs.values())[0]
        return montant, 0, montant


def saisir_operation(operation, valeurs):

    journal = lire_json(FICHIER_JOURNAL)
    numero = obtenir_nouveau_numero()
    ht, tva, ttc = calculer_montants(operation, valeurs)
    nouvelles_ecritures = []

    for ligne in operation["ecritures"]:
        if ligne["montant"] == "HT":
            montant = ht
        elif ligne["montant"] == "TVA":
            montant = tva
        elif ligne["montant"] == "TTC":
            montant = ttc
        else:
            montant = valeurs.get(ligne["montant"], 0)

        nouvelles_ecritures.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "numero": numero,
            "operation": operation["nom"],
            "compte": ligne["compte"],
            "debit": montant if ligne["sens"] == "debit" else 0,
            "credit": montant if ligne["sens"] == "credit" else 0
        })
    journal.extend(nouvelles_ecritures)
    ecrire_json(FICHIER_JOURNAL, journal)


def generer_grand_livre(journal):
    grand_livre = {}
    for e in journal:
        compte = e["compte"]
        if compte not in grand_livre:
            grand_livre[compte] = {"debit": 0, "credit": 0}
        grand_livre[compte]["debit"] += float(e["debit"])
        grand_livre[compte]["credit"] += float(e["credit"])

    return grand_livre