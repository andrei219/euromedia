from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

prod_engine = create_engine('mysql+mysqlconnector://andrei:hnq#4506@192.168.2.253:3306/appdb', echo=False) 

dev_engine = create_engine('mysql+mysqlconnector://root:hnq#4506@localhost:3306/appdb_dev', echo=False) 




