

import pyodbc
from app.db import session, Expedition, ExpeditionSerie

TYPE = 2
NUMBER = 156
EXPEDITION_ID = 20


FACTUSOL = r'Z:\Factusol\Factusol 2017\Datos\FS\0052022.accdb'

class FactusolConectionError(BaseException):
    pass 

class Connection:
    
    instance = None 
    
    def __new__(cls):
        try:
            if cls.instance is None:
                driver = pyodbc.dataSources()['MS Access Database']
                cls.instance = pyodbc.connect(driver=driver, dbq=FACTUSOL)
                return cls.instance
            return cls.instance
        except:
            
            raise FactusolConectionError


def get_series():
    connection = Connection()
    query = "SELECT NSESLF FROM F_SLF WHERE TIPSLF=? AND CODSLF=? ORDER BY POSSLF"
    cursor = connection.cursor()
    
    return [r[0] for r in cursor.execute(query, (TYPE, NUMBER))]

def get_expedition_lines():
    expedition = session.query(Expedition).where(
        Expedition.id == EXPEDITION_ID
    ).one() 
    for line in expedition.lines:
        for i in range(line.quantity):
            yield line 

if __name__ == '__main__':
    
    for serie, line in zip(get_series(), list(get_expedition_lines())):
   
        exp_serie = ExpeditionSerie()
        exp_serie.serie = serie
        exp_serie.line = line
        
        session.add(exp_serie)
    
    session.commit() 
