

from PyQt5.QtWidgets import QMainWindow, QTableView, QMessageBox, QInputDialog

from PyQt5 import QtCore

from ui_maingui import Ui_MainGui

import models 
  
import agentgui, partner_form, product_form, purchase_proforma_form, payments_form, expenses_form, \
    document_form, expedition_form, sale_proforma_form, inventory_form, spec_change_form, condition_change_form, \
        warehouse_change_form, reception_order

from sqlalchemy.exc import IntegrityError

from utils import washDict, setCommonViewConfig, getPassword, getTracking, getNote

from db import PurchaseProforma, PurchaseDocument, SaleDocument, SaleProforma

PASSWORD = '0010'

PREFIXES = [
    'agents_', 
    'partners_', 
    'proformas_purchases_', 
    'proformas_sales_', 
    'invoices_purchases_', 
    'invoices_sales_', 
    'warehouse_expeditions_', 
    'warehouse_receptions_'
]

ACTIONS = [
    'apply', 
    'new', 
    'edit', 
    'delete', 
    'cancel', 
    'print', 
    'pdf', 
    'payments', 
    'expenses', 
    'docs', 
    'toinv', 
    'towh', 
    'ship', 
    'newadv', 
    'mail', 
    'options', 
    'process', 
    'double_click', 
    'search'
]

class MainGui(Ui_MainGui, QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setCentralWidget(self.main_tab)

        # For closing 
        self.opened_windows_instances = set() 
        # Prevent creating multiple
        self.opened_windows_classes = set() 
        
        self.set_handlers()
        
        self.init_models() 
        # self.main_tab.currentChanged.connect(self.tabChanged)


    def init_models(self):
        for prefix in PREFIXES:
            self.set_mv(prefix)

    def set_mv(self, prefix, search_key=None, filters=None):
        from utils import setCommonViewConfig
        if prefix == 'proformas_purchases_':
            self.proformas_purchases_model = \
                models.PurchaseProformaModel(filters=filters, search_key=search_key)
            self.proformas_purchases_view.setModel(
                self.proformas_purchases_model
            )
            self.proformas_purchases_view.setSelectionBehavior(QTableView.SelectRows)

        elif prefix == 'proformas_sales_':
            self.proformas_sales_model = \
                models.SaleProformaModel(filters=filters, search_key=search_key)
        
        elif prefix == 'agents_':
            self.agents_model = models.AgentModel(search_key=search_key)
            self.agents_view.setModel(self.agents_model) 
            setCommonViewConfig(self.agents_view)
        

    def set_handlers(self):
        for prefix in PREFIXES:
            for action in ACTIONS:
                try:
                    widget_name = prefix + action
                    self.attach_handler(prefix, action)
                except AttributeError:
                    continue 

    def attach_handler(self, prefix, action):
        try:
            handler = getattr(self, prefix + action + '_handler') 
            if action == 'double_click':
                widget = getattr(self, prefix + 'view')
                widget.doubleClicked.connect(handler) 
            elif action == 'search':
                widget = getattr(self, prefix + action)
                widget.returnPressed.connect(handler)
            else:
                widget = getattr(self, prefix + action)
                widget.clicked.connect(handler) 
        except AttributeError:
            raise         

    def get_filters(self,*, prefix):
        filters = {}
        for name in [
            'types', 'financial', 'shipment', 
            'logistic', 'cancelled'
        ]:
            try:
                filters[name] = getattr(self, name)(prefix=prefix)
            except AttributeError:
                continue
        return filters

    def cancelled(self, prefix):
        return [
            name for name in (
                'cancelled', 'notcancelled'
            ) if getattr(self, prefix + name).isChecked()
        ]

    def types(self, *, prefix):
        return [
            i for i in range(1, 7)
            if getattr(self, prefix + 'serie' + str(i)).isChecked()
        ]

    def financial(self, *, prefix):
        return [
            name for name in (
                'notpaid', 'partiallypaid', 'fullypaid'
            ) if getattr(self, prefix + name).isChecked() 
        ]

    def shipment(self, *, prefix):
        return [
            name for name in ('sent', 'notsent') 
            if getattr(self, prefix + name).isChecked() 
        ]
    
    def logistic(self, *, prefix):
        return [
            name for name in (
                'empty', 'partially_processed', 
                'completed', 'overflowed'
            ) if getattr(self, prefix + name).isChecked()
        ]


    # Agents Handlers:
    def agents_double_click_handler(self, index):
        self.launch_agent_form(index) 
        
    def agents_new_handler(self):
        self.launch_agent_form() 

    def agents_edit_handler(self):
        indexes = self.agents_view.selectedIndexes() 
        if indexes:
            index = indexes[0]
            self.launch_agent_form(index)

    def launch_agent_form(self, index=None):
        if agentgui.AgentGui not in self.opened_windows_classes:
            self.a = agentgui.AgentGui(self, self.agents_view, index) 
            self.a.show() 

            self.opened_windows_instances.add(self.a)
            self.opened_windows_classes.add(agentgui.AgentGui) 

    def agents_search_handler(self):
        key = self.agent_search_line_edit.text() 
        self.setUpAgentsModelAndView(search_key=key)

    def agents_delete_handler(self):
        indexes = self.agents_view.selectedIndexes() 
        if indexes:
            index = indexes[0]
            try:
                self.agentModel.delete(index)
                self.agents_view.clearSelection() 
            except IntegrityError as e:
                if e.orig.args[0] == 1451:
                    QMessageBox.critical(self, 'Error - Delete', \
                        "Could not delete Agent with data associated. Deactivate it.") 

    # Partners Handlers:
    def partners_double_click_handler(self, index):
        self.launch_partners_form(index) 

    def partners_new_handler(self):
        self.launch_partners_form() 

    def partners_edit_handler(self):
        indexes = self.partners_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.launch_partners_form(index)

    def partners_delete_handler(self):
        indexes = self.partners_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            try:
                self.partnerModel.delete(index)
                self.partners_view.clearSelection() 
            except IntegrityError as e:
                QMessageBox.critical(self, "Error - Delete", "Could not delete Partner with data associated. Deactivate it.")

    def partners_search_handler(self):
        key = self.partner_search_line_edit.text() 
        self.setUpPartnersModelAndView(search_key=key)

    def launch_partners_form(self, index=None):
        if partner_form.PartnerForm not in self.opened_windows_classes:
            self.p = partner_form.PartnerForm(self, self.partners_view, index)
            self.p.show()
    
            self.opened_windows_instances.add(self.p)
            self.opened_windows_classes.add(partner_form.PartnerForm)

    # Proformas purchases handlers:
    def proformas_purchases_search_handler(self):
        print('search connected')

    def proformas_purchases_double_click_handler(self, index):
        print('double click')
        self.proformas_purchases_launch_form(index)

    def proformas_purchases_new_handler(self):
        print('new attached')
        # self.proformas_purchases_launch_form() 
    
    def proformas_purchases_cancel_handler(self):
        print('cancel attached')
        # indexes = self.proforma_purchases_view.selectedIndexes() 
        # if not indexes:
        #     return
        # try:
        #     if QMessageBox.question(self, 'Proformas - Cancel', 'Cancel proforma/s ?',\
        #          QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
        #             return

        #     self.purchaseProformaModel.cancel(indexes)
        # except:
        #     raise 
        #     QMessageBox.critical(self, 'Update Error', 'Error updating proformas')

    def proformas_purchases_print_handler(self):
        pass 

    def proformas_purchases_pdf_handler(self):
        pass 

    def proformas_purchases_payments_handler(self, invoice=None):
        if invoice:
            proforma = invoice            
        else:
            proforma = self._getOnePurchaseProforma('Payments')
        if proforma:
            payments_form.PaymentForm(self, proforma).exec_() 

    def proformas_purchases_expenses_handler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOnePurchaseProforma('Expenses')
        if proforma:
            expenses_form.ExpenseForm(self, proforma).exec_() 

    def proformas_purchases_docs_handler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOnePurchaseProforma('Documents')
        if proforma:
            document_form.DocumentForm(self, 'proforma_id', \
                proforma.id , PurchaseProforma, PurchaseDocument).exec_() 

    def proformas_purchases_toinv_handler(self):
        proforma = self._getOnePurchaseProforma('Invoice') 
        if proforma:
            if proforma.cancelled:
                QMessageBox.information(self, 'Information', \
                    "Cannot build invoice from cancelled proforma")
                return 
            try:    
                proforma.invoice.type
                type_num = str(proforma.invoice.type) + '-' \
                    + str(proforma.invoice.number).zfill(6)
                QMessageBox.information(self, 'Information', \
                    f"Invoice already associated: {type_num}") 
            except AttributeError: 
                try:                
                    invoice = self.purchaseProformaModel.associateInvoice(proforma) 
                    type_num = str(invoice.type) + '-' + str(invoice.number).zfill(6)
                    QMessageBox.information(self, 'Information', \
                        f"Invoice {type_num} created")
                except:
                    raise 
                    QMessageBox.critical(self, 'Update - Error', \
                        'Could not build Invoice From Proforma')

    def proformas_purchases_towh_handler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self._getOnePurchaseProforma('Warehouse')
        if not proforma:
            return 
        try:
            ok, note = getNote(self, proforma)
            if not ok:
                return 
            self.purchaseProformaModel.toWarehouse(proforma, note)
            QMessageBox.information(self, 'Information', \
                'Successfully created warehouse reception')            
        except IntegrityError as ex:
            if ex.orig.args[0] == 1048:
                d = 'Invoice' if invoice else 'Proforma'
                QMessageBox.critical(self, 'Update - Error', \
                    f'Warehouse reception for this {d} already exists')

    def proformas_purchases_ship_handler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self._getOnePurchaseProforma('Shipment')
        
        if not proforma:
            return 
        try:
            tracking = getTracking(self, proforma) 
            self.purchaseProformaModel.ship(proforma, tracking)
            QMessageBox.information(self, 'Information', \
                'Tracking number updated successfully')
        except:
            raise 
            QMessageBox.critical(self, 'Update - Error', \
                'Could not update tracking number')

    # def purchaseProformaSelectionChanged(self):
    #     rows = {index.row() for index in self.proforma_purchases_view.selectedIndexes()}
    #     # ship 
    #     if len(rows) != 1:
    #         self.proforma_purchase_ship_button.setEnabled(False)
    #     else:
    #         row = rows.pop() 
    #         if not self.purchaseProformaModel.proformas[row].sent:
    #             self.proforma_purchase_ship_button.setEnabled(True)
    #         else:
    #             self.proforma_purchase_ship_button.setEnabled(False)

    #     rows = {index.row() for index in self.proforma_purchases_view.selectedIndexes()}
        
    #     if len(rows) == 1:
    #         try:
    #             self.purchaseProformaModel.proformas[row].receptions.lines
    #             self.proforma_purchase_warehouse_button.setEnabled(False)
    #         except AttributeError:
    #             self.proforma_purchase_warehouse_button.setEnabled(True)
    #     elif not rows:
    #         self.proforma_purchase_warehouse_button.setEnabled(True)
    #     else:
    #         self.proforma_purchase_warehouse_button.setEnabled(False)

    def proformas_purchases_launch_form(self, index=None):
        if index:
            proforma = self.purchaseProformaModel.proformas[index.row()]
            self.epp = purchase_proforma_form.EditableForm(self,\
                self.proforma_purchases_view, proforma) 
            self.epp.show() 
        else:
            self.pp = purchase_proforma_form.Form(self, self.proforma_purchases_view) 
            self.pp.show() 


    def _getOnePurchaseProforma(self, s=None):
        rows = { index.row() for index in self.proforma_purchases_view.selectedIndexes()}
        if len(rows) == 0:
            return 
        elif len(rows) > 1: 
            QMessageBox.information(self, 'Information', f'{s} for one proforma at a time')
        else:
            return self.purchaseProformaModel.proformas[rows.pop()]
    
    # SALE PROFORMA HANDLERS:
    def saleProformaNewButtonHandler(self):
        self.launchSaleProforma() 
             
    def purchaseProformaSearchHandler(self):
        pass 

    def saleProformaDoubleClickedHandler(self, index):
        self.launchSaleProforma(index)

    def saleProformaCancelHandler(self):
        indexes = self.proforma_sales_view.selectedIndexes() 
        if not indexes:
            return
        try:
            if QMessageBox.question(self, 'Proformas - Cancel', 'Cancel proforma/s ?',\
                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                    return

            self.saleProformaModel.cancel(indexes)
        except:
            raise 
            QMessageBox.critical(self, 'Update Error', 'Error updating proformas')

    def saleProformaPrintButtonHandler(self):
        print('printing')

    def saleProformaPdfButtonHandler(self):
        print('exporting pdfs')
    
    def saleProformaMailButtonHandler(self):
        print('sending mails')

    def saleProformaPaymentsHandler(self, invoice=None):
        if invoice:
            proforma = invoice            
        else:
            proforma = self._getOneSaleProforma('Payments')
        if proforma:
            payments_form.PaymentForm(self, proforma, sale=True).exec_() 

    def saleProformaExpenseButtonHandler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOneSaleProforma('Expenses')
        if proforma:
            expenses_form.ExpenseForm(self, proforma, sale=True).exec_() 

    def saleProformaDocsButtonHandler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOneSaleProforma('Documents')
        if proforma:
            document_form.DocumentForm(self, 'proforma_id', proforma.id , SaleProforma, SaleDocument).exec_() 

    def saleProformaToInvoiceButtonHandler(self):
        proforma = self._getOneSaleProforma('Invoice') 
        if proforma:
            if proforma.cancelled:
                QMessageBox.information(self, 'Information', "Cannot build invoice from cancelled proforma")
                return 
            try:    
                proforma.invoice.type
                type_num = str(proforma.invoice.type) + '-' + str(proforma.invoice.number).zfill(6)
                QMessageBox.information(self, 'Information', f"Invoice already associated: {type_num}") 
            except AttributeError: 
                try:                
                    invoice = self.saleProformaModel.associateInvoice(proforma) 
                    type_num = str(invoice.type) + '-' + str(invoice.number).zfill(6)
                    QMessageBox.information(self, 'Information', f"Invoice {type_num} created")
                except:
                    raise 
                    QMessageBox.critical(self, 'Update - Error', 'Could not build Invoice From Proforma')

    def saleProformaToWarehouseHandler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self._getOneSaleProforma('Warehouse') 
        if not proforma:
            return  
        try:
            # Hay que meter el codigo de la prioridad aqui.
            if not self.saleProformaModel.\
                physicalStockAvailable(proforma.warehouse_id, proforma.lines):
                QMessageBox.critical(self, 'Error',\
                    "Can't send to warehouse for preparation. Not enough SN in physical stock.")
                return

            ok, note = getNote(self, proforma)
            if not ok:
                return
            self.saleProformaModel.toWarehouse(proforma, note)
            QMessageBox.information(self, 'Information', 'Successfully created warehouse expedition')  
            self.proforma_purchases_view.clearSelection() 
            
        except IntegrityError as ex:
            if ex.orig.args[0] == 1048:
                d = 'Invoice' if invoice else 'Proforma'
                QMessageBox.critical(self, 'Update - Error', f'Warehouse expedition for this {d} already exists')

    def saleProformaShippedHandler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self._getOneSaleProforma('Shipment')
        
        if not proforma:
            return 
        try:
            tracking = getTracking(self, proforma) 
            if not tracking:
                return 
            self.saleProformaModel.ship(proforma, tracking)
            QMessageBox.information(self, 'Information', 'Tracking number updated successfully')
        except:
            raise 
            QMessageBox.critical(self, 'Update - Error', 'Could not update tracking number')

    def _getOneSaleProforma(self, s=None):
        rows = { index.row() for index in self.proforma_sales_view.selectedIndexes()}
        if len(rows) == 0:
            return 
        elif len(rows) > 1: 
            QMessageBox.information(self, 'Information', f'{s} for one proforma at a time')
        else:
            return self.saleProformaModel.proformas[rows.pop()]

    def launchSaleProforma(self, index=None):
        if index:
            pass 
        else:
            if sale_proforma_form.Form not in self.opened_windows_classes:
                self.sp = sale_proforma_form.Form(self, self.proforma_sales_view)
                self.sp.show() 

                self.opened_windows_instances.add(self.sp)
                self.opened_windows_classes.add(sale_proforma_form.Form)

    # PURCHASE INVOICE HANDLERS:
    def purchaseInvoicePaymentHandler(self):
        invoice = self._getOneInvoice(self.purchaseInvoiceModel, self.invoices_purchases_view, 'Payments')
        self.purchaseProformaPaymentsHandler(invoice=invoice)
    
    def purchaseInvoiceShippedHandler(self):
        invoice = self._getOneInvoice(self.purchaseInvoiceModel, self.invoices_purchases_view, 'Shipment')
        self.purchaseProformaShippedHandler(invoice)

    def purchaseInvoiceToWarehouseHandler(self):
        invoice = self._getOneInvoice(self.purchaseInvoiceModel, self.invoices_purchases_view,'Warehouse')
        self.purchaseProformaToWarehouseHandler(invoice)

    def purchaseInvoiceDocsHandler(self):
        invoice = self._getOneInvoice(self.purchaseInvoiceModel, self.invoices_purchases_view, 'Documents')
        self.purchaseProformaDocsButtonHandler(invoice=invoice)

    def purchaseInvoiceExpenseButtonHandler(self):
        invoice = self._getOneInvoice(self.purchaseInvoiceModel, self.invoices_purchases_view, 'Expenses')
        self.purchaseProformaExpenseButtonHandler(invoice=invoice)

    def purchaseInvoicePdfHandler(self):
        print('print to pdf')

    def purchaseInvoicePrintHandler(self):
        print('print to printer')

    # SALE INVOICE HANDLER:
    def saleInvoicePaymentHandler(self):
        invoice = self._getOneInvoice(self.saleinvoiceModel, self.sales_invoices_view, s='Payments')
        self.saleProformaPaymentsHandler(invoice=invoice)
    
    def saleInvoiceShippedHandler(self):
        invoice = self._getOneInvoice(self.saleinvoiceModel, self.sales_invoices_view,s='Shipment')
        self.saleProformaShippedHandler(invoice)

    def saleInvoiceToWarehouseHandler(self):
        invoice = self._getOneInvoice(self.saleinvoiceModel, self.sales_invoices_view, s='Warehouse')
        self.saleProformaToWarehouseHandler(invoice)

    def saleInvoiceDocsHandler(self):
        invoice = self._getOneInvoice(self.saleinvoiceModel, self.sales_invoices_view,s='Documents')
        self.saleProformaDocsButtonHandler(invoice=invoice)

    def saleInvoiceExpenseButtonHandler(self):
        invoice = self._getOneInvoice(self.saleinvoiceModel, self.sales_invoices_view,s='Expenses')
        self.saleProformaExpenseButtonHandler(invoice=invoice)

    def saleInvoicePdfHandler(self):
        print('print to pdf')

    def saleInvoicePrintHandler(self):
        print('print to printer')


    def saleInvoiceMailHandler(self):
        print('sending mails')


    def _getOneInvoice(self, model, view, s):
        rows = { index.row() for index in view.selectedIndexes()}
        if len(rows) == 0:
            return 
        elif len(rows) > 1: 
            QMessageBox.information(self, 'Information', f'{s} for one Invoice at a time')
        else:
            return model.invoices[rows.pop()]

    # WAREHOUSE RECEPTION HANDLERS:
    def processReception(self):
        reception = self.getReception(self.warehouse_reception_view, self.receptionModel) 
        if not reception:
            return 
        else:
            reception_order.Form(self, reception).exec_()

    def receptionDoubleClicked(self, index):
        self.processReception() 

    def receptionDeleteHandler(self):
        print('aaa')

    def getReception(self, view, model):
        rows = { index.row() for index in view.selectedIndexes()}
        if len(rows) == 0:
            return
        return model.receptions[rows.pop()]


    # WAREHOUSE EXPEDITION:
    def processExpedition(self):
        expedition = self.getExpedition(self.warehouse_expedition_view, self.expeditionModel) 
        if not expedition:
            return 
        expedition_form.Form(self, expedition).exec_()

    def expeditionDoublecClicked(self):
        self.processExpedition() 

    def expeditionDeleteHandler(self):
        expedition = self.getExpedition(self.warehouse_expedition_view, self.expeditionModel)
        if not expedition:
            return
        
    def getExpedition(self, view, model):
        rows = { index.row() for index in view.selectedIndexes()}
        if len(rows) == 0:
            return
        return model.expeditions[rows.pop()]

    # TOOLS HANDLERS:
    def createProductHandler(self):
        d = product_form.ProductForm(self)  
        password = getPassword(self) 
        if password == PASSWORD:
            d.exec_() 

    def showInventoryHandler(self):
        d = inventory_form.InventoryForm(self)
        password = getPassword(self)
        if password == PASSWORD:
            d.exec_() 

    def changeSpecHandler(self):
        d = spec_change_form.SpecChange(self)
        # password = getPassword(self)
        # if password == PASSWORD:
        d.exec_() 

    def changeCondtionHandler(self):
        d = condition_change_form.ConditionChange(self)
        d.exec_() 
    

    def changeWarehouseHandler(self):
        d = warehouse_change_form.WarehouseChange(self)
        d.exec_() 

    def createWarehouseHandler(self):
        from warehouse import Form
        Form(self).exec_() 
    
    def createConditionHandler(self):
        from condition import Form
        Form(self).exec_() 
    
    def createSpecHandler(self):
        from spec import Form
        Form(self).exec_() 

    def apply_handler(self):
        object_name = self.sender().objectName()
        if object_name.count('_') == 2:
            prefix = object_name[0:object_name.rfind('_') + 1]
            filters = self.get_filters(prefix=prefix)
        elif object_name.count('_') == 1:
            prefix = object_name[0:object_name.index('_')+1]
            filters = self.get_filters(prefix=prefix)
        self.set_mv(prefix, filters) 

    def tabChanged(self, index):
        # Clean up the filters also 
        # And complete the rest of the models
        self.refresh_session() 
        if index == 0:
            self.agentModel = models.AgentModel() 
            self.agents_view.setModel(self.agentModel)
        elif index == 1:
            self.partnerModel = models.PartnerModel() 
            self.partners_view.setModel(self.partnerModel) 
        elif index == 2:
            self.purchaseProformaModel = models.PurchaseProformaModel() 
            self.proforma_purchases_view.setModel(self.purchaseProformaModel)
            self.proforma_purchases_view.selectionModel().selectionChanged.connect(self.purchaseProformaSelectionChanged)
            self.saleProformaModel = models.SaleProformaModel() 
            self.proforma_sales_view.setModel(self.saleProformaModel) 
        elif index == 3:
            self.purchaseInvoiceModel = models.InvoiceModel() 
            self.invoices_purchases_view.setModel(self.purchaseInvoiceModel) 
            self.saleinvoiceModel = models.InvoiceModel(sale=True) 
            self.sales_invoices_view.setModel(self.saleinvoiceModel)
        elif index == 4:
            self.receptionModel = models.ReceptionModel() 
            self.warehouse_reception_view.setModel(self.receptionModel) 
            self.expeditionModel = models.ExpeditionModel() 
            self.warehouse_expedition_view.setModel(self.expeditionModel) 


    def refresh_session(self):
        import db
        db.refresh_session() 
        models.refresh_maps() 

    def closeEvent(self, event):
        for w in self.opened_windows_instances:
            w.close() 
        
        super().closeEvent(event)

