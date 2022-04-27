from PyQt5.QtWidgets import QDialog
from ui_trace_form import Ui_Form

from models import find_last_description
from models import ChangeModelTrace
from models import OperationModel

from db import WarehouseChange
from db import SpecChange
from db import ConditionChange


def get_last_description(sn):
    return find_last_description(sn)


class Form(Ui_Form, QDialog):

    def __init__(self, parent):
        super(Form, self).__init__(parent)
        self.setupUi(self)
        self.search_button.clicked.connect(self.search_handler)+
        self.sn.setFocus()

    def search_handler(self):
        sn = self.sn.text()

        self.last_description.setText(get_last_description(sn))
        self.set_models(sn)

    def set_models(self, sn):
        self.wh_view.setModel(ChangeModelTrace(WarehouseChange, sn))
        self.condition_view.setModel(ChangeModelTrace(ConditionChange, sn))
        self.spec_view.setModel(ChangeModelTrace(SpecChange, sn))
        self.trace_view.setModel(OperationModel(sn))
