from ui_agents_document_form import Ui_DocumentsForm

from PyQt5.QtWidgets import QDialog

from models import AgentsDocumentModel

class Form(Ui_DocumentsForm, QDialog):

    def __init__(self, parent, agent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)
        self.model = AgentsDocumentModel(agent)
        self.document_view.setModel(self.model)
        self.set_handlers()

    def set_handlers(self):
        pass

    def add_handler(self):
        from utils import get_file_path

        file_path = get_file_path(self, pdf_filter=True)

        try:
            self.model.add(file_path)
        except :
            raise


    def export_handler(self):
        pass

    def delete_handler(self):
        pass

    def view_handler(self):
        pass
