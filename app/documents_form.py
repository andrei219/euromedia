from ui_document_form import Ui_DocumentsForm

from PyQt5.QtWidgets import QDialog

import models


class Form(Ui_DocumentsForm, QDialog):

    def __init__(self, parent, obj):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)
        Model = self.decide_model(obj)
        self.model = Model(obj)
        self.document_view.setModel(self.model)
        self.set_handlers()

    @staticmethod
    def decide_model(obj):
        import db
        cls = obj.__class__
        return {
            db.SaleProforma: models.ProformasSalesDocumentModel,
            db.PurchaseProforma: models.ProformasPurchasesDocumentModel,
            db.Agent: models.AgentsDocumentModel,
            db.Partner: models.PartnersDocumentModel,
            db.SaleInvoice: models.InvoicesSalesDocumentModel,
            db.PurchaseInvoice: models.InvoicesPurchasesDocumentModel
        }.get(cls)

    def set_handlers(self):
        self.add_button.clicked.connect(self.add_handler)
        self.export_button.clicked.connect(self.export_handler)
        self.delete_button.clicked.connect(self.delete_handler)
        self.document_view.doubleClicked.connect(self.view_handler)

    def add_handler(self):
        from utils import get_open_file_path
        file_path = get_open_file_path(self, pdf_filter=True)
        if not file_path:
            return
        try:
            self.model.add(file_path)
        except FileNotFoundError:
            raise

    def export_handler(self):
        from utils import get_directory
        directory = get_directory(self)
        row = self.selected_row

        if row is None:
            return

        self.model.export(directory, row)
        self.document_view.clearSelection()

    @property
    def selected_row(self):
        try:
            return {i.row() for i in self.document_view.selectedIndexes()}.pop()
        except KeyError:
            pass

    def delete_handler(self):
        row = self.selected_row
        if row is None:
            return
        self.model.delete(self.selected_row)
        self.document_view.clearSelection()

    def view_handler(self, index):
        self.model.view(index.row())
        self.document_view.clearSelection()
