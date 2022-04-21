


from PyQt5.QtWidgets import QDialog, QMessageBox, QTableView

from PyQt5.QtCore import Qt

from ui_change_form import Ui_ChangeForm


from models import ChangeModel 


# Con hint se decide:
#   orm class
#   attribute from imeis
#   header name 

from models import ChangeModel
from db import Spec, Condition, Warehouse


import utils

class ChangeForm(Ui_ChangeForm, QDialog):
    
    def __init__(self, parent, hint=None):
        super().__init__(parent)

        self.setupUi(self) 
        
        from importlib import reload
        global utils
        utils = reload(utils)

        self.attr_name = 'description'
        self.model = ChangeModel(hint=hint) 
        self.view.setModel(self.model)
        self.hint = hint 
        self.sn.returnPressed.connect(self.sn_handler) 
        self.apply.clicked.connect(self.apply_handler)

        self.set_completers()

        utils.setCommonViewConfig(self.view)

    def set_completers(self):
        if self.hint == 'warehouse':
            utils.setCompleter(self.new_, utils.warehouse_id_map.keys())
        elif self.hint == 'spec':
            utils.setCompleter(self.new_, utils.specs)
        elif self.hint == 'condition':
            utils.setCompleter(self.new_, utils.conditions)


    def apply_handler(self):
        name = self.new_.text().strip()
        comment = self.comment.text()[:50]
        try:
            self.model.apply(name, comment)
        except:
            raise 

    def sn_handler(self):
        sn = self.sn.text() 

        if not sn:
            return 
            
        try:
            self.model.search(sn)
            self.view.resizeColumnToContents(1)
        except:
            raise 


        self.sn.clear()


