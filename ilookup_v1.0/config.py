import os;
import pymysql;
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get("SECRET_KEY") or "SECRET-KEY"
	#SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')'sqlite:///' + os.path.join(basedir,'app.db')

<<<<<<< HEAD
	#SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ilookupdb:ilookupdb@ilookupdb.cqoaspdapbvm.us-east-1.rds.amazonaws.com:3306/ilookup_copy"

	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Sj93299347!@127.0.0.1:3306/td-def-table"


=======
	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ilookupdb:ilookupdb@ilookupdb.cqoaspdapbvm.us-east-1.rds.amazonaws.com:3306/ilookupdbcopy"
>>>>>>> 9d3d59b21a803e8897eae6c4317196d204b90387

	SQLALCHEMY_TRACK_MODIFICATIONS = False
