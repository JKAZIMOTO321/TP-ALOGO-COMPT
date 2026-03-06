import sys
from datetime import datetime
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from openpyxl import Workbook
from PyQt5.QtWidgets import QMessageBox, QFileDialog,QHeaderView
from interface_ui import Ui_MainWindow
from stockage import lire_json
from comptabilite import saisir_operation, generer_grand_livre
from PyQt5.QtWidgets import QLabel, QLineEdit
from export_data import exporterJournal,ajusterColonnesDansTables


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # on force la premiere fenetre a s'ouvrir
        self.ui.stackedWidget.setCurrentIndex(0)
        # mettre la hauteur des champs generes automatiquement
        self.ui.zoneChamps.setMinimumHeight(50) # donner la hauteur automatique des champs

        self.model_journal = QStandardItemModel()
        self.ui.tableView.setModel(self.model_journal)

        # le boutton de filtrage du journal est connecté à la fonction d'affichage du journal qui prend en compte les dates
        self.ui.btnFiltrer.clicked.connect(self.afficher_journal)

        self.inputs_dynamiques = {}


        self.charger_operations_combo()


        self.ui.dateDebut.setDate(QDate(2010, 1, 1))
        self.ui.dateFin.setDate(QDate.currentDate())
        # Navigation
        self.ui.pushButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.pushButton_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.pushButton_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        # pour exporter le journal en excel
        self.ui.pushButton_export.clicked.connect(self.exporter_pdf)

        self.ui.pushButton_4.clicked.connect(self.enregistrer_operation)

        #connecter le combobox des opertions à la génération des champs dynamiques
        self.ui.comboBox.currentIndexChanged.connect(self.generer_champs_dynamiques)

        # Journal
        self.model_journal = QStandardItemModel()
        self.model_journal.setHorizontalHeaderLabels(
            ["Date", "Opération", "Compte", "Débit", "Crédit"]
        )
        self.ui.tableView.setModel(self.model_journal)
        ajusterColonnesDansTables([self.ui.tableView])
        self.afficher_journal()
        self.afficher_grand_livre()

     # Charger opérations dans le comboBox

    def charger_operations_combo(self):
        self.ui.comboBox.clear()
        self.operations = lire_json("operations.json")

        for op in self.operations:
            # texte affiché / donnée interne
            self.ui.comboBox.addItem(op["nom"], op)

    def enregistrer_operation(self):
        op = self.ui.comboBox.currentData()

        if not op:
            return

        valeurs = {}

        for nom_champ, widget in self.inputs_dynamiques.items():  # parcourir les champs dynamiques

            texte = widget.text().strip()  # récupérer et nettoyer le texte

            if not texte:  # si le champ est vide on refuse de continuer
                QMessageBox.warning(self, "Erreur", f"Le champ '{nom_champ}' est obligatoire.")
                return

            try:
                valeurs[nom_champ] = float(texte)
            except ValueError:  # si la conversion échoue, ce n'est pas un nombre valide
                QMessageBox.warning(self, "Erreur", f"Le champ '{nom_champ}' doit être un nombre.")
                return

        saisir_operation(op, valeurs)  # appeler la fonction de comptabilite pour enregistrer l'opération

        self.afficher_journal()  # rafraîchir l'affichage du journal
        self.afficher_grand_livre()  # rafraîchir l'affichage du grand livre
        # pour remettre les champs à zéro après l'enregistrement
        for widget in self.inputs_dynamiques.values():
            widget.clear()


    def afficher_journal(self):

        self.model_journal.clear()
        self.model_journal.setHorizontalHeaderLabels(
            ["Date", "Numéro", "Opération", "Compte", "Débit", "Crédit"]
        )

        journal = lire_json("journal.json")

        # trier le journal par date et numéro pour un affichage cohérent
        # Trier par date croissante
        journal = sorted(
            journal,
            key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d")
        )

        # Convertir en vraies dates Python
        date_debut = self.ui.dateDebut.date().toPyDate()
        date_fin = self.ui.dateFin.date().toPyDate()

        # Sécurité si mauvaise sélection
        if date_fin < date_debut:
            QMessageBox.warning(self, "Erreur", "La date de fin doit être après la date de début.")
            return

        total_debit = 0
        total_credit = 0
        row = 0

        for ecriture in journal:

            try:
                date_ecriture = datetime.strptime(
                    ecriture["date"], "%Y-%m-%d"
                ).date()
            except:
                continue  # ignorer si date invalide

            if date_debut <= date_ecriture <= date_fin:

                self.model_journal.setItem(row, 0, QStandardItem(ecriture["date"]))
                self.model_journal.setItem(row, 1, QStandardItem(str(ecriture.get("numero", ""))))
                self.model_journal.setItem(row, 2, QStandardItem(ecriture["operation"]))
                self.model_journal.setItem(row, 3, QStandardItem(ecriture["compte"]))
                self.model_journal.setItem(row, 4, QStandardItem(str(ecriture["debit"])))
                self.model_journal.setItem(row, 5, QStandardItem(str(ecriture["credit"])))

                total_debit += float(ecriture["debit"])
                total_credit += float(ecriture["credit"])

                row += 1

        # calculer les totaux et vérifier l'équilibre
        # Ajouter ligne TOTAL après calcul
        
        self.model_journal.setItem(row, 0, QStandardItem(""))
        self.model_journal.setItem(row, 1, QStandardItem(""))
        self.model_journal.setItem(row, 2, QStandardItem("TOTAL"))
        self.model_journal.setItem(row, 3, QStandardItem(""))
        self.model_journal.setItem(row, 4, QStandardItem(str(total_debit)))
        self.model_journal.setItem(row, 5, QStandardItem(str(total_credit)))

        if total_debit != total_credit:
            QMessageBox.warning(
                self,
                "Erreur Comptable",
                f"Déséquilibre détecté !\nDébit: {total_debit}\nCrédit: {total_credit}"
            )

    def afficher_grand_livre(self):
        grand_livre = generer_grand_livre(lire_json("journal.json"))
        texte = ""
        for c, v in grand_livre.items():
            solde = v["debit"] - v["credit"]
            texte += f"Compte {c}\nDébit: {v['debit']}  |  Crédit: {v['credit']} |  Solde: {solde}\n\n"
        self.ui.plainTextEdit.setPlainText(texte)

    def generer_champs_dynamiques(self):

        layout = self.ui.zoneChamps.layout()

        # une petite securite
        if layout is None:
            return

        # Supprimer anciens champs
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        op = self.ui.comboBox.currentData()

        if not op:
            return

        self.inputs_dynamiques = {}

        for champ in op["champs"]:

            label = QLabel(champ.replace("_", " ").capitalize())
            line = QLineEdit()

            layout.addWidget(label)
            layout.addWidget(line)
            line.setMinimumHeight(30)
            line.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    border: 2px solid #a7c6ff;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 14px;
                }

                QLineEdit:focus {
                    border: 2px solid #090b41;
                }
            """)


            self.inputs_dynamiques[champ] = line
    def exporter_excel(self):

        journal = lire_json("journal.json")

        if not journal:
            QMessageBox.warning(self, "Erreur", "Le journal est vide.")
            return

        fichier, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le fichier Excel",
            "journal.xlsx",
            "Fichiers Excel (*.xlsx)"
        )

        if not fichier:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Journal"

        # En-têtes
        ws.append(["Date", "Opération", "Compte", "Débit", "Crédit"])

        total_debit = 0
        total_credit = 0

        for e in journal:
            ws.append([e["date"], e["operation"], e["compte"], e["debit"], e["credit"]])
            total_debit += e["debit"]
            total_credit += e["credit"]

        # Ligne total
        ws.append(["", "", "TOTAL", total_debit, total_credit])

        wb.save(fichier)

        QMessageBox.information(self, "Succès", "Export Excel réussi.")
    
    def exporter_pdf(self):
        chemin_fichier, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier PDF", "", "Fichiers PDF (*.pdf)")
        try:
            exporterJournal(cheminFichier=chemin_fichier,tableView=self.ui.tableView)
            QMessageBox.information(self, "Succès", "Enregistrement du PDF réussi.")
        except Exception as e:
            QMessageBox.warning(self, "Attention", f"Erreur lors de l'enregistrement:{e}")
            print(e)

    # la focnction qui actualise le journal et remet les dates à leur valeur par défaut après l'enregistrement d'une opération
    def actualiser_journal(self):
        # remettre les dates par défaut
        self.ui.dateDebut.setDate(QDate(2010, 1, 1))
        self.ui.dateFin.setDate(QDate.currentDate())

        # rafraîchir affichage
        self.afficher_journal()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
