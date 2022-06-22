

from PyQt5.QtWidgets import QDialog

from ui_output import Ui_Dialog

from models import OutputModel


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)
        self._export.clicked.connect(self.export_handler)

    @classmethod
    def by_period(cls, parent, _from, to):
        self = cls(parent)
        self.model = OutputModel.by_period(_from, to)
        self.view.setModel(self.model)
        return self

    @classmethod
    def by_serials(cls, parent, serials):
        self = cls(parent)
        self.model = OutputModel.by_serials(serials)
        self.view.setModel(self.model)
        return self

    @classmethod
    def by_document(cls, parent, type_dict, doc_numbers):
        self = cls(parent)
        self.model = OutputModel.by_document(type_dict, doc_numbers)
        self.view.setModel(self.model)
        return self

    def export_handler(self):
        pass
