import os 

from PyQt5.QtWidgets import (
    QMainWindow, 
    QTableView, 
    QMessageBox, 
    QInputDialog, 
    QFileDialog,
    
)

from PyQt5 import QtCore

from ui_maingui import Ui_MainGui

import models 
  
import agentgui, partner_form, product_form, purchase_proforma_form, payments_form, expenses_form, \
    document_form, expedition_form, sale_proforma_form, inventory_form, spec_change_form, condition_change_form, \
        warehouse_change_form, reception_order, advanced_sale_proforma_form

from sqlalchemy.exc import IntegrityError

from utils import (
    setCommonViewConfig, 
    getPassword, 
    getTracking, 
    getNote, 
    get_directory
) 

import db 
from pdfbuilder import build_document

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
    'warehouse_receptions_', 
    'tools_'
]

ACTIONS = [
    'apply', 
    'new', 
    'edit', 
    'delete', 
    'cancel', 
    'print', 
    'export', 
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
    'search', 
    'create_warehouse', 
    'change_warehouse', 
    'create_spec', 
    'change_spec',
    'create_condition', 
    'change_condition', 
    'check_inventory', 
    'create_product', 
    'view_pdf', 
    'newadv'
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
        self.main_tab.currentChanged.connect(self.tab_changed)


        self.proformas_purchases_view.selectionModel().\
            selectionChanged.connect(self.proformas_purchases_selection_changed)

        self.proformas_sales_view.selectionModel().\
            selectionChanged.connect(self.proformas_sales_selection_changed)


        # self.invoices_sales_view.selectionModel().\
        #     selectionChanged.connect(self.invoices_sales_selection_changed)
        
        # self.invoices_purchases_view.selectionModel().\
        #     selectionChanged.connect(self.invoices_purchases_selection_changed)

    def selection_changed_generic(self, view):
        rows = {i.row() for i in view.selectedIndexes()}
        total, paid = 0, 0
        for row in rows:
            doc = view.model()[row] 
            paid += sum(p.amount for p in doc.payments)
            total += round(
                    sum(
                    line.price * line.quantity 
                    for line in doc.lines
                ), 2
            ) 

        name = view.objectName() 
        prefix = name[0:name.rfind('_') +  1]

        getattr(self, prefix + 'total').setText('Total: ' + str(total))
        getattr(self, prefix + 'paid').setText('Paid: ' + str(paid))

    def init_models(self):
        for prefix in PREFIXES:
            self.set_mv(prefix)

    def set_mv(self, prefix, search_key=None, filters=None):
        from utils import setCommonViewConfig
        if prefix == 'agents_':
            self.agents_model = models.AgentModel(search_key=search_key)
            self.agents_view.setModel(self.agents_model) 
            setCommonViewConfig(self.agents_view)

        elif prefix == 'partners_':
            self.partners_model = models.PartnerModel(search_key=search_key)
            self.partners_view.setModel(self.partners_model)
            setCommonViewConfig(self.partners_view)

        elif prefix == 'proformas_purchases_':
            self.proformas_purchases_model = \
                models.PurchaseProformaModel(filters=filters, search_key=search_key)
            self.proformas_purchases_view.setModel(
                self.proformas_purchases_model
            )
            self.proformas_purchases_view.setSelectionBehavior(QTableView.SelectRows)
            self.proformas_purchases_view.setSortingEnabled(True)
            self.proformas_purchases_view.setAlternatingRowColors(True)

        elif prefix == 'invoices_purchases_':
            self.invoices_purchases_model = \
                models.PurchaseInvoiceModel(filters=filters, search_key=search_key)
            self.invoices_purchases_view.setModel(self.invoices_purchases_model)
            self.invoices_purchases_view.setSelectionBehavior(QTableView.SelectRows)
            self.invoices_purchases_view.setSortingEnabled(True)
            self.invoices_purchases_view.setAlternatingRowColors(True)

        elif prefix == 'invoices_sales_':
            self.invoices_sales_model = \
                models.SaleInvoiceModel(filters=filters, search_key=search_key)
            self.invoices_sales_view.setModel(self.invoices_sales_model)
            self.invoices_sales_view.setSelectionBehavior(QTableView.SelectRows)
            self.invoices_sales_view.setSortingEnabled(True)
            self.invoices_sales_view.setAlternatingRowColors(True)


        elif prefix == 'proformas_sales_':
            self.proformas_sales_model = \
                models.SaleProformaModel(filters=filters, search_key=search_key)
            self.proformas_sales_view.setModel(
                self.proformas_sales_model
            )
            self.proformas_sales_view.setSelectionBehavior(QTableView.SelectRows)
            self.proformas_sales_view.setAlternatingRowColors(True)
            self.proformas_sales_view.setSortingEnabled(True) 

        elif prefix == 'warehouse_receptions_':
            self.warehouse_receptions_model = \
                models.ReceptionModel(filters=filters, search_key=search_key)
            self.warehouse_receptions_view.setModel(self.warehouse_receptions_model)
            self.warehouse_receptions_view.setSelectionBehavior(QTableView.SelectRows)
            self.warehouse_receptions_view.setSortingEnabled(True)
            self.warehouse_receptions_view.setAlternatingRowColors(True) 

        elif prefix == 'warehouse_expeditions_':
            self.warehouse_expeditions_model = models.ExpeditionModel(
                filters = filters, 
                search_key = search_key
            )
            self.warehouse_expeditions_view.setModel(self.warehouse_expeditions_model)
            self.warehouse_expeditions_view.setSelectionBehavior(QTableView.SelectRows)
            self.warehouse_expeditions_view.setAlternatingRowColors(True)
            self.warehouse_expeditions_view.setSortingEnabled(True)

    def set_handlers(self):
        from itertools import product
        for prefix, action in product(PREFIXES, ACTIONS):
            try:
                widget_name = prefix + action
                self.attach_handler(prefix, action)
            except AttributeError:
                continue  

    def attach_handler(self, prefix, action):
        try:
            if action == 'apply':
                handler = getattr(self, action + '_handler')
                widget = getattr(self, prefix + action)
                widget.clicked.connect(handler) 
            elif action == 'double_click':
                handler = getattr(self, prefix + action + '_handler') 
                widget = getattr(self, prefix + 'view')
                widget.doubleClicked.connect(handler) 
            elif action == 'search':
                handler = getattr(self, action + '_handler')
                widget = getattr(self, prefix + action)
                widget.returnPressed.connect(handler)
            else:
                handler = getattr(self, prefix + action + '_handler')
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


    def apply_handler(self):
        object_name = self.sender().objectName()
        prefix = object_name[0:object_name.rfind('_') + 1]
        filters = self.get_filters(prefix=prefix)
        self.set_mv(prefix,filters=filters)
    
    def search_handler(self):
        widget = self.sender() 
        object_name = widget.objectName()    
        prefix = object_name[0:object_name.rfind('_') + 1]
        filters = self.get_filters(prefix=prefix)
        search_key = widget.text()
        self.set_mv(prefix, filters=filters, search_key=search_key) 

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



    def export_documents(self, view, model, is_invoice=False):
        ixs = view.selectedIndexes()
        if not ixs:return  
        directory = get_directory(self)
        if not directory:return 
        rows = {i.row() for i in ixs}
        try:
            for row in rows:
                proforma = model[row]
                if not is_invoice:
                    name = str(proforma.type) + '-' + str(proforma.number).zfill(6) + '.pdf'
                else:
                    name = str(proforma.invoice.type) + '-' + \
                        str(proforma.invoice.number).zfill(6) + '.pdf'
                pdf = build_document(proforma, is_invoice=is_invoice)
                pdf.output(os.path.join(directory, name))
        
        
        except:
            QMessageBox.critical(self, 'Error', 'Error exporting documents')
            raise 
        else:
            QMessageBox.information(self, 'Success', 'Document exported successfully')

    def view_documents(self, view, model, is_invoice=False):
        ixs = view.selectedIndexes()
        if not ixs:return
        rows = {i.row() for i in ixs}
        try:
            for row in rows:
                document = model[row]
                if not is_invoice:
                    filename = str(document.type) + '-' + str(document.number).zfill(6)
                else:
                    filename = str(document.invoice.type) + '-' + str(document.invoice.number).zfill(6)
                filename += '.pdf'
                pdf = build_document(document, is_invoice=is_invoice)
                pdf.output(filename)
                import subprocess
                subprocess.Popen((filename, ), shell=True) 
                os.remove(filename)
        except:
            QMessageBox.critical(self, 'Error', 'Error viewing the file')
            raise 

    # Proformas purchases handlers:
    def proformas_purchases_view_pdf_handler(self):
        self.view_documents(
            self.proformas_purchases_view, 
            self.proformas_purchases_model
        )

    def proformas_purchases_selection_changed(self, selection_model):
        self.selection_changed_generic(self.proformas_purchases_view)

    def proformas_purchases_double_click_handler(self, index):
        self.proformas_purchases_launch_form(index)

    def proformas_purchases_new_handler(self):
        self.proformas_purchases_launch_form() 
    
    def proformas_purchases_cancel_handler(self):
        indexes = self.proformas_purchases_view.selectedIndexes() 
        if not indexes:
            return
        try:
            if QMessageBox.question(self, 'Proformas - Cancel', 'Cancel proforma/s ?',\
                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                    return
            self.proformas_purchases_model.cancel(indexes)
        except:
            raise 
            QMessageBox.critical(self, 'Update Error', 'Error updating proformas')

    def proformas_purchases_print_handler(self):
        print('print') 

    def proformas_purchases_export_handler(self):
        self.export_documents(
            self.proformas_purchases_view, 
            self.proformas_purchases_model
        )
        

    def proformas_purchases_payments_handler(self, invoice=None):
        if invoice:
            proforma = invoice            
        else:
            proforma = self.get_proforma_purchase()
        if proforma:
            payments_form.PaymentForm(self, proforma).exec_() 

    def proformas_purchases_expenses_handler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self.get_proforma_purchase()
        if proforma:
            expenses_form.ExpenseForm(self, proforma).exec_() 

    def proformas_purchases_docs_handler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self.get_proforma_purchase()
        if proforma:
            document_form.DocumentForm(
                self, 
                'proforma_id', 
                proforma.id , 
                PurchaseProforma, 
                PurchaseDocument
            ).exec_() 

    def proformas_purchases_toinv_handler(self):
        proforma = self.get_proforma_purchase() 
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
                    invoice = self.proformas_purchases_model.associateInvoice(proforma) 
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
            proforma = self.get_proforma_purchase()
        if proforma:
            try:
                ok, note = getNote(self, proforma)
                if ok:
                    self.proformas_purchases_model.toWarehouse(proforma, note)
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
            proforma = self.get_proforma_purchase()
        if proforma:
            try:
                tracking, ok = getTracking(self, proforma) 
                if ok:
                    print(ok, tracking)
                    self.proformas_purchases_model.ship(proforma, tracking)
                    mss = 'Updated successfully'
                    if invoice:
                        mss = 'Invoice/Proforma ' + mss 
                    QMessageBox.information(self, 'Information', mss)
            except:
                QMessageBox.critical(self, 'Update - Error', \
                    'Error updating proforma')
                raise 

    def proformas_purchases_launch_form(self, index=None, proforma=None, is_invoice=False):
        if proforma:
            self.epp = purchase_proforma_form.EditableForm(
                self, 
                self.proformas_purchases_view,
                proforma, 
                is_invoice=is_invoice
            )
            self.epp.show()
        elif index:
            proforma = self.proformas_purchases_model.proformas[index.row()]
            self.epp = purchase_proforma_form.EditableForm(
                self,
                self.proformas_purchases_view,
                proforma, 
                is_invoice=is_invoice
            ) 
            self.epp.show() 
        else:
            self.pp = purchase_proforma_form.Form(
                self, 
                self.proformas_purchases_view, 
            ) 
            self.pp.show() 


    def get_proforma_purchase(self):
        rows = { index.row() for index in \
            self.proformas_purchases_view.selectedIndexes()}
        if len(rows) == 1:
            return self.proformas_purchases_model.proformas[rows.pop()]
    
    # PROFORMAS SALES HANDLERS
    def proformas_sales_newadv_handler(self):
        self.launch_adv_sale_proforma_form()

    def proformas_sales_view_pdf_handler(self):
        self.view_documents(
            self.proformas_sales_view, 
            self.proformas_sales_model
        )

    def proformas_sales_selection_changed(self):
        self.selection_changed_generic(self.proformas_sales_view)
       
    def proformas_sales_new_handler(self):
        self.launch_sale_proforma_form() 

    def proformas_sales_double_click_handler(self, index):
        self.launch_sale_proforma_form(index)

    def proformas_sales_cancel_handler(self):
        indexes = self.proformas_sales_view.selectedIndexes() 
        if not indexes:
            return
        try:
            if QMessageBox.question(
                self, 
                'Proformas - Cancel', 
                'Cancel proforma/s ?',
                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                    return

            self.proformas_sales_model.cancel(indexes)
        except:
            raise 
            QMessageBox.critical(self, 'Update Error', 'Error updating proformas')

    def proformas_sales_print_handler(self):
        print('printing')

    def proformas_sales_export_handler(self):
        self.export_documents(
            self.proformas_sales_view, 
            self.proformas_sales_model
        )

    
    def proformas_sales_mail_handler(self):
        print('sending mails')

    def proformas_sales_payments_handler(self, invoice=None):
        if invoice:
            proforma = invoice            
        else:
            proforma = self.get_sale_proforma('Payments')
        if proforma:
            payments_form.PaymentForm(self, proforma, sale=True).exec_() 

    def proformas_sales_expenses_handler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self.get_sale_proforma('Expenses')
        if proforma:
            expenses_form.ExpenseForm(self, proforma, sale=True).exec_() 

    def proformas_sales_docs_handler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self.get_sale_proforma('Documents')
        if proforma:
            document_form.DocumentForm(
                self, 
                'proforma_id',
                proforma.id ,
                SaleProforma,
                SaleDocument
            ).exec_() 

    def proformas_sales_toinv_handler(self):
        proforma = self.get_sale_proforma('Invoice') 
        if proforma:
            if proforma.cancelled:
                QMessageBox.information(
                self,
                'Information', 
                "Cannot build invoice from cancelled proforma"
            )
                return 
            try:    
                proforma.invoice.type
                type_num = str(proforma.invoice.type) + '-' \
                    + str(proforma.invoice.number).zfill(6)
                QMessageBox.information(
                    self, 
                    'Information', 
                    f"Invoice already associated: {type_num}") 
            except AttributeError: 
                try:                
                    invoice = self.proformas_sales_model.associateInvoice(proforma) 
                    type_num = str(invoice.type) + '-' \
                        + str(invoice.number).zfill(6)
                    QMessageBox.information(
                        self, 
                        'Information', 
                        f"Invoice {type_num} created")
                except:
                    raise 
                    QMessageBox.critical(
                        self, 
                        'Update - Error', 
                        'Could not build Invoice From Proforma')

    def proformas_sales_towh_handler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self.get_sale_proforma('Warehouse') 
        if not proforma:
            return  
        try:
            # # Hay que meter el codigo de la prioridad aqui.
            # if not self.proformas_sales_model.\
            #     stock_available(proforma.warehouse_id, proforma.lines):
            #     QMessageBox.critical(
            #         self, 
            #         'Error',
            #         "Can't send to warehouse for preparation. Not enough SN in physical stock."
            #     )
            #     return

            ok, note = getNote(self, proforma)
            if not ok:
                return
            self.proformas_sales_model.toWarehouse(proforma, note)
            QMessageBox.information(self, 'Information', 'Successfully created warehouse expedition')  
            self.proformas_purchases_view.clearSelection() 
            
        except IntegrityError as ex:
            if ex.orig.args[0] == 1048:
                d = 'Invoice' if invoice else 'Proforma'
                QMessageBox.critical(self, 'Update - Error', f'Warehouse expedition for this {d} already exists')

    def proformas_sales_ship_handler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self.get_sale_proforma('Shipment')
        if not proforma:
            return 
        try:
            ok, tracking = getTracking(self, proforma) 
            if ok:
                self.proformas_sales_model.ship(proforma, tracking)
                mss = 'updated'
                if invoice:
                    mss = 'Invoice/Proforma ' + mss 
                else:
                    mss = 'Proforma ' + mss 
                QMessageBox.information(self,'Information', mss)
        except:
            raise 

    def get_sale_proforma(self, s=None):
        rows = { index.row() for index in \
            self.proformas_sales_view.selectedIndexes()}
        if len(rows) == 1:
            return self.proformas_sales_model.proformas[rows.pop()]


    def launch_adv_sale_proforma_form(self, index=None):
        from contextlib import suppress
        proforma = None 
        with suppress(AttributeError):
            proforma = self.proformas_sales_model.proformas[index.row()]

        self.advsp = advanced_sale_proforma_form.get_form(
            self, 
            self.proformas_sales_view, 
            proforma
        )

        self.advsp.show() 


    def launch_sale_proforma_form(self, index=None):
        proforma = None 
        try:
            proforma = self.proformas_sales_model.proformas[index.row()]
        except AttributeError:
            pass
        self.sp = sale_proforma_form.get_form(
            self, 
            self.proformas_sales_view, 
            proforma
        )
        self.sp.show()

    # PURCHASE INVOICE HANDLERS:

    def invoices_purchases_view_pdf_handler(self):
        self.view_documents(
            self.invoices_purchases_view, 
            self.invoices_purchases_model, 
            is_invoice=True 
        )

    def invoices_purchases_selection_changed(self):
        self.selection_changed_generic(self.invoices_purchases_view)

    def invoices_purchases_payments_handler(self):
        invoice = self.get_purchases_invoice() 
        self.proformas_purchases_payments_handler(invoice=invoice)
    
    def invoices_purchases_ship_handler(self):
        invoice = self.get_purchases_invoice() 
        self.proformas_purchases_ship_handler(invoice)

    def invoices_purchases_towh_handler(self):
        invoice = self.get_purchases_invoice()          
        self.proformas_purchases_towh_handler(invoice)

    def invoices_purchases_docs_handler(self):
        invoice = self.get_purchases_invoice()  
        self.proformas_purchases_docs_handler(invoice=invoice)

    def invoices_purchases_expenses_handler(self):
        invoice = self.get_purchases_invoice()          
        self.proformas_purchases_expenses_handler(invoice=invoice)

    def invoices_purchases_double_click_handler(self, index):
        proforma = self.invoices_purchases_model[index.row()]
        self.proformas_purchases_launch_form(proforma=proforma, is_invoice=True)
    
    def invoices_purchases_export_handler(self):
       self.export_documents(
           self.invoices_purchases_view, 
           self.invoices_purchases_model, 
           is_invoice=True 
       )

    
    def invoices_purchases_print_handler(self):
        print('print to printer')

    def get_purchases_invoice(self):
        return self.get_invoice(
            self.invoices_purchases_model, 
            self.invoices_purchases_view
        )

    # SALE INVOICE HANDLER:
    def invoices_sales_view_pdf_handler(self):
        self.view_documents(
            self.invoices_sales_view, 
            self.invoices_sales_model, 
            is_invoice=True
        )

    def invoices_sales_selection_changed(self):
        self.selection_changed_generic(self.invoices_purchases_view)

    def invoices_sales_payments_handler(self):
        invoice = self.get_sales_invoice() 
        self.proformas_sales_payments_handler(invoice=invoice)

    def invoices_sales_ship_handler(self):
        invoice = self.get_sales_invoice()
        self.proformas_sales_ship_handler(invoice) 

    def invoices_sales_towh_handler(self):
        invoice = self.get_sales_invoice()
        self.proformas_sales_towh_handler(invoice=invoice)

    def invoices_sales_docs_handler(self):
        invoice = self.get_sales_invoice()
        self.proformas_sales_docs_handler(invoice=invoice)

    def invoices_sales_expenses_handler(self):
        invoice = self.get_sales_invoice()
        self.proformas_sales_expenses_handler(invoice=invoice)

    def invoices_sales_export_handler(self):
        self.export_documents(
            self.invoices_sales_view, 
            self.invoices_sales_model, 
            is_invoice = True
        )
        

    def invoices_sales_print_handler(self):
        print('print to printer')

    def invoices_sales_mail_handler(self):
        print('sending mails')

    def get_sales_invoice(self):
        return self.get_invoice(
            self.invoices_sales_model, 
            self.invoices_sales_view
        )

    def get_invoice(self, model, view):
        rows = { index.row() for index in view.selectedIndexes()}
        if len(rows) == 1:
            return model.invoices[rows.pop()]

    # WAREHOUSE RECEPTION HANDLERS:
    def warehouse_receptions_process_handler(self):
        reception = self.get_reception(
            self.warehouse_receptions_view,
            self.warehouse_receptions_model
        ) 
        if not reception:
            return 
        else:
            reception_order.Form(self, reception).exec_()

    def warehouse_receptions_double_click_handler(self, index):
        self.warehouse_receptions_process_handler()

    def warehouse_receptions_delete_handler(self):
        print('delete')

    def warehouse_receptions_print_handler(self):
        print('print')

    def warehouse_expeditions_apply_handler(self):
        pass 

    def get_reception(self, view, model):
        rows = { index.row() for index in view.selectedIndexes()}
        if len(rows) == 1:
            return model.receptions[rows.pop()]


    # WAREHOUSE EXPEDITION:
    def warehouse_expeditions_process_handler(self):
        expedition = self.get_expedition(
            self.warehouse_expedition_view, 
            self.warehouse_expeditions_model
        ) 
        if not expedition:return 
        expedition_form.Form(self, expedition).exec_()

    def warehouse_expeditions_double_click_handler(self, index):
        expedition = self.warehouse_expeditions_model.expeditions[index.row()]
        expedition_form.Form(self, expedition).exec_() 

    def warehouse_expeditions_delete_handler(self):
        expedition = self.get_expedition(
            self.warehouse_expeditions_view,
            self.warehouse_expeditions_model
        )
        if not expedition:return
        
        print('delete expedition with ID:', expedition.id)


    def get_expedition(self, view, model):
        rows = { index.row() for index in view.selectedIndexes()}
        if len(rows) == 1:
            return model.expeditions[rows.pop()]

    # TOOLS HANDLERS:
    def tools_create_product_handler(self):
        d = product_form.ProductForm(self)  
        password = getPassword(self) 
        if password == PASSWORD:
            d.exec_() 

    def tools_check_inventory_handler(self):
        d = inventory_form.InventoryForm(self)
        password = getPassword(self)
        if password == PASSWORD:
            d.exec_() 
    
    def tools_change_spec_handler(self):
        if models.stock_gap():
            QMessageBox.information(self, 'Information', 'Process all sales first.')
            return 
        d = spec_change_form.SpecChange(self)
        # password = getPassword(self)
        # if password == PASSWORD:
        d.exec_() 

    def tools_change_condition_handler(self):
        if models.stock_gap():
            QMessageBox.information(self, 'Information', 'Process all sales first.')
            return 
        d = condition_change_form.ConditionChange(self)
        d.exec_() 
    

    def tools_change_warehouse_handler(self):
        if models.stock_gap():
            QMessageBox.information(self, 'Information', 'Process all sales first.')
            return 
        d = warehouse_change_form.WarehouseChange(self)
        d.exec_() 

    def tools_create_warehouse_handler(self):
        from warehouse import Form
        Form(self).exec_() 
    
    def tools_create_condition_handler(self):
        from condition import Form
        Form(self).exec_() 
    
    def tools_create_spec_handler(self):
        from spec import Form
        Form(self).exec_() 

    def tab_changed(self, index):
        # Clean up the filters also 
        # And complete the rest of the models
        db.session.commit() 
        
        if index == 0:
           self.set_mv('agents_')
        elif index == 1:
            self.set_mv('partners_')
        elif index == 2:
            self.set_mv('proformas_purchases_')
            self.set_mv('proformas_sales_')
        elif index == 3:
            self.set_mv('invoices_purchases_')
            self.set_mv('invoices_sales_')
        elif index == 4:
            self.set_mv('warehouse_expeditions_')
            self.set_mv('warehouse_receptions_')
            self.set_mv('warehouse_incoming_rmas_')
            self.set_mv('warehouse_outgoing_rmas_')

    def closeEvent(self, event):
        for w in self.opened_windows_instances:
            w.close() 
        
        super().closeEvent(event)

