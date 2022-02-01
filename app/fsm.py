

from statemachine import StateMachine, State

from models import StockModel
from utils import setCompleter

class FiltersState(StateMachine):
    
    start = State('START', initial=True)
    notmixd = State('NOTMIXD')
    notmixs = State('NOTMIXS')
    newc = State('NEWC')
    mixd = State('MIXD')
    mixc = State('MIXC')
    mixs = State('MIXS')

    # necesito saber en que estado estoy y que input tengo
    # handler para cada uno de los campos 

    start_to_notmixd = start.to(notmixd)
    notmixd_to_start = notmixd.to(start)
    start_to_notmixs = start.to(notmixs)
    notmixs_to_start = notmixs.to(start)
    start_to_newc = start.to(newc)
    newc_to_start = newc.to(start)
    start_to_mixd = start.to(mixd)
    mixd_to_start = mixd.to(start) 
    start_to_mixc = start.to(mixc)
    mixc_to_start = mixc.to(start)
    start_to_mixs = start.to(mixs)
    mixs_to_start = mixs.to(start)
    mixd_to_mixc = mixd.to(mixc)
    mixc_to_mixd = mixc.to(mixc)
    mixd_to_mixs = mixd.to(mixs)
    mixs_to_mixd = mixs.to(mixd)
    mixc_to_mixs = mixc.to(mixs)
    mixs_to_mixc = mixs.to(mixc)


    def on_start_to_notmixd(self):
        pass 

    def on_notmixd_to_start(self):
        pass 

    def __init__(self, form):
        super().__init__() 
        warehouse_id = utils.warehouse_id_map[
            form.warehouse.currentText() 
        ]
        self.stocks = StockModel.compute_availables(warehouse_id) 
        self.description = form.description
        self.condition = form.condition
        self.spec = form.spec 

    



