

from ui_advanced_to_normal_form import Ui_Form


from PyQt5.QtWidgets import QWidget, QMessageBox

import utils

def reload_utils():

    from importlib import reload
    global utils
    utils = reload(utils)


from models import AdvancedLinesModel

class Form(Ui_Form, QWidget):
    def __init__(self, parent, view, proforma):
        reload_utils()
        super().__init__()
        self.setupUi(self)
        self.proforma = proforma   

        self.lines_model = AdvancedLinesModel(proforma)
        self.lines_view.setModel(self.lines_model)
        utils.setCommonViewConfig(self.lines_view)

        self.set_header()
        self.set_handlers()




    def set_handlers(self):
        self.lines_view.clicked.connect(self.lines_view_clicked_handler) 
        self.delete_.clicked.connect(self.delete_handler)
        self.update.clicked.connect(self.update_handler) 
        self.save.clicked.connect(self.save_handler)

    def set_header(self):
        self.partner.setText(self.proforma.partner.fiscal_name)
        doc = str(self.proforma.type) + '-' + str(self.proforma.number).zfill(6)
        self.document.setText(doc) 
        self.date.setText(self.proforma.date.strftime('%d/%m/%Y'))
        self.warehouse.setText(self.proforma.warehouse.description)

    def lines_view_clicked_handler(self):
        indexes = self.lines_view.selectedIndexes()
        if not indexes: return
        row = {i.row() for i in indexes}.pop()
        line = self.lines_model.lines[row]
        condition, spec = line.condition, line.spec 
        if line.free_description: return
        self.set_stock_mv(line)


    def update_handler(self):
        print('update')

    def save_handler(self):
        print('save')

    def delete_handler(self):
        print('delete')


    def set_stock_mv(self, line):
        warehouse_id = utils.warehouse_id_map.get(self.warehouse.text())
        condition, spec = line.condition, line.spec 
