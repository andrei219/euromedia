from itertools import chain

from PyQt5.QtWidgets import QDialog, QMessageBox, QCompleter, QTableView
from PyQt5.QtCore import QStringListModel, Qt, QItemSelectionModel

from ui_reception_order import Ui_Form

import models 

from utils import setCompleter

class AlreadyProcessedError(BaseException):
    pass 

class ExcessLimitError(BaseException):
    pass 

class Form(QDialog, Ui_Form):

    def __init__(self, parent, reception):
        super().__init__(parent=parent) 
        self.setupUi(self)

        self.reception = reception
        self.total_lines = len(reception.lines) 
        self.current_index = 0 
        
        self.setHandlers()
        self.setCompleters()
        self.populateHeader() 
        self.populate_body()
        
        self.view.setSelectionBehavior(QTableView.SelectRows)

    def setHandlers(self):
        self.next.clicked.connect(self.next_handler)
        self.prev.clicked.connect(self.prev_handler)
        self.commit.clicked.connect(self.commit_handler)
        self.delete_buttton.clicked.connect(self.delete_handler)
        self.search.clicked.connect(self.search_handler) 

    def setCompleters(self):
        conditions = models.conditions.difference({'Mix'})
        specs = models.specs.difference({'Mix'})
        for field, data in [
            (self.actual_item, models.description_id_map.keys()), 
            (self.actual_condition, conditions), 
            (self.actual_spec, specs)
        ]: setCompleter(field, data) 


    def on_automatic_toggled(self, on):
        pass

    def populateHeader(self):
        self.reception_number.setText(str(self.reception.id).zfill(6))
        self.date.setText(self.reception.created_on.strftime('%d/%m/%Y'))
        self.partner.setText(self.reception.proforma.partner.fiscal_name)
        self.agent.setText(self.reception.proforma.agent.fiscal_name)
        self.warehouse.setText(self.reception.proforma.warehouse.description)
        self.reception_total.setText(str(self._total()))
    
    def populate_body(self):
        
        line = self.reception.lines[self.current_index]
        if self.current_line_is_mixed():
            self.description.setText(line.description) 
        else:
            self.description.setText(str(line.item))

        self.line_total.setText(str(line.quantity))
        self.condition.setText(line.condition)
        self.spec.setText(line.spec)
        line_number = '/'.join([str(self.current_index + 1),\
            str(self.total_lines)])
        self.line_number.setText(line_number)

    def set_series_model(self):
        self.series_model = models.ReceptionSeriesModel

    def _total(self):
        return sum([line.quantity for line in self.reception.lines])
 
    def prev_handler(self):
        if self.current_index - 1 == -1:
            self.current_index = self.total_lines - 1
        else:
            self.current_index -= 1
        self.populate_body()

    def next_handler(self):
        if self.current_index + 1 == self.total_lines:
            self.current_index = 0
        else:
            self.current_index += 1
        self.populate_body()

    def commit_handler(self):
        pass 

    def delete_handler(self):
        ixs = self.snlist.selectedIndexes()
        if not ixs:
           return
        row = {i.row() for i in ixs}
        
    
    def search_handler(self):
        pass 
    
    def current_line_is_mixed(self):
        line = self.reception.lines[self.current_index]
        return line.description is not None or \
            line.condition == 'Mix' or line.spec == 'Mix'
    
 



































# class EditableForm(Form):

#     def __init__(self, parent, order):
#         super(QDialog, MixedReceptionForm).__init__(self)
#         self.setupUi(self) 
#         self.processed_store = ProcessedDevicesStore(order, editable=True)
        

#         self.desc_to_item_id_holder = {str(item):item.id for item in db.session.query(db.Item)}

#         self.specs = {r[0] for r in db.session.query(db.PurchaseProformaLine.specification)}.\
#             union({r[0] for r in db.session.query(db.SpecificationChange.after)})

#         self.conditions = {r[0] for r in db.session.query(db.PurchaseProformaLine.condition)}.\
#             union({r[0] for r in db.session.query(db.ConditionChange.after)})


#         self.order = order
#         self.total_lines = len(order.mixed_lines)
#         self.current_index = 0 
#         self._set_defined_devices_model() 
#         self.next.clicked.connect(self.next_handler)
#         self.prev.clicked.connect(self.prev_handler)
#         self.search.clicked.connect(self.search_handler)

#         self.populateHeader() 
#         self.populateBody() 

#         self.view.setSelectionBehavior(QTableView.SelectRows)

#         self.configure_buttons_and_fields() 

#     def configure_buttons_and_fields(self):
#         self.delete_buttton.setDisabled(True)
#         self.commit.setDisabled(True)
#         self.finish.setDisabled(True)
#         self.all.setDisabled(True)
#         self.exit.clicked.connect(lambda : self.close())
#         self.sn.setDisabled(True)
#         self.actual_condition.setDisabled(True)
#         self.actual_spec.setDisabled(True)
#         self.actual_item.setDisabled(True)
#         self.chance_label.setText('')
