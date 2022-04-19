

from PyQt5.QtWidgets import QWidget
from ui_rmas_incoming_form import Ui_Form


from utils import setCompleter
from utils import partner_id_map
from models import get_partner_warranty
from utils import today_date

from db import IncomingRma
from db import session

from models import RmaIncomingLineModel
from models import get_sn_rma_info

class Form(Ui_Form, QWidget):

    def __init__(self, parent, order=None):
        super(Form, self).__init__()
        self.order = None
        self.lines_model = None
        self.setupUi(self)
        self.set_completer()
        self.set_handlers()

        if order is not None:
            self.order = order
        else:
            self.order = IncomingRma()
            session.add(self.order)
            session.flush()

        self.set_model()

    def set_model(self):
        self.lines_model = RmaIncomingLineModel(self.order.lines)
        self.view.setModel(self.lines_model)

    def set_completer(self):
        setCompleter(self.partner, partner_id_map.keys())
        self.date.setText(today_date())

    def set_handlers(self):
        self.partner.editingFinished.connect(self.search_partner_warranty)
        self.check.clicked.connect(self.search_sn)
        self.exit.clicked.connect(self.exit_handler)

    def search_partner_warranty(self):
        try:
            warranty = get_partner_warranty(partner_id_map[self.partner.text()])
        except KeyError:
            self.warranty.setText('Invalid Partner')
            return
        else:
            self.warranty.setText(str(warranty))


    def search_sn(self):
        sn = self.sn.text()
        self.lines_model.add(sn)


    def exit_handler(self):
        self.close()

    def closeEvent(self, event) -> None:
        session.rollback()




















