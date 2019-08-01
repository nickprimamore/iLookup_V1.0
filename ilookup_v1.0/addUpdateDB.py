from app import db
from app.models import Client, Cluster, CPRC, Product, Product_Release, Task_Definition, Component
from datetime import datetime

class AddUpdateRecords:
	def addUpdateClient(self,old_client_name,new_client_name, product_name, cluster_name, release_number):
		exists_client = db.session.query(Client.client_name).filter(Client.client_name==new_client_name).scalar() is not None
		print(old_client_name,new_client_name, product_name, cluster_name, release_number)
		if not exists_client:
			client = Client(client_name=new_client_name, is_active=True)
			db.session.add(client)
			db.session.commit()
			print("New client is being added!!!!!!!!")
			# make the old client record as inactive 
			if old_client_name!="":
				self.deactivateClient(old_client_name)
				self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)
				
				# check if the client belongs to multiple clusters
				# if not then deactivate it
			self.addCPRC(new_client_name,product_name,cluster_name,release_number)

		if exists_client:
			client = db.session.query(Client).filter(Client.client_name == new_client_name).first()
			if client:
				client.is_active = True
				db.session.commit()
			exists_cprc  = self.checkCPRCExists(new_client_name, cluster_name, product_name, release_number)
			if exists_cprc is not None:
				#exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
				if exists_cprc.is_active == False:
					exists_cprc.is_active = True
					db.session.commit()
					self.deactivateClient(old_client_name)

					self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)
				return "Client-cprc record already exists"
			else:
				self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)
				self.addCPRC(new_client_name,product_name,cluster_name,release_number)


	def checkCPRCExists(self,client_name, cluster_name, product_name, release_number):
		print(product_name, ">>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<KKKKKKKKKKKKSSSSSSSSSSSSSS")
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		print(product_id)
		if (client_id and product_id and cluster_id):
			product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
			print(product_release_id)
			if product_release_id:
				exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
				return exists_cprc
		#return False


	def addUpdateProduct(self,old_product_name,new_product_name,client_names, cluster_name,release_number):
		new_product_id = db.session.query(Product.product_id).filter_by(product_name=new_product_name).first()

		if new_product_id is not None:
			print("product already exists")
			new_product_id = new_product_id[0]
			product_release = db.session.query(Product_Release).filter(Product.product_id==Product_Release.product_id).filter(Product.product_name==new_product_name).filter(Product_Release.release_number==release_number).first()
			if not product_release:
				product_release = Product_Release(product_id=new_product_id,release_number=release_number, inserted_at=datetime.utcnow())
				db.session.add(product_release)
				db.session.commit()
				print("new product release added for existing product..................................")
		# product_id = product_id[0]
		#print(product_id)
		exists_product = db.session.query(Product.product_id).filter_by(product_id=new_product_id).scalar() is not None
		#print("New entry is added in product table")y(Product.product_id).filter_by(product_id=product_id).scalar() is not None
		old_product_id = db.session.query(Product.product_id).filter_by(product_name=old_product_name).first()
		if old_product_id:
			cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id, Product.product_id==Product_Release.product_id).filter(Product.product_id==old_product_id[0]).distinct().all()
			print(cluster_count)

			if len(cluster_count)==1:
				print("only one cluster and one product")
				old_product_id = db.session.query(Product.product_id).filter_by(product_name=old_product_name).first()
				product = db.session.query(Product).filter(Product.product_id==old_product_id[0]).first()
				product.is_active = False
			
			if exists_product:
				# exists_product = db.session.query(Product.product_id).filter_by(product_id=product_id).all()

				for client_name in client_names:
					# self.deactivateCPRC(client_name, old_product_name, cluster_name, release_number)
					# print("Going ionto addCPRC function")
					# self.addCPRC(client_name, new_product_name, cluster_name, release_number)
					# print("Product already exists in database")
					self.updateCPRC(client_name, old_product_name, new_product_name, cluster_name, release_number)
			else:
				productValue = Product(product_name=new_product_name, is_active=True)
				db.session.add(productValue)
				db.session.commit()
				product_id = db.session.query(Product.product_id).filter_by(product_name=new_product_name).first()
				print(product_id[0])
				inserted_at = datetime.utcnow()
				product_release = Product_Release(product_id=product_id[0], release_number=release_number, inserted_at = inserted_at)
				db.session.add(product_release)
				db.session.commit()
				for client_name in client_names:
					# self.deactivateCPRC(client_name, old_product_name, cluster_name, release_number)
					# self.addCPRC(client_name, new_product_name, cluster_name, release_number)
					self.updateCPRC(client_name, old_product_name, new_product_name, cluster_name, release_number)
				

			db.session.commit()

			#

	# def addUpdateEnvironment(cluster_name, environment):

	# def updateRelease(product_name, release_number, client_name, cluster_name)

	def deactivateCPRC(self,client_name, product_name, cluster_name, release_number):
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
		print(client_id)
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		print(cluster_id)
		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		print(product_id)
		if (product_id and client_id and cluster_id) :
			product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
			print(product_release_id)
			if product_release_id:
				cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
				print(cprc)
				if cprc:
					cprc.is_active = False
					db.session.commit()
					print("............................................Deactivated CPRC...............................")
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
		print(release_number)
		product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
		print(product_release_id)
		print("<<<<<<<<<<<<<<<<<<<<<<<<<<<")
		# cprc = CPRC(client_id=client_id, cluster_id=cluster_id, product_release_id=product_release_id)
		# db.session.add(cprc)
		# db.session.commit()
		# return "Added CPRC record"

		if (client_id and cluster_id and product_release_id):
			cprc_value = CPRC(client_id=client_id[0], cluster_id=cluster_id[0], product_release_id=product_release_id[0])
			db.session.add(cprc_value)
				#print('inserted new record in product_release table')
			db.session.commit()
			print("Added new record in CPRC")

	def updateEnvironment(self,cluster_name,environment):
		cluster = db.session.query(Cluster).filter(Cluster.cluster_name==cluster_name).first()
		cluster.environment = environment
		db.session.commit()

		# need to update this function
	def updateProductRelease(self, product_name, cluster_name, old_release_number, new_release_number):
		exists = self.checkRelease(product_name, cluster_name, old_release_number, new_release_number)
		if exists:
			return True
		else:
			product_release_exists = True
			print( product_name, old_release_number, new_release_number)
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
			product_id = product_id[0]
			print(new_release_number, old_release_number)
			print(product_id)
			product_release_number = db.session.query(Product_Release).filter(Product_Release.product_id==product_id).filter(Product_Release.release_number==old_release_number).first()
			print("product_release_number before",product_release_number)
			product_release_number.release_number = new_release_number 
			db.session.commit()
			print("product_release_number after", product_release_number)
			print("......................................updated Product_Release...................................")
			return False

	def updateTaskDefinition(self, cluster_name, old_release_number, new_release_number):
		search_result = db.session.query(Task_Definition).filter(Cluster.cluster_id==Component.cluster_id,Component.component_id==Task_Definition.component_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.release_number==old_release_number).all()
		print(search_result)
		for res in search_result:
			res.release_number = new_release_number
		db.session.commit()
		print("......................................updated Task_Definition...................................")


	#### Check validation for inserting new release number

	def checkRelease(self, product_name, cluster_name, old_release_number, new_release_number):
		exists = False
		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		exists_product_release = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==new_release_number).scalar() is not None

		if exists_product_release:
			product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==new_release_number).first()
			exists_cprc = db.session.query(CPRC.cprc_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==product_release_id[0]).filter(Cluster.cluster_name==cluster_name).scalar() is not None

			if exists_cprc:
				exists = True
		return exists

	def deactivateClient(self, client_name):
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()

		if client_id:
			client_id = client_id[0]
			print(client_id)
			

			cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.client_id==client_id).distinct().all()
			print(cluster_count)

			if(len(cluster_count)==1):
				client = db.session.query(Client).filter(Client.client_name==client_name).first()
				client.is_active = False
				db.session.commit()


	def updateCPRC(self,client_name, old_product_name, new_product_name, cluster_name, release_number):
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		cluster_id = cluster_id[0]
		print("cluster",cluster_id)
		old_product_id = db.session.query(Product.product_id).filter(Product.product_name==old_product_name).first()
		old_product_id = old_product_id[0]
		print("old product id",old_product_id)
		new_product_id = db.session.query(Product.product_id).filter(Product.product_name==new_product_name).first()
		new_product_id = new_product_id[0]
		print("new product id", new_product_id)
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
		client_id = client_id[0]
		print("client id",client_id)
		old_product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==old_product_id).first()
		old_product_release_id = old_product_release_id[0]
		print("old prid",old_product_release_id)
		new_product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==new_product_id).first()
		new_product_release_id = new_product_release_id[0]
		print("new prid",new_product_release_id)
		cprc = db.session.query(CPRC).filter(CPRC.product_release_id==old_product_release_id).filter(CPRC.cluster_id==cluster_id).filter(CPRC.client_id==client_id).first()
		print(">?????????????????><<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
		print(cprc)
		cprc.product_release_id = new_product_release_id

		db.session.commit()

	# def updateProductRelease(self,old_product_name,new_product_name,release_number):
	# 	old_product_id = db.session.query(Product.product_id).filter(Product.product_name==old_product_name).first()
	# 	new_product_id = db.session.query(Product.product_id).filter(Product.product_name==new_product_name).first()
	# 	product_release = db.session.query(Product_Release).filter(Product_Release.product_id==old_product_id).filter(Product_Release.release_number==release_number).first()
	# 	product_release.product_id=new_product_id
	# 	db.session.commit()