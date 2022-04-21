
from app.db import session
from app.db import Imei
from sqlalchemy.sql import  delete
from app.db import session


series = [
    'SDX3HDBFYN73D',
    'SDX3HDBG5N73D',
    'SDX3HDBGEN73D',
    'SDX3HDBH8N73D',
    'SDX3HDBHGN73D',
    'SDX3HDBJZN73D',
    'SDX3HDBK6N73D',
    'SDX3HDBK8N73D',
    'SDX3HDBKCN73D',
    'SDX3HDBL2N73D',
    'SDX3HDBG1N73D',
    'SDX3HDBG8N73D',
    'SDX3HDBGDN73D',
    'SDX3HDBGTN73D',
    'SDX3HDBH3N73D',
    'SDX3HDBJ4N73D',
    'SDX3HDBJ6N73D',
    'SDX3HDBJPN73D',
    'SDX3HDBJSN73D',
    'SDX3HDBLVN73D'
]

if __name__ == '__main__':

    from app.db import get_engine

    engine = get_engine()

    engine.echo = True


    query = delete(Imei).where(Imei.imei.in_(series))
    session.execute(query)
    session.commit()

