


from app.db import * 

copy_engine = create_engine('mysql+mysqlconnector://root:hnq#4506@localhost:3306/appdb_copy', echo=False)

engine = create_engine('mysql+mysqlconnector://root:hnq#4506@localhost:3306/appdb', echo=False)


copy_Session = sessionmaker(bind=copy_engine)

Session = sessionmaker(bind=engine)

from sqlalchemy.orm import make_transient

csession = copy_Session()
session = Session()

for sale in session.query(SaleProforma):

    make_transient(sale)
    csession.add(sale)

for line in session.query(SaleProformaLine):
    make_transient(line)
    csession.add(line) 


csession.commit() 