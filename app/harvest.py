from ui_harvevst import Ui_Form

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import Qt



from models import HarvestModel
from utils import parse_date, agent_id_map, partner_id_map, setCompleter
import re

from output import Form as OutputForm

DOC_PATTERN = '^[1-6]\-0*\d+\Z'

class Form(Ui_Form, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.document_model = HarvestModel()
        self.document_view.setModel(self.document_model)

        self.serial_model = HarvestModel()
        self.serial_view.setModel(self.serial_model)

        self.by_serial.toggled.connect(self.by_serial_toggled)
        self.by_document.toggled.connect(self.by_doc_toggled)
        self.by_period.toggled.connect(self.by_period_toggled)

        self.add_document.clicked.connect(self.add_document_handler)
        self.delete_document.clicked.connect(self.delete_document_handler)
        self.add_serial.clicked.connect(self.add_serial_handler)
        self.delete_serial.clicked.connect(self.delete_serial_handler)
        self.calculate.clicked.connect(self.calculate_handler)

        completer = QCompleter(agent_id_map.keys())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.agent.setCompleter(completer)

        setCompleter(self.partner, partner_id_map.keys())

    def by_doc_toggled(self, enable):
        self.by_serial.setEnabled(not enable)
        self.by_period.setEnabled(not enable)

    def by_serial_toggled(self, enable):
        self.by_document.setEnabled(not enable)
        self.by_period.setEnabled(not enable)

    def by_period_toggled(self, enable):
        self.by_document.setEnabled(not enable)
        self.by_serial.setEnabled(not enable)

    def calculate_handler(self):

        if self.by_document.isChecked():
            type_dict = {
                'PurchaseProforma': self.purchase_pi.isChecked(),
                'SaleProforma': self.sales_pi.isChecked(),
                'SaleInvoice': self.sales_invoice.isChecked(),
                'PurchaseInvoice': self.purchase_invoice.isChecked()
            }

            doc_numbers = self.document_model.elements or [] # force emptynesss in any casse

            if not any(type_dict.values()):
                QMessageBox.critical(self, 'Error', 'Choose document type')
                return

            # disable the check 
            # if len(doc_numbers) == 0:
            #     QMessageBox.critical(self, 'Error', 'Enter document numbers')
            #     return

            try:
                year = int(self.year.text())
                
                if not year in range(2000, 2030):
                    QMessageBox.critical(self, 'Error', 'Year must be between 2000 and 2030')
                    return 
                    
            except ValueError:
                QMessageBox.critical(self, 'Error', 'Invalid year')
                return


            OutputForm.by_document(self, type_dict, doc_numbers, 
                partner_id=partner_id_map.get(self.partner.text()), 
                year=year).exec_()

        elif self.by_period.isChecked():
            try:
                _from, to = parse_date(self._from.text()), parse_date(self.to.text())
            except ValueError:
                QMessageBox.critical(self, 'Error', 'Invalid date format')
                return
            else:
                try:
                    agent_id = agent_id_map[self.agent.text()]
                except KeyError:
                    agent_id = None

                OutputForm.by_period(self, _from, to,
                                     _input=self.input.isChecked(),
                                     agent_id=agent_id).exec_()

        elif self.by_serial.isChecked():
            serials = self.serial_model.elements
            if len(serials) == 0:
                QMessageBox.critical(self, 'Error', 'Provide serials')
                return

            OutputForm.by_serials(self, serials).exec_()

    def add_document_handler(self):
        doc = self.document.text()
        if not re.match(DOC_PATTERN, doc):
            QMessageBox.critical(self, 'Error', 'Incorrect document format')
            return

        self.document_model.add(doc)
        self.document.clear()
        self.document.setFocus()

    def delete_document_handler(self):
        if self.delete_all_document.isChecked():
            self.document_model.delete_all()
        else:
            indexes = self.document_view.selectedIndexes()
            self.document_model.delete({index.row() for index in indexes})
        self.document_view.clearSelection()

    def add_serial_handler(self):
        serial = self.serial.text()
        if serial == '':
            return
        self.serial_model.add(serial)
        self.serial.clear()
        self.serial.setFocus()

    def delete_serial_handler(self):
        if self.delete_all_serial.isChecked():
            self.serial_model.delete_all()
        else:
            indexes = self.serial_view.selectedIndexes()
            self.serial_model.delete({index.row() for index in indexes})

        self.serial_view.clearSelection()

