from app import db
from app.models import Client, Cluster, CPRC, Product, Product_Release

class AddUpdateRecords:
	def addUpdateClient(self,old_client_name,new_client_name, product_name, cluster_name, release_number):
		exists_client = db.session.query(Client.client_name).filter(Client.client_name==new_client_name).first()
		if not exists_client:
			client = Client(client_name=new_client_name, is_active=True)
			db.session.add(client)
			db.session.commit()
			self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)
			self.addCPRC(new_client_name,product_name,cluster_name,release_number)
		if exists_client:
			exists_cprc  = self.checkCPRCExists(new_client_name, cluster_name, product_name, release_number)
			if exists_cprc is not None:
				#exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
				if exists_cprc.is_active == False:
					exists_cprc.is_active = True
					db.session.commit()
					self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)


				return "Client-cprc record already exists" 
			else:
				self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)
				self.addCPRC(new_client_name,product_name,cluster_name,release_number)


	def checkCPRCExists(self,client_name, cluster_name, product_name, release_number):
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		print(product_id)
		product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
		print(product_release_id)
		exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
		#if exists_cprc:
		return exists_cprc
		#return False

	# def addUpdateProduct(product_name):

	# def addUpdateEnvironment(cluster_name, environment):

	# def updateRelease(product_name, release_number, client_name, cluster_name)

	def deactivateCPRC(self,client_name, product_name, cluster_name, release_number):
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
		print(client_id)
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		print(cluster_id)
		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		print(product_id)
		product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
		print(product_release_id)
		cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
		print(cprc)
		cprc.is_active = False
		db.session.commit()
		return "Deactivated old cprc record"
		# set old_client to deactivate

	def addCPRC(self,client_name, product_name, cluster_name, release_number):
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
		print(client_id)
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		print(cluster_id)
		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		print(product_id)
		product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
		print(product_release_id)
		print("<<<<<<<<<<<<<<<<<<<<<<<<<<<")
		# cprc = CPRC(client_id=client_id, cluster_id=cluster_id, product_release_id=product_release_id)
		# db.session.add(cprc)
		# db.session.commit()
		# return "Added CPRC record"

		cprc_value = CPRC(client_id=client_id[0], cluster_id=cluster_id[0], product_release_id=product_release_id[0])
		db.session.add(cprc_value)
			#print('inserted new record in product_release table')
		db.session.commit()
		print("Added new record in CPRC")

	def updateEnvironment(self,cluster_name,environment):
		cluster = db.session.query(Cluster).filter(Cluster.cluster_name==cluster_name).first()
		cluster.environment = environment
		db.session.commit()
