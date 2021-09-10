                    
from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_order_form import Ui_OrderForm

from models import SerieModel

from exceptions import LineCompletedError, SeriePresentError

from sqlalchemy.exc import IntegrityError

from exceptions import NotExistingStockOutput

class OrderForm(Ui_OrderForm, QDialog):

    def __init__(self, parent, order, session, sale=False):
        super().__init__(parent=parent) 
        self.setupUi(self) 
        self.order = order
        self.session = session
        self.current_index = 0 
        self.total_lines = len(order.lines)
        self.sale = sale 

        self.next_line_tool_button.clicked.connect(self.next) 
        self.prev_line_button.clicked.connect(self.prev) 
        self.imei_line_edit.textChanged.connect(self.input_text_changed)
        
        if self.order.proforma.cancelled:
            self.imei_line_edit.returnPressed.connect(self.alertNoInputCancelled) 
        else:
            self.imei_line_edit.returnPressed.connect(self.serieInput) 
        self.delete_imei_tool_button.clicked.connect(self.delete) 

        self._setModel(self.order.lines[self.current_index])

        if self.sale:
            self.setWindowTitle('Expedition')
        else:
            self.setWindowTitle('Reception')


        self.populateHeader() 
        self.populateBody() 



    def input_text_changed(self, text):
        if self.automatic_input.isChecked():
            lenght = self.lenght.value()
            if len(text) == lenght:
                self.serieInput() 

    def alertNoInputCancelled(self):
        QMessageBox.critical(self, 'Update - Error', "Can't add SN/Imei to canelled order. Only remove")

    def serieInput(self):
        line = self.order.lines[self.current_index]
        serie = self.imei_line_edit.text() 
        if not serie:
            return 
        try:
            self.model.add(line, serie) 
            self.populateBody()
        except SeriePresentError:
            QMessageBox.critical(self, 'Update - Error', f'Serie {serie} already present')
        except LineCompletedError:
            QMessageBox.critical(self, 'Update - Error', 'Line completed! Switch to next')
        except IntegrityError as err:
            if err.orig.args[0] == 1062:
                s = f"""
                    IMEI/SN: {serie} exists as physical stock.You have received it two times without selling it first.
                    The same sn/imeis were processed in two different reception orders. 
                """
                QMessageBox.critical(self, 'Update - Error', s)
                return
        except NotExistingStockOutput:
            QMessageBox.critical(self, 'Error', 'This SN is not in physical stock')
            return

        self.imei_line_edit.setText('')

    def delete(self):
        indexes = self.view.selectedIndexes() 
        if not indexes:
            return
        try:
            self.model.delete(indexes[0])
            self.populateBody() 
            self.view.clearSelection() 
        except NotExistingStockOutput:
            QMessageBox.critical(self, 'Error', 'This SN is not in physical stock.May be you changed condition or spec')
            return
        except:
            raise 

    def populateHeader(self):
        self.order_number_line_edit.setText(str(self.order.id).zfill(6))
        self.order_date_line_edit.setText(str(self.order.created_on.strftime('%d/%m/%Y')))
        self.partner_line_edit.setText(self.order.proforma.partner.fiscal_name)
        self.agent_line_edit.setText(self.order.proforma.agent.fiscal_name)
        self.warehouse_line_edit.setText(self.order.proforma.warehouse.description)
        self.order_total_line_edit.setText(str(self._total()))

    def populateBody(self):
        self.description_line_edit.setText(self._buildDescription(self.order.lines[self.current_index].item))
        self.line_total_line_edit.setText(str(self.order.lines[self.current_index].quantity))
        self.condition_line_edit.setText(self.order.lines[self.current_index].condition)
        self.spec_line_edit.setText(self.order.lines[self.current_index].specification) 
        self.processed_line_edit.setText(str(self._processed(self.order.lines[self.current_index])))
        self.number_line_edit.setText(str(self.current_index + 1) + '/' + str(self.total_lines))
        self.total_processed_line_edit.setText(str(self._totalProcessed()))

    def next(self):
        if self.current_index + 1 == self.total_lines:
            self.current_index = 0 
        else:
            self.current_index += 1
        self.populateBody() 
        self._setModel(self.order.lines[self.current_index])

    def prev(self):
        if self.current_index - 1 == -1:
            self.current_index = self.total_lines - 1
        else:
            self.current_index -= 1
        self.populateBody() 
        self._setModel(self.order.lines[self.current_index])

    def _buildDescription(self, item):
        return ' '.join([item.manufacturer, item.model, str(item.capacity), 'GB', item.color]) 
    
    def _total(self):
        return sum([line.quantity for line in self.order.lines])

    def _processed(self, line):
        return sum([1 for serie in line.series]) or 0 

    def _totalProcessed(self):
        processed = 0
        for line in self.order.lines:
            for serie in line.series:
                processed += 1 
        return processed

    def _setModel(self, line):
        self.model = SerieModel(self.session, line, self.order, self.sale) 
        self.view.setModel(self.model) 