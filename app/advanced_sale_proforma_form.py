from datetime import date

from PyQt5.QtWidgets import QWidget, QMessageBox

import db
import utils

from db import Agent, Partner
from models import (
    AdvancedLinesModel,
    IncomingStockModel,
    computeCreditAvailable,
    sale_proforma_next_number,
    update_sale_warehouse
)
from sale_proforma_form import Form
from ui_advanced_sale_proforma_form import Ui_Form
from utils import setCommonViewConfig


MESSAGE = "This presale is only for incoming stock \n {}. For others stocks create new presale"

from sqlalchemy.exc import IntegrityError

def reload_utils():
    global utils
    from importlib import reload
    utils = reload(utils)

class Form(Ui_Form, QWidget):
    def __init__(self, parent, view):
        self.stock_model = None
        reload_utils()
        super().__init__()
        self.setupUi(self)
        setCommonViewConfig(self.stock_view)
        self.model = view.model()
        self.init_template()
        self.parent = parent
        self.lines_model = AdvancedLinesModel(self.proforma, self)
        self.lines_view.setModel(self.lines_model)

        self.set_combos()
        self.set_completers()
        self.set_handlers()

        self.type_filter = None
        self.number_filter = None


    def init_template(self):
        self.proforma = db.SaleProforma()
        db.session.add(self.proforma)
        db.session.flush()
        self.date.setText(date.today().strftime('%d%m%Y'))
        self.type.setCurrentText('1')
        self.number.setText(str(sale_proforma_next_number(1)).zfill(6))

    def set_handlers(self):
        self.partner.returnPressed.connect(self.partner_search)
        self.delete_.clicked.connect(self.delete_handler)
        self.add.clicked.connect(self.add_handler)
        self.save.clicked.connect(self.save_handler)
        self.insert.clicked.connect(self.insert_handler)
        self.type.currentTextChanged.connect(self.type_changed)
        self.search.clicked.connect(self.search_handler)
        self.warehouse.currentTextChanged.connect(self.warehouse_handler)

    def set_combos(self):
        for combo, data in [
            (self.agent, utils.agent_id_map.keys()),
            (self.warehouse, utils.warehouse_id_map.keys()),
            (self.courier, utils.courier_id_map.keys())
        ]:
            combo.addItems(data)

    def set_completers(self):
        for field, data in [
            (self.partner, utils.partner_id_map.keys()),
            (self.description, utils.descriptions),
            (self.spec, utils.specs),
            (self.condition, utils.conditions)
        ]: utils.setCompleter(field, data)

    def proforma_to_form(self):
        p = self.proforma
        self.type.setCurrentText(str(p.type))
        self.number.setText(str(p.number))
        self.date.setText(str(p.date.strftime('%d%m%Y')))
        self.partner.setText(p.partner_name)
        self.agent.setCurrentText(p.agent.fiscal_name)
        self.warehouse.setCurrentText(p.warehouse.description)
        self.courier.setCurrentText(p.courier.description)
        self.incoterms.setCurrentText(p.incoterm)
        self.warranty.setValue(p.warranty)
        self.days.setValue(p.credit_days)
        self.eur.setChecked(p.eur_currency)
        self.credit.setValue(p.credit_amount)
        self.tracking.setText(p.tracking)
        self.they_pay_we_ship.setChecked(p.they_pay_we_ship)
        self.they_pay_they_ship.setChecked(p.they_pay_they_ship)
        self.we_pay_we_ship.setChecked(p.we_pay_we_ship)
        self.note.setText(p.note)
        self.external.setText(p.external)

    def set_stock_mv(self):
        warehouse_id = utils.warehouse_id_map.get(
            self.warehouse.currentText()
        )

        description = self.description.text()
        condition = self.condition.text()
        spec = self.spec.text()

        if spec == 'Mix' or not spec:
            spec = None
        if condition == 'Mix' or not condition:
            condition = None

        self.stock_model = IncomingStockModel(
            warehouse_id,
            description=description,
            condition=condition,
            spec=spec,
            type=self.type_filter,
            number=self.number_filter

        )

        self.stock_view.setModel(self.stock_model)

    def search_handler(self):
        self.set_stock_mv()

    def warehouse_handler(self):

        try:
            self.stock_model.reset()
            self.lines_model.reset()
        except AttributeError:
            pass

        self.update_totals()
        # removing objects in pending state 
        db.session.rollback()

    def update_totals(self, note=0.0):
        self.total.setText(str(self.proforma.total_debt))
        self.ptax.setText(str(self.proforma.tax))
        self.cn.setText(str(self.proforma.cn_total))
        self.pending.setText(str(self.proforma.total_debt - self.proforma.total_paid))
        self.subtotal.setText(str(self.proforma.subtotal))
        self.quantity_label.setText('Qnt.: ' + str(self.lines_model.quantity))

    def set_stock_message(self, empty=False):
        if empty:
            self.stock_message.setText('')
            self.stock_message.setStyleSheet('')
        else:
            s = str(self.type_filter) + '-' + str(self.number_filter).zfill(6)
            self.stock_message.setText(MESSAGE.format(s))
            self.stock_message.setStyleSheet('background-color:"#FF7F7F"')

    def delete_handler(self):
        indexes = self.lines_view.selectedIndexes()
        if not indexes:
            return
        row = {index.row() for index in indexes}.pop()
        self.lines_model.delete(row)
        self.lines_view.clearSelection()
        self.set_stock_message(empty=not self.lines_model)
        self.update_global_filters()
        self.set_stock_mv()
        self.update_totals()

    def add_handler(self):
        if not hasattr(self, 'stock_model'):
            return
        indexes = self.stock_view.selectedIndexes()
        if not indexes:
            return
        row = {i.row() for i in indexes}.pop()
        vector = self.stock_model[row]

        quantity = self.quantity.value()
        if quantity > vector.available:
            QMessageBox.critical(
                self,
                'Error',
                'quantity must be less than available'
            )
            return

        price = self.price.value()
        ignore = self.ignore.isChecked()
        tax = int(self.tax.currentText())
        showing = self.showing_condition.text()

        try:
            self.lines_model.add(quantity, price, ignore, tax, showing, vector)
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
            raise
        else:
            self.update_totals()

            # set filters before compute stocks:
            self.update_global_filters(vector=vector)

            self.set_stock_mv()
            self.set_stock_message()

    def update_global_filters(self, vector=None):
        if vector:
            self.type_filter = vector.type
            self.number_filter = vector.number
        else:
            self.type_filter = None
            self.number_filter = None

    def partner_search(self):
        partner_id = utils.partner_id_map.get(self.partner.text())
        if not partner_id:
            return
        try:
            available_credit = computeCreditAvailable(partner_id)
            self.available_credit.setValue(float(available_credit))
            self.credit.setMaximum(float(available_credit))

        except TypeError:
            raise

        result = db.session.query(Agent.fiscal_name,
                                  Partner.warranty, Partner.euro, Partner.they_pay_they_ship,
                                  Partner.they_pay_we_ship, Partner.we_pay_we_ship,
                                  Partner.days_credit_limit).join(Agent)\
            .where(Partner.id == partner_id).one()

        agent, warranty, euro, they_pay_they_ship, they_pay_we_ship, we_pay_we_ship, days = \
            result

        self.agent.setCurrentText(agent)
        self.warranty.setValue(warranty)
        self.eur.setChecked(euro)
        self.they_pay_they_ship.setChecked(they_pay_they_ship)
        self.they_pay_we_ship.setChecked(they_pay_we_ship)
        self.we_pay_we_ship.setChecked(we_pay_we_ship)

    def insert_handler(self):
        from free_line_form import Dialog
        dialog = Dialog(self)
        if dialog.exec_():
            try:
                description = dialog.description.text()
                if not description:
                    return

                self.lines_model.insert_free(
                    description,
                    dialog.quantity.value(),
                    dialog.price.value(),
                    int(dialog.tax.currentText())
                )
            except:
                QMessageBox.critical(self, 'Error', 'Error adding free line')
                raise

    def type_changed(self, type):
        next_num = sale_proforma_next_number(int(type))
        self.number.setText(str(next_num).zfill(6))

    def save_handler(self):
        if not self._valid_header():
            return
        if not self.lines_model:
            QMessageBox.critical(self, 'Error', "Can't process empty proforma")
            return

        # warehouse_id = utils.warehouse_id_map.get(self.warehouse.currentText())
        # warehouse_id = self.proforma.warehouse_id
        # lines = self.lines_model.lines
        # if self.stock_model is not None:
        #     if self.stock_model.lines_against_stock(warehouse_id, lines):
        #         QMessageBox.critical(self, 'Error', 'Someone took those incoming stocks. Start again.')
        #         self.close()

        self._form_to_proforma()
        try:
            self.save_template()
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            QMessageBox.critical(self, 'Error', 'Document with that type and number already exists')
        else:
            QMessageBox.information(self, 'Success', 'Sale saved successfully')
            self.close()

    def save_template(self):
        self.model.add(self.proforma)
        self.proforma.advanced_lines.extend(self.lines_model.lines)

    def _valid_header(self):
        try:
            utils.partner_id_map[self.partner.text()]
        except KeyError:
            QMessageBox.critical(self, 'Update - Error', 'Invalid Partner')
            return False
        try:
            utils.parse_date(self.date.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in date field. Format: ddmmyyyy')
            return False
        return True

    def closeEvent(self, event):
        db.session.rollback()

    def _form_to_proforma(self):

        self.proforma.type = int(self.type.currentText())
        self.proforma.number = int(self.number.text())
        self.proforma.date = utils.parse_date(self.date.text())
        self.proforma.warranty = self.warranty.value()
        self.proforma.they_pay_they_ship = self.they_pay_they_ship.isChecked()
        self.proforma.they_pay_we_ship = self.they_pay_we_ship.isChecked()
        self.proforma.we_pay_we_ship = self.we_pay_we_ship.isChecked()
        self.proforma.agent_id = utils.agent_id_map[self.agent.currentText()]
        self.proforma.partner_id = utils.partner_id_map[self.partner.text()]
        self.proforma.warehouse_id = utils.warehouse_id_map[self.warehouse.currentText()]
        self.proforma.courier_id = utils.courier_id_map[self.courier.currentText()]
        self.proforma.eur_currency = self.eur.isChecked()
        self.proforma.credit_amount = self.credit.value()
        self.proforma.credit_days = self.days.value()
        self.proforma.incoterm = self.incoterms.currentText()
        self.proforma.tracking = self.tracking.text()
        self.proforma.note = self.note.toPlainText()[0:255]
        self.proforma.external = self.external.text()

    def clear_filters(self):
        self.description.clear()
        self.spec.clear()
        self.condition.clear()


class EditableForm(Form):

    def __init__(self, parent, view, proforma):
        reload_utils()
        self.proforma = proforma
        super().__init__(parent, view)
        self.update_totals()
        self.proforma_to_form()
        self.warehouse.setEnabled(False)
        self.disable_if_cancelled()
        self.set_stock_message(empty=not self.lines_model)

    def init_template(self):
        # This method is empty but is part of the template pattern
        # The behaviour in this specific class is to do nothing
        # but if omitted, method in the superclass
        # is executed causing the replacing of this already existing
        # Proforma object with a new one populated with Nones
        # and raising AttributeErrors
        pass


    def save_template(self):
        update_sale_warehouse(self.proforma)

    def disable_if_cancelled(self):
        if self.proforma.cancelled:
            self.delete_.setEnabled(False)
            self.header.setEnabled(False)
            self.create_line.setEnabled(False)
            self.search.setEnabled(False)
            self.insert.setEnabled(False)
            self.add.setEnabled(False)
            self.save.setEnabled(False)


def get_form(parent, view, proforma=None,):
    return EditableForm(parent, view, proforma) if proforma else Form(parent, view)
