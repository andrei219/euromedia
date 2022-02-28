                    
from PyQt5.QtWidgets import QDialog, QMessageBox,\
    QAbstractItemView
from PyQt5.QtCore import QItemSelectionModel

from ui_expedition_form import Ui_ExpeditionForm

from models import (
    SerieModel, 
    sale_total_quantity, 
    sale_total_processed
)

from exceptions import LineCompletedError, SeriePresentError

from sqlalchemy.exc import IntegrityError

from exceptions import NotExistingStockOutput

class Form(Ui_ExpeditionForm, QDialog):

    def __init__(self, parent, expedition):
        super().__init__(parent=parent) 
        self.setupUi(self) 
        self.expedition = expedition
        self.current_index = 0 
        self.total_lines = len(expedition.lines)
        self.parent = parent

        self.next.clicked.connect(self.next_handler) 
        self.prev.clicked.connect(self.prev_handler) 
        self.imei.textChanged.connect(self.input_text_changed)
        self.delete_imei.clicked.connect(self.delete_handler) 
        self.imei.returnPressed.connect(self.serieInput) 


        self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        if expedition.proforma.cancelled:
            self.imei.setEnabled(False)
            self.automatic_input.setEnabled(False) 

        self.set_model(self.expedition.lines[self.current_index])

        self.populateHeader() 
        self.populateBody() 

    def input_text_changed(self, text):
        if self.automatic_input.isChecked():
            lenght = self.lenght.value()
            if len(text) == lenght:
                self.serieInput() 

    def serieInput(self):
        serie = self.imei.text() 
        if not serie:
            return 
        try:
            self.model.add(serie) 
            self.populateBody()
        except SeriePresentError:
            if serie and serie in self.view.model():
                # index_of may return None if serie not found
                # Catch error and ignore it
                index = self.view.model().index_of(serie)
                
                if index is None:
                    mss = ' SN/IMEI: ' + serie
                    mss += ' is already processed in this order'
                    QMessageBox.critical(self, 'Error', mss)
                    self.imei.clear()
                    return 
                
                index = self.view.model().index(index, 0)
                
   
                self.view.selectionModel().setCurrentIndex(
                    index, 
                    QItemSelectionModel.SelectCurrent
                )

        
        except IntegrityError as err:
            QMessageBox.critical(self, 'Error', '[ERROR 1001]:' + str(err))
            return 

        except NotExistingStockOutput:
            mss = 'This SN with this spec or condition is not in Stock. '
            mss += 'May be it is in an overflowed expedition?' 
            QMessageBox.critical(self, 'Error', mss) 
        
        self.imei.clear()


    def invent_series(self):
        try:
            new_processed = int(self.processed_line.text())
            old_processed = self.processed_in_line
            self.model.add_invented(new_processed - old_processed)
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Enter an integer number')
            return 
        except:
            raise 


    def update_overflow_condition(self):
        processed_in_line = self.processed_in_line
        line = self.expedition.lines[self.current_index]
        self.processed_line.setText(str(processed_in_line))
        self.set_overflow(
            processed_in_line > line.quantity
        )

    def set_overflow(self, overflow=False):
        if not overflow:
            self.lines_group.setStyleSheet('')
            self.overflow.setText('')
        else:
            self.lines_group.setStyleSheet('background-color:"#FF7F7F"')
            self.overflow.setText('OVERFLOW')

    def delete_handler(self):
        try:
            if self.all.isChecked():
                self.model.delete_all()
            else:
                indexes = self.view.selectedIndexes()
                if not indexes:return
                self.model.delete(
                    [
                        self.model.series[index.row()]
                        for index in indexes
                    ]
                )
        except:
            raise 
        
        self.populateBody()
        self.populateHeader()

    def populateHeader(self):
        self.imei.setFocus(True)
        self.expedition_number.setText(str(self.expedition.id).zfill(6))
        self.date.setText(str(self.expedition.created_on.strftime('%d/%m/%Y')))
        self.partner.setText(self.expedition.proforma.partner.fiscal_name)
        self.agent.setText(self.expedition.proforma.agent.fiscal_name)
        self.warehouse.setText(self.expedition.proforma.warehouse.description)
        self.expedition_total.setText(str(sale_total_quantity(self.expedition)))

    def populateBody(self):
        self.description.setText(str((self.expedition.lines[self.current_index].item.clean_repr)))
        self.line_total.setText(str(self.expedition.lines[self.current_index].quantity))
        self.condition.setText(self.expedition.lines[self.current_index].condition)
        self.spec.setText(self.expedition.lines[self.current_index].spec) 
        self.showing_condition.setText(self.expedition.lines[self.current_index].showing_condition)

        self.processed_line.setText(str(self.processed_in_line))
        self.number.setText(str(self.current_index + 1) + '/' + str(self.total_lines))
        self.expedition_total_processed.setText(str(sale_total_processed(self.expedition))) 

        import utils 
        serie_state = utils.has_serie(self.expedition.lines[self.current_index])
        self.handle_layout_mode(serie_state)

        self.update_overflow_condition() 


    def handle_layout_mode(self, serie_state):
        for widget in [
            'imei', 'view', 'automatic_input', 
            'delete_imei', 'all', 
        ]:
            getattr(self, widget).setEnabled(serie_state)
        self.processed_line.setReadOnly(not serie_state)

    def next_handler(self):
        if self.current_index + 1 == self.total_lines:
            self.current_index = 0 
        else:
            self.current_index += 1
        self.populateBody() 
        self.set_model(self.expedition.lines[self.current_index])

    def prev_handler(self):
        if self.current_index - 1 == -1:
            self.current_index = self.total_lines - 1
        else:
            self.current_index -= 1
        self.populateBody() 
        self.set_model(self.expedition.lines[self.current_index])

    @property
    def processed_in_line(self):
        return sum(1 for serie in self.expedition.lines[self.current_index].series) 

    def set_model(self, line):
        self.model = SerieModel(line, self.expedition) 
        self.view.setModel(self.model) 

    
    def closeEvent(self, event):
        import db
        for line in self.expedition.lines:
            if line.quantity == len(line.series) == 0:
                db.session.delete(line)

        self.model.commit()
        super().closeEvent(event)        
        self.parent.set_mv('warehouse_expeditions_')  