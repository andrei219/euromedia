



from db import session
from db import PurchaseProforma as Proforma
from db import PurchaseProformaLine as Line
from db import Reception
from db import ReceptionSerie
from db import ReceptionLine
from db import AdvancedLine
from db import Partner
from sqlalchemy import func, join
from sqlalchemy.orm import aliased

s = session.query(Line).join(Proforma).join(Partner).outerjoin(Reception)

class Vector:
    def __init__(self, line):
        self.line_id = line.id 
        self.type = line.proforma.type
        self.number = line.proforma.number 
        self.partner = line.proforma.partner.fiscal_name
        self.item_id = line.item_id
        # self.description = line.description
        self.asked = sum(line.quantity for line in line.advanced_lines)
        try:
            # breakpoint()
            self.processed = sum(
                1 for line in line.proforma.reception.lines
                for serie in line.series 
                if self.line_id == line.id 
            )
        except AttributeError as ex:
            self.processed = 0 

    def __iter__(self):
        return iter(self.__dict__.values())

    # def __repr__(self):
    #     classname = self.__class__.__name__
    #     return classname + \
    #         '(' + ', '.join(map(str, self)) + ')'

    def __repr__(self):
        return repr(self.__dict__)

from db import engine



for line in sorted(s.all(), key=lambda o:o.id):
    print(Vector(line)) 