

from sqlalchemy import create_engine
from app.db import url
from sqlalchemy import MetaData

''' Copy empty Mysql Database into another Database '''
def copy():
	original_engine = create_engine(url.format(db_name='euromediadb'))

	metadata = MetaData(bind=original_engine)
	metadata.reflect()


	metadata.create_all(bind=create_engine(url.format(db_name='capitaldb')))


if __name__ == '__main__':

    copy()