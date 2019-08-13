from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json
import boto3
# from awsdata import AWSData
from datetime import datetime
import sys

f=open("errorLog.txt", "a+")
class Update_Release:

	def populateProductRelease(self, product_name, release_number):
		try:
			product_id = db.session.query(Product.product_id).filter_by(product_name=product_name).first()
			product_id = product_id[0]
			print(product_id)
			exists_product_release = db.session.query(Product_Release.product_release_id).filter_by(product_id=product_id).filter_by(release_number=release_number).scalar() is not None

			print(exists_product_release)
			if exists_product_release:
				print("already exists record for product_release")

			else:
				product_release_value = Product_Release(product_id=product_id, release_number=release_number)
				db.session.add(product_release_value)
				print('inserted new record in product_release table')

			product_release_id = db.session.query(Product_Release.product_release_id).filter_by(product_id=product_id).filter_by(release_number=release_number).first()
			product_release_id = product_release_id[0]
			print(product_release_id)

			db.session.commit()
			return product_release_id
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_update_release.py - Function: populateProductRelease - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()



	def populateCPRC(self, cluster_name, product_release_id):
		try:
			#fetch the cluster id
			cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster_name).first()
			print(cluster_id)

			cluster_id = cluster_id[0]
			print(cluster_id)

			#get the client id list
			client_ids = db.session.query(CPRC.client_id).filter_by(cluster_id=cluster_id).all()

			#print(client_ids)

			#check for the existing record
			#insert the new record
			for client_id in client_ids:

				client_id = client_id[0]
				print(client_id)
				exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id).filter_by(cluster_id=cluster_id).filter_by(product_release_id=product_release_id).scalar() is not None

				print(exists_cprc)
				if exists_cprc:
					print("already exists record for cprc")
				else:
					cprc_value = CPRC(client_id=client_id, cluster_id=cluster_id, product_release_id=product_release_id)
					db.session.add(cprc_value)
					print('inserted new record in product_release table')
			db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_update_release.py - Function: populateCPRC - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	def populateTaskDefinition(self, cluster):
		try:
			cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster).first()
			awsdata = AWSData()
			awsdata.populateComponent(cluster_id, cluster)

			db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_update_release.py - Function: populateTaskDefinition - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()
# insert = Update_Release()
# product_release_id = insert.populateProductRelease('iForms', '1.1.1.2')
# print('product_release_id is: ' + str(product_release_id))
# insert.populateCPRC('Marsh-Willis-dev-iForms-cluster', product_release_id )
