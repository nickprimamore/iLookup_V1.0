import os;
import pymysql;
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get("SECRET_KEY") or "SECRET-KEY"
	#SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')'sqlite:///' + os.path.join(basedir,'app.db')


	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ilookupdb:ilookupdb@ilookupdb.cqoaspdapbvm.us-east-1.rds.amazonaws.com:3306/ilookupdbcopy"

	SQLALCHEMY_TRACK_MODIFICATIONS = False
