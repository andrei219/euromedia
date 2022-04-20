
from app.db import session
from app.db import Imei
from sqlalchemy.sql import  delete
from app.db import session


series = [
    '3243243',
    '0234234234',
    '234325',
    '4234'

]


if __name__ == '__main__':

    query = delete(Imei).where(Imei.imei.in_(series))
    session.execute(query)
    session.commit()

