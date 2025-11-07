import os 
import sys 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))


if __name__ == "__main__":

    from app import db 
    from app import models as m 
    from app import utils

    for p in db.session.query(db.PurchaseProforma):
        if m.get_purchase_stock_value(p) == 0: 
            
            print(f"Zero stock value proforma: {p.id} - {p.number} - {p.agent.fiscal_name}")