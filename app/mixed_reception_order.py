
from PyQt5.QtWidgets import QDialog, QMessageBox, QCompleter, QTableView

from PyQt5.QtCore import QStringListModel, Qt, QItemSelectionModel

from ui_mixed_reception_order import Ui_MixedReceptionForm

from models import DefinedDevicesModel, SeriesListModel

import db 

from itertools import chain

class AlreadyProcessedError(BaseException):
    pass 

class ExcessLimitError(BaseException):
    pass 

class Register:
    
    def __init__(self, sn, item, condition, spec, line):
        self.sn = sn
        self.item = item 
        self.condition = condition
        self.spec = spec
        self.line = line 

    def __str__(self):
        return ' '.join([str(type(v)) for v in self.__dict__.values()])
    

class ProcessedDevicesStore:

    def __init__(self, order, editable=False):
        self.container = {}
        self.order = order
        for index, line in enumerate(order.mixed_lines):
            key = (order.mixed_lines[index].description, \
                self.order.mixed_lines[index].condition, \
                    self.order.mixed_lines[index].specification)
            if index == 0:
                self.current_description_key = key # also sets lenght           
            if not editable:
                self.container.setdefault(key, [])
            else:
                self.container[key] = self.buildRegisters(line) 

    def buildRegisters(self, line):
        return [Register(m.sn, str(m.item), m.condition, m.spec, m.line) for m in line.series]

    def __iter__(self):
        return iter(self.container[self.current_description_key])

    def add(self, sn, item, condition, spec, line):
        
        # global check 
        for description_key in self.container:
            for c in self.container[description_key]:
                if c.sn == sn:
                    raise AlreadyProcessedError             
        else:
            if self.current_line_lenght == len(self.container[self.current_description_key]):
                raise ExcessLimitError

            self.container[self.current_description_key].\
                append(Register(sn, item, condition, spec, line)) 
    
    # def print(self):
    #     for key in self.container:
    #         print(key)
    #         for r in self.container[key]:
    #             print(' '*10, end=' ')
    #             print(r)

    def update(self, sn, item, condition, spec, line):
        for key in self.container:
            for r in self.container[key]:
                if r.sn == sn:
                    r.item, r.condition, r.spec, r.line = item, condition, spec, line 
                    break

    def delete(self, sn):
        for key in self.container:
            for i, register in enumerate(self.container[key]):
                if sn == register.sn:
                    del self.container[key][i]

    def set_current_key(self, description_key):
        # Doing this for no breaking the interface exposed to MixedReceptionForm a
        # and keep sync the current_lenght in order to stop adding devices
        for line in self.order.mixed_lines:
            if description_key == (line.description, line.condition, line.specification):
                self.current_line_lenght = line.quantity
                break 
        self._current_description_key = description_key
    
    def delete_all_series(self, sns):
        self.container[self.current_description_key] = \
            [r for r in self.container[self.current_description_key] if r.sn not in sns]


    def get_current_key(self):
        return self._current_description_key

    current_description_key = property(fset=set_current_key, fget=get_current_key)

    def processed_in_line(self):
        return len(self.container[self.current_description_key])

    def total_processed(self):
        return sum(map(len, self.container.values()))

    def get_series_with(self, item, condt, spec):
        return { r.sn for r in self.container[self.current_description_key] if \
            r.item == item and r.condition == condt and r.spec == spec}

class MixedReceptionForm(QDialog, Ui_MixedReceptionForm):

    def __init__(self, parent, order, session):
        super().__init__(parent=parent) 
        self.setupUi(self)
        self.session = session

        self.desc_to_item_id_holder = {str(item):item.id for item in self.session.query(db.Item)}

        self.specs = {r[0] for r in self.session.query(db.PurchaseProformaLine.specification)}.\
            union({r[0] for r in self.session.query(db.SpecificationChange.after)})

        self.conditions = {r[0] for r in self.session.query(db.PurchaseProformaLine.condition)}.\
            union({r[0] for r in self.session.query(db.ConditionChange.after)})


        self.order = order
        self.total_lines = len(order.mixed_lines)
        self.current_index = 0 
        self.processed_store = ProcessedDevicesStore(order) 
        self._set_defined_devices_model() 
        self.next.clicked.connect(self.next_handler)
        self.prev.clicked.connect(self.prev_handler)
        self.commit.clicked.connect(self.commit_handler)
        self.finish.clicked.connect(self.finish_handler)
        self.delete_buttton.clicked.connect(self.delete_handler)
        self.search.clicked.connect(self.search_handler) 
        self.exit.clicked.connect(self.exit_handler) 

        self.populateHeader() 
        self.populateBody() 

        self.view.setSelectionBehavior(QTableView.SelectRows)

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


    def populateHeader(self):
        self.order_number.setText(str(self.order.id).zfill(6))
        self.order_date.setText(self.order.created_on.strftime('%d/%m/%Y'))
        self.partner.setText(self.order.proforma.partner.fiscal_name)
        self.agent.setText(self.order.proforma.agent.fiscal_name)
        self.warehouse.setText(self.order.proforma.warehouse.description)
        self.order_total.setText(str(self._total()))

    def configure_line_fields_and_description_dict(self):
        
        received_description = self.description.text() 
        def filter_func(description_key):
            manufacturer, category, model, *trash = description_key.split(' ')
            return manufacturer in received_description and \
                category in received_description and model in received_description

        self.desc_to_item = {description_key:self.desc_to_item_id_holder[description_key] for \
            description_key in self.desc_to_item_id_holder if filter_func(description_key)}

        c = QCompleter() 
        m = QStringListModel() 
        m.setStringList(self.desc_to_item.keys()) 
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m) 

        self.actual_item.setCompleter(c) 

        received_spec = self.spec.text() 
        if received_spec != 'Mixed':
            self.actual_spec.setText(received_spec)
            self.actual_spec.setReadOnly(True)
        else:
            c = QCompleter() 
            m = QStringListModel()
            m.setStringList(self.specs)
            c.setFilterMode(Qt.MatchContains)
            c.setCaseSensitivity(False)
            c.setModel(m) 
            self.actual_spec.setCompleter(c) 


        # We let this as a point for changing the condition.
        # So we dont apply the logic above
        c = QCompleter() 
        m = QStringListModel()
        m.setStringList(self.conditions)
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m) 
        
        self.actual_condition.setCompleter(c) 


    def populateBody(self):
        self.description.setText(self.order.mixed_lines[self.current_index].description)
        self.line_total.setText(str(self.order.mixed_lines[self.current_index].quantity))
        self.condition.setText(self.order.mixed_lines[self.current_index].condition)
        self.spec.setText(self.order.mixed_lines[self.current_index].specification)
        self.processed.setText(str(self._processed_in_line(self.order.mixed_lines[self.current_index])))
        self.line_number.setText(str(self.current_index + 1) + '/' + str(self.total_lines))
        self.total_processed.setText(str(self._total_processed()))
        self.configure_line_fields_and_description_dict() 

    def _total(self):
        return sum([line.quantity for line in self.order.mixed_lines])    

    def prev_handler(self):
        if self.current_index - 1 == -1:
            self.current_index = self.total_lines - 1
        else:
            self.current_index -= 1
        
        self.populateBody() 
        self.processed_store.current_description_key = \
            (self.order.mixed_lines[self.current_index].description, \
                self.order.mixed_lines[self.current_index].condition, \
                    self.order.mixed_lines[self.current_index].specification) 

        self._set_defined_devices_model() 
        self._refresh_sn_model() 
        self.populateBody() 

    def next_handler(self):
        if self.current_index + 1 == self.total_lines:
            self.current_index = 0
        else:
            self.current_index += 1
        self.populateBody() 
        self.processed_store.current_description_key = \
            (self.order.mixed_lines[self.current_index].description, \
                self.order.mixed_lines[self.current_index].condition, \
                    self.order.mixed_lines[self.current_index].specification) 
        
        self._set_defined_devices_model()
        self._refresh_sn_model()
        self.populateBody() 

    def commit_handler(self):
        try:
            desc = self.actual_item.text()
            self.desc_to_item[desc]
        except KeyError:
            QMessageBox.critical(self, 'Error', 'That item does not exist or correspond')
            return
        else:
            sn = self.sn.text() 
            condition = self.actual_condition.text() 
            spec = self.actual_spec.text() 
            # line = int(self.line_number.text().split('/')[0]) 
            line = self.order.mixed_lines[self.current_index].id 

        if not condition:
            QMessageBox.critical(self, 'Error', 'Condition cannot be empty')
            return 

        if not sn:
            QMessageBox.critical(self, 'Error', 'SN/IMEI cannot be empty')
            return

        if not spec:
            QMessageBox.critical(self, 'Error', 'Spec cannot be empty')
            return 

        try:
            self.processed_store.add(sn, desc, condition, spec, line)
            self.populateBody()
            self._set_defined_devices_model() 
            
        except AlreadyProcessedError:
            if QMessageBox.question(self, 'Update - Device', 'Device already processed. Update it ?', \
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.processed_store.update(sn, desc, condition, spec, line)
                    self._set_defined_devices_model() 
        except ExcessLimitError:
            QMessageBox.critical(self, 'Error', 'You can not add more devices in this line')

        self.sn.setText('')
        self.sn.setFocus()

    def finish_handler(self):
        
        if self._total() != self._total_processed():
            QMessageBox.information(self, 'Information', \
                'You can not finish, there are unproccessed devices')
            return
        try:
            self.defined_devices_model.save()
            QMessageBox.information(self, 'Information', 'Process successfully saved')
            self.close() 
        except:
            QMessageBox.critical(self, 'Error - Update', 'Error saving process')
            raise

    def delete_handler(self):
        if self.all.isChecked():
            try:
                self.processed_store.delete_all_series(list(self.sn_model)) 
                self._refresh_sn_model() 
                self._set_defined_devices_model()
                self.populateBody() 
            except AttributeError:
                return 
            return 

        try:
            row = self.snlist.selectedIndexes()[0].row()
        except IndexError:
            return 
        else:
            sn = self.sn_model[row]
            self.processed_store.delete(sn)
            self.sn_model.delete(sn) 
            self._set_defined_devices_model()
            self.populateBody() 
    
    def search_handler(self):
        sn = self.search_line_edit.text()
        try:
            if sn and sn in self.sn_model:
                index = self.sn_model.indexOf(sn) 
                index = self.snlist.model().index(index)
                self.snlist.selectionModel().setCurrentIndex(index, \
                    QItemSelectionModel.SelectCurrent) 
            else:
                self.snlist.selectionModel().clearSelection() 
        except AttributeError: # Any model defined yet 
            return 

    def _clear_define_device_line_fields(self):
        self.actual_condition.setText('')
        self.actual_item.setText('')
        self.actual_spec.setText('')
        self.sn.setText('')

    def defined_devices_selection_changed(self):
        device = self._get_selected_device() 
        if device:
            item, condt, spec, _ = device 
            self._set_sn_model(item, condt, spec)

    def _get_selected_device(self):
        indexes = self.view.selectedIndexes() 
        try:
            row = {i.row() for i in indexes}.pop() 
        except KeyError:
            self._refresh_sn_model() 
            return 
        return self.defined_devices_model[row]

    def _refresh_sn_model(self):
        self.sn_model = SeriesListModel() 
        self.snlist.setModel(self.sn_model) 

    def _set_sn_model(self, item, condition, spec):
        self.sn_model = SeriesListModel(self.processed_store.get_series_with(item, condition, spec))
        self.snlist.setModel(self.sn_model) 

    def _set_defined_devices_model(self):
        self.defined_devices_model = DefinedDevicesModel(self.processed_store, self)
        self.view.setModel(self.defined_devices_model)
        self.view.selectionModel().selectionChanged.connect(self.defined_devices_selection_changed) 
    
    def _processed_in_line(self, line):
        return self.processed_store.processed_in_line() 

    def _total_processed(self):
        return self.processed_store.total_processed() 


    def exit_handler(self):
        if QMessageBox.question(self, ' Exit ', 'Changes will be lost. Are you sure ?', \
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.close() 



class EditableForm(MixedReceptionForm):

    def __init__(self, parent, order, session):
        super(QDialog, MixedReceptionForm).__init__(self)
        # super().__init__(self, order, session)
        self.setupUi(self) 
        self.processed_store = ProcessedDevicesStore(order, editable=True)
        
        self.session = session

        self.desc_to_item_id_holder = {str(item):item.id for item in self.session.query(db.Item)}

        self.specs = {r[0] for r in self.session.query(db.PurchaseProformaLine.specification)}.\
            union({r[0] for r in self.session.query(db.SpecificationChange.after)})

        self.conditions = {r[0] for r in self.session.query(db.PurchaseProformaLine.condition)}.\
            union({r[0] for r in self.session.query(db.ConditionChange.after)})


        self.order = order
        self.total_lines = len(order.mixed_lines)
        self.current_index = 0 
        self._set_defined_devices_model() 
        self.next.clicked.connect(self.next_handler)
        self.prev.clicked.connect(self.prev_handler)
        self.search.clicked.connect(self.search_handler)

        self.populateHeader() 
        self.populateBody() 

        self.view.setSelectionBehavior(QTableView.SelectRows)

        self.configure_buttons_and_fields() 

    def configure_buttons_and_fields(self):
        self.delete_buttton.setDisabled(True)
        self.commit.setDisabled(True)
        self.finish.setDisabled(True)
        self.all.setDisabled(True)
        self.exit.clicked.connect(lambda : self.close)
        self.sn.setDisabled(True)
        self.actual_condition.setDisabled(True)
        self.actual_spec.setDisabled(True)
        self.actual_item.setDisabled(True)
        self.chance_label.setText('')
