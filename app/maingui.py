

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

class MainGui(Ui_MainGui, QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setCentralWidget(self.main_tab)

        # For closing 
        self.opened_windows_instances = set() 
        
        # Prevent creating multiple
        self.opened_windows_classes = set() 


        # Agents setup 
        self.setUpAgentsModelAndView() 
        self.setUpAgentsHandlers() 
        
        # Partners setup
        self.setUpPartnersModelAndView() 
        self.setUpPartnersHandlers() 
        
        
        # Invoices setup:
        self.setUpPurchaseInvoicesModelAndView()
        self.setUpSaleInvoicesModelAndView() 
        self.setUpSaleInvoicesHandler() 
        self.setUpPurchaseInvoicesHandler() 


        # Proformas setup:
        self.setUpPurchaseProformasModelAndView() 
        self.setUpPurchaseProformaHandlers() 
        self.setUpSaleProformasModelAndView() 
        self.setUpSalesProformasHandler() 


        # Warehouse setup:
        self.setUpReceptionMV() 
        self.setUpExpeditionMV() 
        self.setUpReceptionHandlers() 
        self.setUpExpeditionHandlers() 

        # Tools setup:
        self.setupToolsHandlers() 
        self.main_tab.currentChanged.connect(self.tabChanged)

    def get_filters(self,*, prefix):
        return {
            group_name : getattr(self, group_name)(prefix=prefix) 
            for group_name in [
                'types', 'financial', 
                'shipment', 'logistic'
            ]
        }

    def types(self, *, prefix):
        return [
            i for i in range(1, 7)
            if getattr(self, prefix + 'serie' + str(i)).isChecked()
        ]

    def financial(self, *, prefix):
        return [
            name for name in (
                'notpaid', 'partiallypaid', 
                'fullypaid', 'cancelled'
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


    # Agent Handlers:
    def agentDoubleClickedHandler(self, index):
        self.launchAgentGui(index) 
        
    def agentNewButtonHandler(self):
        self.launchAgentGui() 

    def agentEditButtonHandler(self):
        indexes = self.agents_view.selectedIndexes() 
        if indexes:
            index = indexes[0]
            self.launchAgentGui(index)

    def launchAgentGui(self, index=None):
        if agentgui.AgentGui not in self.opened_windows_classes:
            self.a = agentgui.AgentGui(self, self.agents_view, index) 
            self.a.show() 

            self.opened_windows_instances.add(self.a)
            self.opened_windows_classes.add(agentgui.AgentGui) 

    def agentSearchHandler(self):
        key = self.agent_search_line_edit.text() 
        self.setUpAgentsModelAndView(search_key=key)

    def agentDeleteHandler(self):
        indexes = self.agents_view.selectedIndexes() 
        if indexes:
            index = indexes[0]
            try:
                self.agentModel.delete(index)
                self.agents_view.clearSelection() 
            except IntegrityError as e:
                if e.orig.args[0] == 1451:
                    QMessageBox.critical(self, 'Error - Delete', "Could not delete Agent with data associated. Deactivate it.") 

    # Partner Handlers:
    def partnerDoubleClickedHandler(self, index):
        self.launchPartnerGui(index) 

    def partnerNewButtonHandler(self):
        self.launchPartnerGui() 

    def partnerEditButtonHandler(self):
        indexes = self.partners_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.launchPartnerGui(index)

    def partnerDeleteHandler(self):
        indexes = self.partners_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            try:
                self.partnerModel.delete(index)
                self.partners_view.clearSelection() 
            except IntegrityError as e:
                QMessageBox.critical(self, "Error - Delete", "Could not delete Partner with data associated. Deactivate it.")

    def partnerSearchHandler(self):
        key = self.partner_search_line_edit.text() 
        self.setUpPartnersModelAndView(search_key=key)

    def launchPartnerGui(self, index=None):
        if partner_form.PartnerForm not in self.opened_windows_classes:
            self.p = partner_form.PartnerForm(self, self.partners_view, index)
            self.p.show()
    
            self.opened_windows_instances.add(self.p)
            self.opened_windows_classes.add(partner_form.PartnerForm)

    # PURCHASE PROFORMA HANDLERS:
    def purchaseProformaSearchHandler(self):
        filters = self.proformap

    def purchaseProformaDoubleClickedHandler(self, index):
        self.launchPurchaseProformaForm(index)

    def purchaseProformaNewButtonHandler(self):
        self.launchPurchaseProformaForm() 
    
    def purchaseProformaCancelHandler(self):
        indexes = self.proforma_purchases_view.selectedIndexes() 
        if not indexes:
            return
        try:
            if QMessageBox.question(self, 'Proformas - Cancel', 'Cancel proforma/s ?',\
                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                    return

            self.purchaseProformaModel.cancel(indexes)
        except:
            raise 
            QMessageBox.critical(self, 'Update Error', 'Error updating proformas')

    def purchaseProformaPrintButtonHandler(self):
        pass 

    def purchaseProformaPdfButtonHandler(self):
        pass 

    def purchaseProformaPaymentsHandler(self, invoice=None):
        if invoice:
            proforma = invoice            
        else:
            proforma = self._getOnePurchaseProforma('Payments')
        if proforma:
            payments_form.PaymentForm(self, proforma).exec_() 

    def purchaseProformaExpenseButtonHandler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOnePurchaseProforma('Expenses')
        if proforma:
            expenses_form.ExpenseForm(self, proforma).exec_() 

    def purchaseProformaDocsButtonHandler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOnePurchaseProforma('Documents')
        if proforma:
            document_form.DocumentForm(self, 'proforma_id', \
                proforma.id , PurchaseProforma, PurchaseDocument).exec_() 

    def purchaseProformaToInvoiceButtonHandler(self):
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

    def purchaseProformaToWarehouseHandler(self, invoice=None):
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

    def purchaseProformaShippedHandler(self, invoice=None):
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

    def purchaseProformaSelectionChanged(self):
        rows = {index.row() for index in self.proforma_purchases_view.selectedIndexes()}
        # ship 
        if len(rows) != 1:
            self.proforma_purchase_ship_button.setEnabled(False)
        else:
            row = rows.pop() 
            if not self.purchaseProformaModel.proformas[row].sent:
                self.proforma_purchase_ship_button.setEnabled(True)
            else:
                self.proforma_purchase_ship_button.setEnabled(False)

        rows = {index.row() for index in self.proforma_purchases_view.selectedIndexes()}
        
        if len(rows) == 1:
            try:
                self.purchaseProformaModel.proformas[row].receptions.lines
                self.proforma_purchase_warehouse_button.setEnabled(False)
            except AttributeError:
                self.proforma_purchase_warehouse_button.setEnabled(True)
        elif not rows:
            self.proforma_purchase_warehouse_button.setEnabled(True)
        else:
            self.proforma_purchase_warehouse_button.setEnabled(False)

    def launchPurchaseProformaForm(self, index=None):
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

    def setUpAgentsModelAndView(self, search_key=None):
        self.agentModel = models.AgentModel(search_key) 
        self.agents_view.setModel(self.agentModel)
        setCommonViewConfig(self.agents_view)

    def setUpPartnersModelAndView(self, search_key=None):
        self.partnerModel = models.PartnerModel(search_key)
        self.partners_view.setModel(self.partnerModel)
        setCommonViewConfig(self.partners_view)
    
    def setUpPurchaseProformasModelAndView(self, search_key=None, filters=None):
        self.purchaseProformaModel = models.PurchaseProformaModel(filters, search_key) 
        self.proforma_purchases_view.setModel(self.purchaseProformaModel) 
        self.proforma_purchases_view.setSelectionBehavior(QTableView.SelectRows)
        self.proforma_purchases_view.setSortingEnabled(True)
        self.proforma_purchases_view.setAlternatingRowColors(True)
        self.proforma_purchases_view.setEditTriggers(QTableView.NoEditTriggers)
        
    def setUpSaleProformasModelAndView(self, search_key=None, filters=None):
        self.saleProformaModel = models.SaleProformaModel(search_key, filters) 
        self.proforma_sales_view.setModel(self.saleProformaModel) 
        self.proforma_sales_view.setSelectionBehavior(QTableView.SelectRows)
        self.proforma_sales_view.setSortingEnabled(True)
        self.proforma_sales_view.setAlternatingRowColors(True)
        self.proforma_sales_view.setEditTriggers(QTableView.NoEditTriggers)
        
    def setUpPurchaseInvoicesModelAndView(self, search_key=None, filters=None):
        self.purchaseInvoiceModel = models.InvoiceModel(search_key, filters) 
        self.invoices_purchases_view.setModel(self.purchaseInvoiceModel)
        setCommonViewConfig(self.invoices_purchases_view)

    def setUpSaleInvoicesModelAndView(self, search_key=None, filters=None):
        self.saleinvoiceModel = models.InvoiceModel(search_key=search_key, filters=filters, sale=True) 
        self.sales_invoices_view.setModel(self.saleinvoiceModel) 
        setCommonViewConfig(self.sales_invoices_view) 

    def setUpExpeditionMV(self, search_key=None, filters=None):
        self.expeditionModel = models.ExpeditionModel(search_key=search_key, filters=filters)
        self.warehouse_expedition_view.setModel(self.expeditionModel)
        setCommonViewConfig(self.warehouse_expedition_view)

    def setUpReceptionMV(self, search_key=None, filters=None):
        self.receptionModel = models.ReceptionModel(search_key=search_key, filters=filters) 
        self.warehouse_reception_view.setModel(self.receptionModel) 
        setCommonViewConfig(self.warehouse_reception_view) 

    def setUpAgentsHandlers(self):
        self.agents_view.doubleClicked.connect(self.agentDoubleClickedHandler) 
        self.agent_new_button.pressed.connect(self.agentNewButtonHandler)
        self.agent_edit_button.pressed.connect(self.agentEditButtonHandler)
        self.agent_search_line_edit.returnPressed.connect(self.agentSearchHandler) 
        self.agent_delete_button.pressed.connect(self.agentDeleteHandler)

    def setUpPartnersHandlers(self):
        self.partners_view.doubleClicked.connect(self.partnerDoubleClickedHandler)
        self.partner_new_button.pressed.connect(self.partnerNewButtonHandler)
        self.partner_edit_button.pressed.connect(self.partnerEditButtonHandler)
        self.delete_partner_button.pressed.connect(self.partnerDeleteHandler)
        self.partner_search_line_edit.returnPressed.connect(self.partnerSearchHandler) 

    def setUpPurchaseProformaHandlers(self):
        self.proforma_purchases_view.selectionModel().selectionChanged.connect(self.purchaseProformaSelectionChanged)
        self.proforma_purchases_view.doubleClicked.connect(self.purchaseProformaDoubleClickedHandler)
        self.proforma_purchase_new_button.clicked.connect(self.purchaseProformaNewButtonHandler) 
        self.proforma_purchase_payment_button.clicked.connect(self.purchaseProformaPaymentsHandler)
        self.proforma_purchase_cancel_button.clicked.connect(self.purchaseProformaCancelHandler)
        self.proforma_purchase_search.returnPressed.connect(self.purchaseProformaSearchHandler)
        self.proforma_purchase_expense_button.clicked.connect(self.purchaseProformaExpenseButtonHandler)
        self.proforma_purchase_documents_button.clicked.connect(self.purchaseProformaDocsButtonHandler) 
        self.proforma_purchase_invoice_button.clicked.connect(self.purchaseProformaToInvoiceButtonHandler)  
        self.proforma_purchase_ship_button.clicked.connect(self.purchaseProformaShippedHandler) 
        self.proforma_purchase_warehouse_button.clicked.connect(self.purchaseProformaToWarehouseHandler)
        self.proforma_purchase_apply.clicked.connect(self.apply_handler)


    def apply_handler(self):
        object_name = self.sender().objectName()
        if 'proforma_purchase_' in object_name:
            filters = self.get_filters(prefix='proforma_purchase_')
            print(filters)
        elif 'proforma_sale_' in object_name:
            filters = self.get_filters(prefix='proforma_sale_')
            print(filters)

    def setUpSalesProformasHandler(self):
        self.proforma_sale_new_button.clicked.connect(self.saleProformaNewButtonHandler)
        self.sales_proformas_cancel_button.clicked.connect(self.saleProformaCancelHandler) 
        self.proforma_sale_print_button.clicked.connect(self.saleProformaPrintButtonHandler) 
        self.proforma_sale_pdf_button.clicked.connect(self.saleProformaPdfButtonHandler)
        self.proforma_sale_mail_button.clicked.connect(self.saleProformaMailButtonHandler)
        self.proforma_sale_payment_button.clicked.connect(self.saleProformaPaymentsHandler)
        self.proforma_sale_expense_button.clicked.connect(self.saleProformaExpenseButtonHandler) 
        self.proforma_sale_documents_button.clicked.connect(self.saleProformaDocsButtonHandler)
        self.proforma_sale_invoice_button.clicked.connect(self.saleProformaToInvoiceButtonHandler)
        self.proforma_sale_warehouse_button.clicked.connect(self.saleProformaToWarehouseHandler)
        self.proforma_sale_ship_button.clicked.connect(self.saleProformaShippedHandler)
        self.proforma_sale_apply.clicked.connect(self.apply_handler)


    def setUpSaleInvoicesHandler(self):
        self.invoice_sale_print_button.clicked.connect(self.saleInvoicePrintHandler)
        self.invoice_sale_ship_button.clicked.connect(self.saleInvoiceShippedHandler)
        self.invoice_sale_warehouse_button.clicked.connect(self.saleInvoiceToWarehouseHandler) 
        self.invoice_sale_expense_button.clicked.connect(self.saleInvoiceExpenseButtonHandler)
        self.invoice_sale_payment_button.clicked.connect(self.saleInvoicePaymentHandler)
        self.invoice_sale_pdf_button.clicked.connect(self.saleInvoicePdfHandler)
        self.invoice_sale_mail_button.clicked.connect(self.saleInvoiceMailHandler)
        self.invoice_sale_docs_button.clicked.connect(self.saleInvoiceDocsHandler) 

    def setUpPurchaseInvoicesHandler(self):
        self.invoice_purchase_payment_button.clicked.connect(self.purchaseInvoicePaymentHandler)
        self.invoice_purchase_ship_button.clicked.connect(self.purchaseInvoiceShippedHandler)
        self.invoice_purchase_warehouse_button.clicked.connect(self.purchaseInvoiceToWarehouseHandler)
        self.invoice_purchase_expense_button.clicked.connect(self.purchaseInvoiceExpenseButtonHandler) 
        self.invoice_purchase_docs_button.clicked.connect(self.purchaseInvoiceDocsHandler) 
        self.invoice_purchase_pdf_button.clicked.connect(self.purchaseInvoicePdfHandler) 
        self.invoice_purchase_print_button.clicked.connect(self.purchaseInvoicePrintHandler)

    def setUpReceptionHandlers(self):
        self.reception_process.clicked.connect(self.processReception) 
        self.warehouse_reception_view.doubleClicked.connect(self.receptionDoubleClicked)
        self.reception_delete.clicked.connect(self.receptionDeleteHandler)

    def setUpExpeditionHandlers(self):
        self.expedition_process.clicked.connect(self.processExpedition) 
        self.warehouse_expedition_view.doubleClicked.connect(self.expeditionDoublecClicked)
        self.expedition_delete.clicked.connect(self.expeditionDeleteHandler)

    def setupToolsHandlers(self):
        self.create_product_button.clicked.connect(self.createProductHandler)
        self.check_inventory.clicked.connect(self.showInventoryHandler)
        self.change_spec.clicked.connect(self.changeSpecHandler)
        self.change_condition.clicked.connect(self.changeCondtionHandler)
        self.change_warehouse.clicked.connect(self.changeWarehouseHandler)
        self.create_warehouse.clicked.connect(self.createWarehouseHandler)
        self.create_spec.clicked.connect(self.createSpecHandler)
        self.create_condition.clicked.connect(self.createConditionHandler) 


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

