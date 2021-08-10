
import os 

from ui_document_form import Ui_DocumentsForm
from PyQt5.QtWidgets import QDialog, QMessageBox


import db, utils

from models import DocumentModel

class DocumentForm(Ui_DocumentsForm, QDialog):
    
    def __init__(self, parent, key, value, sqlalchemyParentClass, sqlAlchemyChildClass):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.document_view.setModel(DocumentModel(key, value, sqlAlchemyChildClass, sqlalchemyParentClass)) 
        
        self.export_button.clicked.connect(self.export)
        self.add_button.clicked.connect(self.add)
        self.delete_button.clicked.connect(self.delete)
        self.document_view.doubleClicked.connect(self.viewPdf) 

    def viewPdf(self, index):
        pass   

    def export(self):
        indexes = self.document_view.selectedIndexes() 
        if indexes:
            index = indexes[0]
            filename = self.document_view.model().data(index)
            abs_filepath_and_extension = utils.askSaveFile(self, filename)
            abs_filepath = abs_filepath_and_extension[0]
            if abs_filepath:
                document = self.document_view.model().documents[index.row()]
                utils.writeBase64Pdf(abs_filepath, document.document)

    def add(self):
        abs_filepath_and_extension = utils.askFilePath(self)
        abs_filepath = abs_filepath_and_extension[0]
        if abs_filepath:
            abs_filepath = abs_filepath_and_extension[0]
            _, filename = os.path.split(abs_filepath)
            try:
                self.document_view.model().add(filename, utils.base64Pdf(abs_filepath))
            except:
                raise
                QMessageBox.critical(self, 'Error', 'Error adding docuemnt')

    def delete(self):
        indexes = self.document_view.selectedIndexes()
        if indexes:
            try:
                self.document_view.model().delete(indexes[0])
                self.document_view.clearSelection() 
            except:
                QMessageBox.critical(self, 'Delete - Error', 'Error deleting document')
