from wsgiref import headers
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (Paragraph, SimpleDocTemplate, 
                                Table, TableStyle, Spacer, paragraph)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors


def exporterJournal(cheminFichier, tableView, dateDebut=None, dateFin=None):

    document = SimpleDocTemplate(cheminFichier, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = []

    titre = "Journal de la comptabilité tenu par l'entreprise"
    elements.append(Paragraph(titre, styles['Title']))

    model = tableView.model()

    # En-têtes des colonnes
    headers = [
        str(model.headerData(i, Qt.Horizontal)).upper()
        for i in range(model.columnCount())
    ]

    data = [headers]

    # Contenu des lignes
    for row in range(model.rowCount()):
        ligne = []
        for col in range(model.columnCount()):
            index = model.index(row, col)
            valeur = model.data(index)
            ligne.append(str(valeur) if valeur else "")
        data.append(ligne)

    # Création du tableau
    table = Table(data)

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ])

    table.setStyle(style)

    elements.append(table)

    document.build(elements)

def ajusterColonnesDansTables(listeTables):
    for table in listeTables:
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

def exporterGrandLivre():
    pass
