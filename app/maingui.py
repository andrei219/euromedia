

from PyQt5.QtWidgets import QMainWindow, QTableView, QMessageBox, QInputDialog

from PyQt5 import QtCore

from ui_maingui import Ui_MainGui

import models

import agentgui, partner_form, product_form, purchase_proforma_form, payments_form, expenses_form, \
    document_form, order_form, sale_proforma_form

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
        self.setUpPurchaseOrdersModelAndView() 
        self.setUpSaleOrdersModelAndView() 
        self.setUpPurchaseOrderHandlers() 
        self.setUpSaleOrdersHandlers() 



        # Tools setup:

        self.setupToolsHandlers() 

        self.initFiltersSwitchers() 
        self.main_tab.currentChanged.connect(self.tabChanged)



    ### CHECK BOX FILTERS SETUP ##########################################

    def initFiltersSwitchers(self):
        # Set label status to implement all/none filters selected:
        # Invoice sale:
        self.invoice_sale_series_on = False
        self.invoice_sale_financial_on = False
        self.invoice_sale_logistic_on = False
        self.invoice_sale_shipment_on = False
       
        # Invoice purchase
        self.invoice_purchase_series_on = False
        self.invoice_purchase_financial_on = False
        self.invoice_purchase_logistic_on = False
        self.invoice_purchase_shipment_on = False

        # proforma sale:
        self.proforma_sale_series_on = False
        self.proforma_sale_financial_on  = False
        self.proforma_sale_shipment_on = False
        self.proforma_sale_logistic_on = False
        
        # proforma purchase
        self.proforma_purchase_series_on = False
        self.proforma_purchase_financial_on = False
        self.proforma_purchase_shipment_on = False
        self.proforma_purchase_logistic_on = False

        # warehouse 
        self.expedition_status_on = False
        self.reception_status_on = False

        # Filter headers connections: 
        
        # Invoice sale:
        self.invoice_sale_series.mousePressEvent =  self.on_invoice_sale_series_clicked
        self.invoice_sale_financial.mousePressEvent = self.on_invoice_sale_financial_clicked
        self.invoice_sale_logistic.mousePressEvent = self.on_invoice_sale_logistic_clicked
        self.invoice_sale_shipment.mousePressEvent = self.on_invoice_sale_shipment_clicked
        
        # Invoice purchase:
        self.invoice_purchase_series.mousePressEvent = self.on_invoice_purchase_series_clicked
        self.invoice_purchase_financial.mousePressEvent = self.on_invoice_purchase_financial_clicked
        self.invoice_purchase_logistic.mousePressEvent = self.on_invoice_purchase_logistic_clicked
        self.invoice_purchase_shipment.mousePressEvent = self.on_invoice_purchase_shipment_clicked

        # proforma sale:
        self.proforma_sale_series.mousePressEvent = self.on_proforma_sale_series_clicked
        self.proforma_sale_financial.mousePressEvent = self.on_proforma_sale_financial_clicked
        self.proforma_sale_logistic.mousePressEvent = self.on_proforma_sale_logistic_clicked
        self.proforma_sale_shipment.mousePressEvent = self.on_proforma_sale_shipemnt_clicked


        # Proforma purchase:
        self.proforma_purchase_series.mousePressEvent = self.on_proforma_purchase_series_clicked
        self.proforma_purchase_logistic.mousePressEvent = self.on_proforma_purchase_logistic_clicked
        self.proforma_purchase_financial.mousePressEvent = self.on_proforma_purchase_financial_clicked
        self.proforma_purchase_shipment.mousePressEvent = self.on_proforma_purchase_shipment_clicked
        
        # Warehouse
        self.reception_status.mousePressEvent = self.on_reception_status_clicked
        self.expedition_status.mousePressEvent = self.on_expedition_status_clicked

    def on_invoice_sale_series_clicked(self, event):
        if self.invoice_sale_series_on:
            self.invoice_sale_serie1.setChecked(False)
            self.invoice_sale_serie2.setChecked(False)
            self.invoice_sale_serie3.setChecked(False)
            self.invoice_sale_serie4.setChecked(False)
            self.invoice_sale_serie5.setChecked(False)
            self.invoice_sale_serie6.setChecked(False)
            self.invoice_sale_series_on = False
        else:
            self.invoice_sale_serie1.setChecked(True)
            self.invoice_sale_serie2.setChecked(True)
            self.invoice_sale_serie3.setChecked(True)
            self.invoice_sale_serie4.setChecked(True)
            self.invoice_sale_serie5.setChecked(True)
            self.invoice_sale_serie6.setChecked(True)
            self.invoice_sale_series_on = True

    def on_invoice_sale_financial_clicked(self, event):
        if self.invoice_sale_financial_on:
            self.invoice_sale_notpaid.setChecked(False)
            self.invoice_sale_partialpaid.setChecked(False)
            self.invoice_sale_fullpaid.setChecked(False)
            self.invoice_sale_cancelled.setChecked(False) 
            self.invoice_sale_financial_on = False
        else:
            self.invoice_sale_notpaid.setChecked(True)
            self.invoice_sale_partialpaid.setChecked(True)
            self.invoice_sale_fullpaid.setChecked(True)
            self.invoice_sale_cancelled.setChecked(True)
            self.invoice_sale_financial_on = True 

    def on_invoice_sale_logistic_clicked(self, event):
        if self.invoice_sale_logistic_on:
            self.invoice_sale_noinstructions.setChecked(False)
            self.invoice_sale_queued.setChecked(False)
            self.invoice_sale_waiting.setChecked(False)
            self.invoice_sale_inpartialprep_chekbox.setChecked(False)
            self.invoice_sale_infullprep.setChecked(False)
            self.invoice_sale_completed.setChecked(False)
            self.invoice_sale_cancelled.setChecked(False)
            self.invoice_sale_logistic_on = False 
        else:
            self.invoice_sale_noinstructions.setChecked(True)
            self.invoice_sale_queued.setChecked(True)
            self.invoice_sale_waiting.setChecked(True)
            self.invoice_sale_inpartialprep_chekbox.setChecked(True)
            self.invoice_sale_infullprep.setChecked(True)
            self.invoice_sale_completed.setChecked(True)
            self.invoice_sale_cancelled.setChecked(True)
            self.invoice_sale_logistic_on = True 

    def on_invoice_sale_shipment_clicked(self, event):
        if self.invoice_sale_shipment_on:
            self.invoice_sale_sent.setChecked(False)
            self.invoice_sale_notsent.setChecked(False)
            self.invoice_sale_shipment_on = False 
        else:
            self.invoice_sale_sent.setChecked(True)
            self.invoice_sale_notsent.setChecked(True) 
            self.invoice_sale_shipment_on = True

    # invoice purchase 
    def on_invoice_purchase_series_clicked(self, event):
        if self.invoice_purchase_series_on:
            self.invoice_purchase_serie1.setChecked(False)
            self.invoice_purchase_serie2.setChecked(False)
            self.invoice_purchase_serie3.setChecked(False)
            self.invoice_purchase_serie4.setChecked(False)
            self.invoice_purchase_serie5.setChecked(False)
            self.invoice_purchase_serie6.setChecked(False)
            self.invoice_purchase_series_on = False
        else:
            self.invoice_purchase_serie1.setChecked(True)
            self.invoice_purchase_serie2.setChecked(True)
            self.invoice_purchase_serie3.setChecked(True)
            self.invoice_purchase_serie4.setChecked(True)
            self.invoice_purchase_serie5.setChecked(True)
            self.invoice_purchase_serie6.setChecked(True)
            self.invoice_purchase_series_on = True
    
    def on_invoice_purchase_financial_clicked(self, event):
        if self.invoice_purchase_financial_on:
            self.invoice_purchase_notpaid.setChecked(False)
            self.invoice_purchase_fullpaid.setChecked(False)
            self.invoice_purchase_partialpaid.setChecked(False)
            self.invoice_purchase_financial_on = False
        else:
            self.invoice_purchase_notpaid.setChecked(True)
            self.invoice_purchase_fullpaid.setChecked(True)
            self.invoice_purchase_partialpaid.setChecked(True)
            self.invoice_purchase_financial_on = True

    def on_invoice_purchase_logistic_clicked(self, event):
        if self.invoice_purchase_logistic_on:
            self.invoice_purchase_noinstructions.setChecked(False)
            self.invoice_purchase_queued.setChecked(False)
            self.invoice_purchase_waiting.setChecked(False)
            self.invoice_purchase_partialreceived.setChecked(False)
            self.invoice_purchase_fullreceived.setChecked(False)
            self.invoice_purchase_completed.setChecked(False)
            self.invoice_purchase_cancelled.setChecked(False)
            self.invoice_purchase_logistic_on = False
        else:
            self.invoice_purchase_noinstructions.setChecked(True)
            self.invoice_purchase_queued.setChecked(True)
            self.invoice_purchase_waiting.setChecked(True)
            self.invoice_purchase_partialreceived.setChecked(True)
            self.invoice_purchase_fullreceived.setChecked(True)
            self.invoice_purchase_completed.setChecked(True)
            self.invoice_purchase_cancelled.setChecked(True)
            self.invoice_purchase_logistic_on = True

    def on_invoice_purchase_shipment_clicked(self, event):
        if self.invoice_purchase_shipment_on:
            self.invoice_purchase_sent.setChecked(False)
            self.invoice_purchase_notsent.setChecked(False)
            self.invoice_purchase_shipment_on = False
        else:
            self.invoice_purchase_sent.setChecked(True)
            self.invoice_purchase_notsent.setChecked(True)
            self.invoice_purchase_shipment_on = True
            

    # proforma sale:
    def on_proforma_sale_series_clicked(self, event):
        if self.proforma_sale_series_on:
            self.proforma_sale_serie1.setChecked(False)
            self.proforma_sale_serie2.setChecked(False)
            self.proforma_sale_serie3.setChecked(False)
            self.proforma_sale_serie4.setChecked(False)
            self.proforma_sale_serie5.setChecked(False)
            self.proforma_sale_serie6.setChecked(False)
            self.proforma_sale_series_on = False
        else:
            self.proforma_sale_serie1.setChecked(True)
            self.proforma_sale_serie2.setChecked(True)
            self.proforma_sale_serie3.setChecked(True)
            self.proforma_sale_serie4.setChecked(True)
            self.proforma_sale_serie5.setChecked(True)
            self.proforma_sale_serie6.setChecked(True)
            self.proforma_sale_series_on = True
            
    def on_proforma_sale_financial_clicked(self, event):
        if self.proforma_sale_financial_on:
            self.proforma_sale_notpaid.setChecked(False)
            self.proforma_sale_partialpaid.setChecked(False)
            self.proforma_sale_fullpaid.setChecked(False)
            self.proforma_sale_financial_on = False
        else:
            self.proforma_sale_notpaid.setChecked(True)
            self.proforma_sale_partialpaid.setChecked(True)
            self.proforma_sale_fullpaid.setChecked(True)
            self.proforma_sale_financial_on = True
    
    def on_proforma_sale_logistic_clicked(self, event):
        if self.proforma_sale_logistic_on:
            self.proforma_sale_noinstructions.setChecked(False)
            self.proforma_sale_queued.setChecked(False)
            self.proforma_sale_waitingstock.setChecked(False)
            self.proforma_sale_inpartialprep_chekbox.setChecked(False)
            self.proforma_sale_infullprep.setChecked(False)
            self.proforma_sale_cancelled.setChecked(False)
            self.proforma_sale_completed.setChecked(False)
            self.proforma_sale_logistic_on = False
        else:
            self.proforma_sale_noinstructions.setChecked(True)
            self.proforma_sale_queued.setChecked(True)
            self.proforma_sale_waitingstock.setChecked(True)
            self.proforma_sale_inpartialprep_chekbox.setChecked(True)
            self.proforma_sale_infullprep.setChecked(True)
            self.proforma_sale_cancelled.setChecked(True)
            self.proforma_sale_completed.setChecked(True)
            self.proforma_sale_logistic_on = True

    def on_proforma_sale_shipemnt_clicked(self, event):
        if self.proforma_sale_shipment_on:
            self.proforma_sale_sent.setChecked(False)
            self.proforma_sale_notsent.setChecked(False)
            self.proforma_sale_shipment_on = False
        else:
            self.proforma_sale_sent.setChecked(True)
            self.proforma_sale_notsent.setChecked(True)
            self.proforma_sale_shipment_on = True

    # proforma purchase
    def on_proforma_purchase_series_clicked(self, event):
        if self.proforma_purchase_series_on:
            self.proforma_purchase_serie1.setChecked(False)
            self.proforma_purchase_serie2.setChecked(False)
            self.proforma_purchase_serie3.setChecked(False)
            self.proforma_purchase_serie4.setChecked(False)
            self.proforma_purchase_serie5.setChecked(False)
            self.proforma_purchase_serie6.setChecked(False)
            self.proforma_purchase_series_on = False
        else:
            self.proforma_purchase_serie1.setChecked(True)
            self.proforma_purchase_serie2.setChecked(True)
            self.proforma_purchase_serie3.setChecked(True)
            self.proforma_purchase_serie4.setChecked(True)
            self.proforma_purchase_serie5.setChecked(True)
            self.proforma_purchase_serie6.setChecked(True)
            self.proforma_purchase_series_on = True

    def on_proforma_purchase_financial_clicked(self, event):
        if self.proforma_purchase_financial_on:
            self.proforma_purchase_notpaid.setChecked(False)
            self.proforma_purchase_fullpaid.setChecked(False)
            self.proforma_purchase_partialpaid.setChecked(False) 
            self.proforma_purchase_financial_on = False
        else:
            self.proforma_purchase_notpaid.setChecked(True)
            self.proforma_purchase_fullpaid.setChecked(True)
            self.proforma_purchase_partialpaid.setChecked(True) 
            self.proforma_purchase_financial_on = True

    def on_proforma_purchase_logistic_clicked(self, event):
        if self.proforma_purchase_logistic_on:
            self.proforma_purchase_noinstructions.setChecked(False)
            self.proforma_purchase_queued.setChecked(False)
            self.proforma_purchase_waitingstock.setChecked(False)
            self.proforma_purchase_partiallyreceived.setChecked(False)
            self.proforma_purchase_fullreceived.setChecked(False)
            self.proforma_purchase_completed.setChecked(False)
            self.proforma_purchase_cancelled.setChecked(False)
            self.proforma_purchase_logistic_on = False
        else:
            self.proforma_purchase_noinstructions.setChecked(True)
            self.proforma_purchase_queued.setChecked(True)
            self.proforma_purchase_waitingstock.setChecked(True)
            self.proforma_purchase_partiallyreceived.setChecked(True)
            self.proforma_purchase_fullreceived.setChecked(True)
            self.proforma_purchase_completed.setChecked(True)
            self.proforma_purchase_cancelled.setChecked(True)
            self.proforma_purchase_logistic_on = True

    def on_proforma_purchase_shipment_clicked(self, event):
        if self.proforma_purchase_shipment_on:
            self.proforma_purchase_sent.setChecked(False)
            self.proforma_purchase_notsent.setChecked(False)
            self.proforma_purchase_shipment_on = False
        else:
            self.proforma_purchase_sent.setChecked(True)
            self.proforma_purchase_notsent.setChecked(True)
            self.proforma_purchase_shipment_on = True

    # Warehouse:
    # Warehouse reception:
    def on_reception_status_clicked(self, event):
        if self.reception_status_on:
            self.reception_empty.setChecked(False) 
            self.reception_partially.setChecked(False)
            self.reception_completed.setChecked(False)
            self.reception_cancelled.setChecked(False)
            self.reception_status_on = False
        else:
            self.reception_empty.setChecked(True) 
            self.reception_partially.setChecked(True)
            self.reception_completed.setChecked(True)
            self.reception_cancelled.setChecked(True)
            self.reception_status_on = True

    # Warehouse expedition:
    def on_expedition_status_clicked(self, event):
        if self.expedition_status_on:
            self.expedition_empty.setChecked(False) 
            self.expedition_partially.setChecked(False)
            self.expedition_completed.setChecked(False)
            self.expedition_cancelled.setChecked(False)
            self.expedition_status_on = False
        else:
            self.expedition_empty.setChecked(True) 
            self.expedition_partially.setChecked(True)
            self.expedition_completed.setChecked(True)
            self.expedition_cancelled.setChecked(True)
            self.expedition_status_on = True


    def on_invoice_purchase_apply_pressed(self):
        filters = self._captureInvoicePurchaseFilters()
        print(filters)

    def on_proforma_sale_apply_pressed(self):
        filters = self._captureProformaSaleFilters() 

    def on_proforma_purchase_apply_pressed(self):
        filters = self._captureProformaPurchaseFilters()
        print(filters)
    
    def on_expedition_apply_pressed(self):
        filters = self._captureWarehouseExpeditionFilters()
        search_key = self.expedition_search.text() 
        self.setUpSaleOrdersModelAndView(filters=filters, search_key=search_key)
    
    def on_reception_apply_pressed(self):
        filters = self._captureWarehouseReceptionFilters() 
        search_key = self.reception_search.text() 
        self.setUpPurchaseOrdersModelAndView(filters=filters, search_key=search_key)        

    def _captureInvoiceSaleFilters(self):   
        
        filters = {
            "series":[
                1 if self.invoice_sale_serie1.isChecked() else None, 
                2 if self.invoice_sale_serie2.isChecked() else None, 
                3 if self.invoice_sale_serie3.isChecked() else None, 
                4 if self.invoice_sale_serie4.isChecked() else None, 
                5 if self.invoice_sale_serie5.isChecked() else None, 
                6 if self.invoice_sale_serie6.isChecked() else None
            ], 
            "financial":[
                "not" if self.invoice_sale_notpaid.isChecked() else None, 
                "full" if self.invoice_sale_fullpaid.isChecked() else None, 
                "partial" if self.invoice_sale_partialpaid.isChecked() else None, 
                "cancelled" if self.invoice_sale_cancelled.isChecked() else None
            ], 
            "logistic":[
                "queued" if self.invoice_sale_queued.isChecked() else None, 
                "waiting stock" if self.invoice_sale_waiting.isChecked() else None, 
                "completed" if self.invoice_sale_completed.isChecked() else None, 
            ], 
            "shipment":[
                "sent" if self.invoice_sale_sent.isChecked() else None, 
                "not" if self.invoice_sale_notsent.isChecked() else None
            ]
        }

        return washDict(filters)
    
    def _captureInvoicePurchaseFilters(self) :
        
        filters = {
            "series":[
                1 if self.invoice_purchase_serie1.isChecked() else None, 
                2 if self.invoice_purchase_serie2.isChecked() else None, 
                3 if self.invoice_purchase_serie3.isChecked() else None, 
                4 if self.invoice_purchase_serie4.isChecked() else None, 
                5 if self.invoice_purchase_serie5.isChecked() else None, 
                6 if self.invoice_purchase_serie6.isChecked() else None
            ], 
            "logistic":[
                "no instructions" if self.invoice_purchase_noinstructions.isChecked() else None, 
                "queued" if self.invoice_purchase_queued.isChecked() else None, 
                "waiting stock" if self.invoice_purchase_waiting.isChecked() else None, 
                "partially received" if self.invoice_purchase_partialreceived.isChecked() else None, 
                "fully received" if self.invoice_purchase_fullreceived.isChecked() else None, 
                "completed" if self.invoice_purchase_completed.isChecked() else None, 
                "cancelled" if self.invoice_purchase_cancelled.isChecked() else None 
            ],"financial":[
                "full" if self.invoice_purchase_fullpaid.isChecked() else None, 
                "partial" if self.invoice_purchase_partialpaid.isChecked() else None, 
                "not" if self.invoice_purchase_notpaid.isChecked() else None, 
                "cancelled" if self.invoice_purchase_cancelled.isChecked() else None 
            ], 
            "shipment":[
                "sent" if self.invoice_purchase_sent.isChecked() else None, 
                "not" if self.invoice_purchase_notsent.isChecked() else None 
            ] 
        }
    
        return washDict(filters) 

    def _captureProformaSaleFilters(self):
        filters = {
            "series":[
                1 if self.proforma_sale_serie1.isChecked() else None, 
                2 if self.proforma_sale_serie2.isChecked() else None, 
                3 if self.proforma_sale_serie3.isChecked() else None, 
                4 if self.proforma_sale_serie4.isChecked() else None, 
                5 if self.proforma_sale_serie5.isChecked() else None, 
                6 if self.proforma_sale_serie6.isChecked() else None,
            ], "financial":[
                "not paid" if self.proforma_sale_notpaid.isChecked() else None, 
                "fully paid" if self.proforma_sale_fullpaid.isChecked() else None, 
                "partially paid" if self.proforma_sale_partialpaid.isChecked() else None
            ], "logistic":[
                "no instructions" if self.proforma_sale_noinstructions.isChecked() else None, 
                "queued" if self.proforma_sale_queued.isChecked() else None, 
                "waiting stock" if self.proforma_sale_waitingstock.isChecked() else None, 
                "in partial preparation" if self.proforma_sale_inpartialprep_chekbox.isChecked() else None, 
                "in full preparation" if self.proforma_sale_infullprep.isChecked() else None, 
                "completed" if self.proforma_sale_completed.isChecked() else None, 
                "cancelled" if self.proforma_sale_cancelled.isChecked() else None
            ], "shipment":[
                "sent" if self.proforma_sale_sent.isChecked() else None, 
                "not sent" if self.proforma_sale_notsent.isChecked() else None
            ]
        }

        return washDict(filters)

    def _captureProformaPurchaseFilters(self):
        filters = {
            "series":[
                1 if self.proforma_purchase_serie1.isChecked() else None, 
                2 if self.proforma_purchase_serie2.isChecked() else None, 
                3 if self.proforma_purchase_serie3.isChecked() else None, 
                4 if self.proforma_purchase_serie4.isChecked() else None, 
                5 if self.proforma_purchase_serie5.isChecked() else None, 
                6 if self.proforma_purchase_serie6.isChecked() else None 
            ], "financial":[
                "partially paid" if self.proforma_purchase_partialpaid.isChecked() else None, 
                "fully paid" if self.proforma_purchase_fullpaid.isChecked() else None, 
                "not paid" if self.proforma_purchase_notpaid.isChecked() else None 
            ], "logistic":[
                "no instructions" if self.proforma_sale_noinstructions.isChecked() else None, 
                "queued" if self.proforma_purchase_queued.isChecked() else None, 
                "waiting" if self.proforma_purchase_waitingstock.isChecked() else None, 
                "partially received" if self.proforma_purchase_partiallyreceived.isChecked() else None, 
                "fully received" if self.proforma_purchase_fullreceived.isChecked() else None, 
                "completed" if self.proforma_purchase_completed.isChecked() else None, 
                "cancelled" if self.proforma_purchase_cancelled.isChecked() else None
            ], "shipment":[
                "sent" if self.proforma_purchase_sent.isChecked() else None, 
                "not sent" if self.proforma_purchase_notsent.isChecked() else None
            ]
        }

        return washDict(filters)

    def _captureWarehouseExpeditionFilters(self):
        return tuple(
            filter(
                None, 
                (
                    "empty" if self.expedition_empty.isChecked() else None, 
                    "partially processed" if self.expedition_partially.isChecked() else None, 
                    "completed" if self.expedition_completed.isChecked() else None, 
                    "cancelled" if self.expedition_cancelled.isChecked() else None
                )
            )
        )

    def _captureWarehouseReceptionFilters(self):
        return tuple(
            filter(
                None, 
                (
                    "empty" if self.reception_empty.isChecked() else None, 
                    "partially processed" if self.reception_partially.isChecked() else None, 
                    "completed" if self.reception_completed.isChecked() else None, 
                    "cancelled" if self.reception_cancelled.isChecked() else None
                )
            )
        )

    ### CHECK BOX FILTERS SETUP ##############################################################

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
        pass 

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
        session = self.purchaseProformaModel.session
        if invoice:
            proforma = invoice            
        else:
            proforma = self._getOnePurchaseProforma('Payments')
        if proforma:
            payments_form.PaymentForm(self, proforma, session).exec_() 

    def purchaseProformaExpenseButtonHandler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOnePurchaseProforma('Expenses')
        if proforma:
            session = self.purchaseProformaModel.session
            expenses_form.ExpenseForm(self, proforma, session).exec_() 

    def purchaseProformaDocsButtonHandler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOnePurchaseProforma('Documents')
        if proforma:
            document_form.DocumentForm(self, 'proforma_id', proforma.id , PurchaseProforma, PurchaseDocument).exec_() 

    def purchaseProformaToInvoiceButtonHandler(self):
        proforma = self._getOnePurchaseProforma('Invoice') 
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
                    invoice = self.purchaseProformaModel.associateInvoice(proforma) 
                    type_num = str(invoice.type) + '-' + str(invoice.number).zfill(6)
                    QMessageBox.information(self, 'Information', f"Invoice {type_num} created")
                except:
                    raise 
                    QMessageBox.critical(self, 'Update - Error', 'Could not build Invoice From Proforma')

    def purchaseProformaToWarehouseHandler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self._getOnePurchaseProforma('Warehouse')
        if not proforma:
            return 
        try:
            note = getNote(self, proforma)
            if not note:
                return 
            self.purchaseProformaModel.toWarehouse(proforma, note)
            QMessageBox.information(self, 'Information', 'Successfully created warehouse order')            
        except IntegrityError as ex:
            if ex.orig.args[0] == 1048:
                d = 'Invoice' if invoice else 'Proforma'
                QMessageBox.critical(self, 'Update - Error', f'Warehouse order for this {d} already exists')

    def purchaseProformaShippedHandler(self, invoice=None):
        if invoice:
            proforma = invoice
        else:
            proforma = self._getOnePurchaseProforma('Shipment')
        
        if not proforma:
            return 
        try:
            tracking = getTracking(self, proforma) 
            if not tracking:
                return 
            self.purchaseProformaModel.ship(proforma, tracking)
            QMessageBox.information(self, 'Information', 'Tracking number updated successfully')
        except:
            raise 
            QMessageBox.critical(self, 'Update - Error', 'Could not update tracking number')

    def launchPurchaseProformaForm(self, index=None):
        if index:
            pass 
        else:
            if purchase_proforma_form.Form not in self.opened_windows_classes:
                self.pp = purchase_proforma_form.Form(self, self.proforma_purchases_view) 
                self.pp.show() 

                self.opened_windows_instances.add(self.pp) 
                self.opened_windows_classes.add(purchase_proforma_form.Form) 

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
        session = self.saleProformaModel.session
        if invoice:
            proforma = invoice            
        else:
            proforma = self._getOneSaleProforma('Payments')
        if proforma:
            payments_form.PaymentForm(self, proforma, session, sale=True).exec_() 

    def saleProformaExpenseButtonHandler(self, invoice=None):
        if invoice:
            proforma = invoice 
        else:
            proforma = self._getOneSaleProforma('Expenses')
        if proforma:
            session = self.saleProformaModel.session
            expenses_form.ExpenseForm(self, proforma, session, sale=True).exec_() 

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
            note = getNote(self, proforma)
            if not note:
                return 
            self.saleProformaModel.toWarehouse(proforma, note)
            QMessageBox.information(self, 'Information', 'Successfully created warehouse order')            
        except IntegrityError as ex:
            raise ex
            if ex.orig.args[0] == 1048:
                d = 'Invoice' if invoice else 'Proforma'
                QMessageBox.critical(self, 'Update - Error', f'Warehouse order for this {d} already exists')

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
    def processPurchaseOrder(self):
        order = self._getOrder(self.warehouse_reception_view, self.purchaseOrdersModel) 
        if not order:
            return 
        session = self.purchaseOrdersModel.session
        order_form.OrderForm(self, order, session).exec_() 
    
    def purchaseOrderDoubleClicked(self, index):
        self.processPurchaseOrder() 

    def _getOrder(self, view, model):
        rows = { index.row() for index in view.selectedIndexes()}
        if len(rows) == 0:
            return
        return model.orders[rows.pop()]

    # WAREHOUSE EXPEDITION:
    def processSaleOrder(self):
        order = self._getOrder(self.warehouse_expedition_view, self.saleOrderModel) 
        if not order:
            return 
        session = self.saleOrderModel.session
        order_form.OrderForm(self, order, session, sale=True).exec_()

    def saleOrderDoubleClicked(self):
        self.processSaleOrder() 

    # TOOLS HANDLERS:
    def createProductHandler(self):
        d = product_form.ProductForm(self)  
        password = getPassword(self) 
        if password == PASSWORD:
            d.exec_() 
    
    def setUpAgentsModelAndView(self, search_key=None):
        self.agentModel = models.AgentModel(search_key) 
        self.agents_view.setModel(self.agentModel)
        setCommonViewConfig(self.agents_view)

    def setUpPartnersModelAndView(self, search_key=None):
        self.partnerModel = models.PartnerModel(search_key)
        self.partners_view.setModel(self.partnerModel)
        setCommonViewConfig(self.partners_view)
    
    def setUpPurchaseProformasModelAndView(self, search_key=None, filters=None):
        self.purchaseProformaModel = models.PurchaseProformaModel(filter, search_key) 
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

    def setUpSaleOrdersModelAndView(self, search_key=None, filters=None):
        self.saleOrderModel = models.OrderModel(sale=True, search_key=search_key, filters=filters)
        self.warehouse_expedition_view.setModel(self.saleOrderModel)
        setCommonViewConfig(self.warehouse_expedition_view)

    def setUpPurchaseOrdersModelAndView(self, search_key=None, filters=None):
        self.purchaseOrdersModel = models.OrderModel(search_key=search_key, filters=filters) 
        self.warehouse_reception_view.setModel(self.purchaseOrdersModel) 
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
        self.proforma_purchases_view.doubleClicked.connect(self.purchaseProformaDoubleClickedHandler)
        self.proforma_purchase_new_button.clicked.connect(self.purchaseProformaNewButtonHandler) 
        self.proforma_purchase_payment_button.clicked.connect(self.purchaseProformaPaymentsHandler)
        self.proforma_purchase_cancel_button.clicked.connect(self.purchaseProformaCancelHandler)
        self.proforma_purchase_search_lineedit.returnPressed.connect(self.purchaseProformaSearchHandler)
        self.proforma_purchase_expense_button.clicked.connect(self.purchaseProformaExpenseButtonHandler)
        self.proforma_purchase_documents_button.clicked.connect(self.purchaseProformaDocsButtonHandler) 
        self.proforma_purchase_invoice_button.clicked.connect(self.purchaseProformaToInvoiceButtonHandler)  
        self.proforma_purchase_ship_button.clicked.connect(self.purchaseProformaShippedHandler) 
        self.proforma_purchase_warehouse_button.clicked.connect(self.purchaseProformaToWarehouseHandler)

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

    def setUpPurchaseOrderHandlers(self):
        self.reception_process.clicked.connect(self.processPurchaseOrder) 
        self.warehouse_reception_view.doubleClicked.connect(self.purchaseOrderDoubleClicked)

    def setUpSaleOrdersHandlers(self):
        self.expedition_process.clicked.connect(self.processSaleOrder) 
        self.warehouse_expedition_view.doubleClicked.connect(self.saleOrderDoubleClicked)

    def setupToolsHandlers(self):
        self.create_product_button.clicked.connect(self.createProductHandler)

    def tabChanged(self, index):
        # Clean up the filters also 
        # And complete the rest of the models mai frei 
        if index == 0:
            self.agentModel = models.AgentModel() 
            self.agents_view.setModel(self.agentModel)
        elif index == 1:
            self.partnerModel = models.PartnerModel() 
            self.partners_view.setModel(self.partnerModel) 
        elif index == 2:
            self.purchaseProformaModel = models.PurchaseProformaModel() 
            self.proforma_purchases_view.setModel(self.purchaseProformaModel)
            self.saleProformaModel = models.SaleProformaModel() 
            self.proforma_sales_view.setModel(self.saleProformaModel) 
        elif index == 3:
            self.purchaseInvoiceModel = models.InvoiceModel() 
            self.invoices_purchases_view.setModel(self.purchaseInvoiceModel) 
            self.saleinvoiceModel = models.InvoiceModel(sale=True) 
            self.sales_invoices_view.setModel(self.saleinvoiceModel)
        elif index == 4:
            self.purchaseOrdersModel = models.OrderModel() 
            self.warehouse_reception_view.setModel(self.purchaseOrdersModel) 
            self.saleOrderModel = models.OrderModel(sale=True) 
            self.warehouse_expedition_view.setModel(self.saleOrderModel) 

    def closeEvent(self, event):
        for w in self.opened_windows_instances:
            w.close() 
        
        super().closeEvent(event)


