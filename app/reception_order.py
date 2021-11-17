from itertools import chain

from PyQt5.QtWidgets import QDialog, QMessageBox, QCompleter, QTableView
from PyQt5.QtCore import QStringListModel, Qt, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView
from ui_reception_order import Ui_Form

import models 
import utils 

from utils import setCompleter

from sqlalchemy.exc import IntegrityError

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
        self.rs_model = models.ReceptionSeriesModel(reception) 
        
        self.snlist.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setHandlers()
        self.setCompleters()
        self.populateHeader() 
        self.populate_body()
        
        self.disable_if_cancelled()

        self.total_processed.setText(str(len(self.rs_model)))

        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)


    def disable_if_cancelled(self):
        if self.reception.proforma.cancelled:
            self.commit.setDisabled(True)
            self.automatic.setDisabled(True)


    def setHandlers(self):
        self.next.clicked.connect(self.next_handler)
        self.prev.clicked.connect(self.prev_handler)
        self.commit.clicked.connect(self.commit_handler)
        self.delete_buttton.clicked.connect(self.delete_handler)
        self.search.clicked.connect(self.search_handler) 

    def setCompleters(self):
        conditions = utils.conditions.difference({'Mix'})
        specs = utils.specs.difference({'Mix'})
        for field, data in [
            (self.actual_item, utils.description_id_map.keys()), 
            (self.actual_condition, conditions), 
            (self.actual_spec, specs)
        ]: setCompleter(field, data) 


    def on_automatic_toggled(self, on):
        if on:
            self.commit.setEnabled(False)
            self.sn.textChanged.connect(self.sn_value_changed) 
        else:
            self.commit.setEnabled(True)
            try:
                self.sn.disconnect() 
            except TypeError:
                pass 

    def sn_value_changed(self, text):
        lenght = self.lenght.value()
        if len(text) == lenght:
            self.commit_handler() 
    
    def set_overflow(self, overflow=False):
        if not overflow:
            self.lines_group.setStyleSheet('')
            self.overflow.setText('')
        else:
            self.lines_group.setStyleSheet('background-color:"#FF7F7F"')
            self.overflow.setText('OVERFLOW')


    def populateHeader(self):
        self.reception_number.setText(str(self.reception.id).zfill(6))
        self.date.setText(self.reception.created_on.strftime('%d/%m/%Y'))
        self.partner.setText(self.reception.proforma.partner.fiscal_name)
        self.agent.setText(self.reception.proforma.agent.fiscal_name)
        self.warehouse.setText(self.reception.proforma.warehouse.description)
        self.reception_total.setText(str(self._total()))
    
    def populate_body(self):
        
        line = self.reception.lines[self.current_index]
        if line.description is not None:
            self.description.setText(line.description) 
        else:
            self.description.setText(str(line.item))
            
        self.line_total.setText(str(line.quantity))
        self.condition.setText(line.condition)
        self.spec.setText(line.spec)
        line_number = '/'.join([str(self.current_index + 1),\
            str(self.total_lines)])
        self.line_number.setText(line_number)

        if line.item is None:
            self.actual_item.clear() 
        else:
            self.actual_item.setText(str(line.item))

        if line.condition == 'Mix':
            self.actual_condition.clear()
        else: 
            self.actual_condition.setText(line.condition)

        if line.spec == 'Mix':
            self.actual_spec.clear()
        else:
            self.actual_spec.setText(line.spec)

        self.update_group_model()
        self.update_overflow_condition()

    def processed_in_line(self):
        line = self.reception.lines[self.current_index]
        return self.rs_model.processed_in(line)

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
        if not self.sn.text(): 
            QMessageBox.critical(self, 'Error', 'Empty SN/IMEI')
            return 
        try:
            self.rs_model.add(
                self.reception.lines[self.current_index], 
                self.sn.text(), 
                self.actual_item.text(), 
                self.actual_condition.text(), 
                self.actual_spec.text(), 
            )
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
        except IntegrityError:
            QMessageBox.critical(self, 'Error', 'That Imei/SN already exists')
        else:      
            self.update_group_model()
            self.update_overflow_condition() 
            self.total_processed.setText(str(len(self.rs_model)))

        self.sn.clear()
        self.sn.setFocus()

    def update_group_model(self):
        group_model = models.GroupModel(
            self.rs_model, 
            self.reception.lines[self.current_index]    
        )
        self.view.setModel(group_model)
        self.view.selectionModel().selectionChanged.\
            connect(self.group_selection_changed)
    
    def group_selection_changed(self):
        try:
            description, condition, spec, quantity = \
                self.get_selected_group()
            self.update_series_model(description, condition, spec)
        except ValueError:
            return 
    
    def get_selected_group(self):
        rows = {i.row() for i in self.view.selectedIndexes()}
        if not rows:return
        row = rows.pop()
        group = self.view.model().groups[row]
        return group.description, group.condition, \
            group.spec, group.quantity

    def update_series_model(self, description, condition, spec):
        series_model = models.DefinedSeriesModel(
            self.rs_model, 
            self.reception.lines[self.current_index], 
            description, condition, spec 
        )
        self.snlist.setModel(series_model) 

    def is_mixed_line(self, line):
        if any((
            line.condition == 'Mix', 
            line.spec == 'Mix'
        )): return True 
        if line.item_id is None and \
            line.description in utils.descriptions:
                return True 
        return False

    def delete_handler(self):
        try:
            if self.all.isChecked():
                    self.rs_model.delete(
                        self.snlist.model().series 
                    )
            else:
                indexes = self.snlist.selectedIndexes()
                if not indexes: return
                self.rs_model.delete(
                    [
                        self.snlist.model().series[index.row()]
                        for index in indexes
                    ]
                )
        except:
            raise 

        try:
            description, condition, spec, _ = self.get_selected_group()
            self.last_description, self.last_condition, self.last_spec = \
                description, condition, spec 
        except TypeError:
            description, condition, spec = self.last_description, \
                self.last_condition, self.last_spec

        self.update_overflow_condition()
        self.update_series_model(description, condition, spec)
        self.update_group_model()
        self.total_processed.setText(str(len(self.rs_model)))
        self.all.setChecked(False)

    def update_overflow_condition(self):
        processed_in_line = self.processed_in_line()
        line = self.reception.lines[self.current_index]
        self.processed.setText(str(processed_in_line))
        self.set_overflow(
            processed_in_line > line.quantity
        )


    def search_handler(self):
        serie = self.search_line_edit.text() 
        try:
            if serie and serie in self.snlist.model():
                index = self.snlist.model().index_of(serie)
                index = self.snlist.model().index(index, 0)
                self.snlist.selectionModel().setCurrentIndex(index, \
                    QItemSelectionModel.SelectCurrent)

            else:
                self.snlist.selectionModel().clearSelection()
        except AttributeError: raise  
        except TypeError: raise    
        # If search does not work we dont care


    def closeEvent(self, event):
        import db 
        for line in self.reception.lines:
            if line.quantity == len(line.series) == 0:
                db.session.delete(line)
        try:
            db.session.commit() 
        except:
            db.session.rollback() 
            raise 
        super().closeEvent(event) 