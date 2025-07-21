# coding: utf-8
import pyodbc

dbpath = "C:\\Users\\Andrei\\Desktop\\euromedia\\data\\FS\\live\\005{year}.accdb"

class Connection:
    _cnx = None
  
    _cnx: dict[int, pyodbc.Connection] = {}

    def __new__(cls, *, year:int):
        driver = pyodbc.dataSources()['MS Access Database']

        if year not in cls._cnx:
            cls._cnx[year] = pyodbc.connect(driver=driver, dbq=dbpath.format(year=year))
        return cls._cnx[year]

            
    def __repr__(self):
        return repr(self._cnx)

ss = "SELECT DISTINCT F_SLF.NSESLF AS SERIE FROM F_SLF"


clients = """
    SELECT DISTINCT
        F_FAC.CLIFAC AS CID, 
        F_FAC.CNOFAC AS CNAME
    FROM 
        F_SLF, F_LFA, F_FAC
    WHERE 
        F_LFA.TIPLFA = F_SLF.TIPSLF AND
        F_LFA.CODLFA = F_SLF.CODSLF AND
        F_LFA.POSLFA = F_SLF.POSSLF AND
        F_FAC.TIPFAC = F_LFA.TIPLFA AND
        F_FAC.CODFAC = F_LFA.CODLFA;
"""

salesq = """
SELECT 
    F_SLF.NSESLF AS SERIE,
    F_FAC.TIPFAC AS TIPO_VENTA,
    F_FAC.CODFAC AS NUMERO_VENTA,
    F_FAC.FECFAC AS FECHA_VENTA,
    F_FAC.CNOFAC AS CLIENTE,
    F_FAC.CNIFAC AS CLIENTE_NIF,
    F_LFA.DESLFA AS ARTICULO,
    F_LFA.CANLFA AS CANTIDAD,
    F_LFA.PRELFA AS PRECIO_VENTA
FROM 
    F_SLF, F_LFA, F_FAC
WHERE 
    F_LFA.TIPLFA = F_SLF.TIPSLF AND
    F_LFA.CODLFA = F_SLF.CODSLF AND
    F_LFA.POSLFA = F_SLF.POSSLF AND
    F_FAC.TIPFAC = F_LFA.TIPLFA AND
    F_FAC.CODFAC = F_LFA.CODLFA AND 
    F_FAC.CLIFAC = {client}
"""

purchq ="""
SELECT 
    F_SLR.NSESLR AS SERIE,
    F_FRE.TIPFRE AS TIPO_COMPRA,
    F_FRE.CODFRE AS NUMERO_COMPRA,
    F_FRE.FECFRE AS FECHA_COMPRA,
    F_FRE.PNOFRE AS PROVEEDOR,
    F_FRE.FACFRE AS DOCUMENTO_PROVEEDOR,
    F_LFR.CANLFR AS CANTIDAD,
    F_LFR.PRELFR AS PRECIO_COMPRA
FROM 
    F_SLR, F_LFR, F_FRE
WHERE 
    F_LFR.TIPLFR = F_SLR.TIPSLR AND
    F_LFR.CODLFR = F_SLR.CODSLR AND
    F_LFR.POSLFR = F_SLR.POSSLR AND
    F_FRE.TIPFRE = F_LFR.TIPLFR AND
    F_FRE.CODFRE = F_LFR.CODLFR
"""


