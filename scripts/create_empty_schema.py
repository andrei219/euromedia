

from sqlalchemy import create_engine
from sqlalchemy import MetaData

url_template = "mysql+mysqlconnector://{host}/{db_name}"


''' Copy empty Mysql Database into another Database '''
''' Arguments are complete urls '''
def copy(origin, destination):
	original_engine = create_engine(origin)

	metadata = MetaData(bind=original_engine)
	metadata.reflect()

	metadata.create_all(bind=create_engine(destination))


if __name__ == '__main__':

	new_host: str = ''
	original_host: str = ''

	choices = ['dev', 'prod']
	url_template = "mysql+mysqlconnector:{host}/{db_name}"

	''' Parse four arguments: host1 dbname1 host2 dbname2 '''
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('host1', help='Host of the first database',
	                    choices=choices)
	parser.add_argument('dbname1', help='Name of the first database')
	parser.add_argument('host2', help='Host of the second database',
	                    choices=choices)
	parser.add_argument('dbname2', help='Name of the second database')
	args = parser.parse_args()


	if args.host1 == 'dev':
		original_host = '//root:hnq#4506@localhost:3306'
	elif args.host1 == 'prod':
		original_host = '//andrei:hnq#4506@192.168.1.78:3306'

	if args.host2 == 'dev':
		new_host = '//root:hnq#4506@localhost:3306'
	elif args.host2 == 'prod':
		new_host = '//andrei:hnq#4506@192.168.1.78:3306'

	copy(
		url_template.format(host=original_host, db_name=args.dbname1),
		destination=url_template.format(host=new_host, db_name=args.dbname2)
	)

	print('Done')
