
from PyQt5.QtWidgets import QWidget

from utils import parse_date, build_description

from ui_sale_proforma_form import Ui_SalesProformaForm

from models import AvailableStockModel, SaleProformaLineModel


import db

from utils import setCommonViewConfig

class Form(Ui_SalesProformaForm, QWidget):

    def __init__(self, parent, view):
        super().__init__() 
        self.setupUi(self) 
        self.model = view.model() 
        self.parent = parent
        self.session = self.model.session 
        self.lines_model = SaleProformaLineModel(self.session)
        self.lines_view.setModel(self.lines_model) 
        
        self.setUp() 

    def setUp(self):
        
        setCommonViewConfig(self.lines_view)
        setCommonViewConfig(self.stock_view)

        self.warehouses = self.session.query(db.Warehouse).all() 

        self.warehouse.addItems([w.description for w in self.warehouses])
        self.warehouse.setCurrentText('Free Sale')        

        self._resetStockAvailable(self.warehouse.currentText(), coming=False, item_id=None, condition=None, specification=None)

        self.warehouse.currentTextChanged.connect(self.warehouseChanged) 

    def warehouseChanged(self, warehouse):
        self._resetStockAvailable(warehouse=warehouse, item_id=None, coming=self.coming.isChecked(), \
            condition=self.condition.text(), specification=self.spec.text()) 

    def _resetStockAvailable(self, warehouse, *, coming, item_id, condition, specification):
        self.stock_model = AvailableStockModel(warehouse, coming=coming, item_id=item_id, condition=condition, \
            specification=specification)

        self.stock_view.setModel(self.stock_model)

    def closeEvent(self, event):
        try:
            self.parent.opened_windows_classes.remove(self.__class__)
        except:
            pass       




class EditableSaleProformaForm(Ui_SalesProformaForm, QWidget):
    pass 
