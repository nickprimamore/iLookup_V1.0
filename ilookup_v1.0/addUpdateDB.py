from app import db
from app.models import Client, Cluster, CPRC, Product, Product_Release, Task_Definition, Component
from datetime import datetime
import sys

f=open("errorLog.txt", "a+")

#this class is used to add/update database records when someone changes aws tags
class AddUpdateRecords:

	#this function add/update the client records and also creates new cprc record for the new client
	# and deactivates all records for the old client(deactivates record in client and CPRC table)
	def addUpdateClient(self,old_client_name,new_client_name, product_name, cluster_name, release_number):

		try:
			#check if the new client already exists or not
			exists_client = db.session.query(Client.client_name).filter(Client.client_name==new_client_name).scalar() is not None

			#if not exists then add new client record
			if not exists_client:
				client = Client(client_name=new_client_name, is_active=True)
				db.session.add(client)
				db.session.commit()
				print("New client is being added!!!!!!!!")

				# make the old client record as inactive
				if old_client_name!="":
					self.deactivateClient(old_client_name)
					self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)

				#add new cprc record with new client
				self.addCPRC(new_client_name,product_name,cluster_name,release_number)

			#if the new client already exists then mark it as active client, deactivate cprc for old and add new cprc record
			if exists_client:
				client = db.session.query(Client).filter(Client.client_name == new_client_name).first()
				if client:
					client.is_active = True
					db.session.commit()
				exists_cprc  = self.checkCPRCExists(new_client_name, cluster_name, product_name, release_number)

				#if the cprc entry already exists then make it as active
				if exists_cprc is not None:
					if exists_cprc.is_active == False:
						exists_cprc.is_active = True
						db.session.commit()
						self.deactivateClient(old_client_name)

						self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)
					return "Client-cprc record already exists"
				#else add new cprc record and deactivate the old record
				else:
					self.deactivateCPRC(old_client_name, product_name, cluster_name, release_number)
					self.addCPRC(new_client_name,product_name,cluster_name,release_number)
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: addUpdateClient - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#this function checks if cprc record already exists and returns the boolean value
	def checkCPRCExists(self,client_name, cluster_name, product_name, release_number):
		try:
			client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
			cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()

			if (client_id and product_id and cluster_id):
				product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
				print(product_release_id)
				if product_release_id:
					exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
					return exists_cprc
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: checkCPRCExists - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	#this function add/update the product and corresponding CPRC record
	# 1. It checks if the new product exist or not if there is new product then, it creates new record for that product
	# 2. It checks for product release for new product, if not exist then creates the new reocrd
	# 3. Updates the cprc for the new product, replaces the old product_release_id with the new_product_release by calling updateCPRC() function
	def addUpdateProduct(self,old_product_name,new_product_name,client_names, cluster_name,release_number):

		try:
			print(old_product_name,new_product_name,client_names, cluster_name,release_number)
			#checks if new product exists or not
			new_product_id = db.session.query(Product.product_id).filter_by(product_name=new_product_name).first()

			#if new product exists then checks for product release record for that function.. if there is not product_release record then creates one
			if new_product_id is not None:
				new_product_id = new_product_id[0]
				product_release = db.session.query(Product_Release).filter(Product.product_id==Product_Release.product_id).filter(Product.product_name==new_product_name).filter(Product_Release.release_number==release_number).first()
				if not product_release:
					product_release = Product_Release(product_id=new_product_id,release_number=release_number, inserted_at=datetime.utcnow())
					db.session.add(product_release)
					db.session.commit()


			exists_product = db.session.query(Product.product_id).filter_by(product_id=new_product_id).scalar() is not None

			#checks if old product belongs to more than one cluster -> if it belongs to only one cluster then deactivate that record
			old_product_id = db.session.query(Product.product_id).filter_by(product_name=old_product_name).first()
			if old_product_id:
				cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id, Product.product_id==Product_Release.product_id).filter(Product.product_id==old_product_id[0]).distinct().all()
				print(cluster_count)

				if len(cluster_count)==1:
					print("only one cluster and one product")
					old_product_id = db.session.query(Product.product_id).filter_by(product_name=old_product_name).first()
					product = db.session.query(Product).filter(Product.product_id==old_product_id[0]).first()
					product.is_active = False
					db.session.commit()

				# if new client already exists then then only update the cprc record
				# else add new product, product_release record and update the CPRC record
				if exists_product:
					for client_name in client_names:
						self.updateCPRC(client_name, old_product_name, new_product_name, cluster_name, release_number)
				else:
					productValue = Product(product_name=new_product_name, is_active=True)
					print(">>>>>>>>>>>>>>>>>>>>>>VVVVVVVVVVVVVVVVVVVVVVVVVV<<<<<<<<<<<<<<<<<<<<")
					print('product',productValue)
					db.session.add(productValue)
					db.session.commit()
					product_id = db.session.query(Product.product_id).filter_by(product_name=new_product_name).first()
					print('product id',product_id)
					inserted_at = datetime.utcnow()
					print('release_number',release_number)
					product_release = Product_Release(product_id=product_id[0], release_number=release_number, inserted_at = inserted_at)
					print('product_release',product_release)
					db.session.add(product_release)
					db.session.commit()
					for client_name in client_names:
						print('client name',client_name)
						print("updating cprc")
						self.updateCPRC(client_name, old_product_name, new_product_name, cluster_name, release_number)
						print(client_name, old_product_name, new_product_name, cluster_name, release_number)
					print(">>>>>>>>>>>>>>>>>>>>>>VVVVVVVVVVVVVVVVVVVVVVVVVV<<<<<<<<<<<<<<<<<<<<")
				db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: addUpdateProduct - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	# deactivates the CPRC record for the given arguments
	def deactivateCPRC(self,client_name, product_name, cluster_name, release_number):

		try:
			client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
			cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
			if (product_id and client_id and cluster_id) :
				product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()
				if product_release_id:
					cprc = db.session.query(CPRC).filter_by(client_id=client_id[0]).filter_by(cluster_id=cluster_id[0]).filter_by(product_release_id=product_release_id[0]).first()
					if cprc:
						cprc.is_active = False
						db.session.commit()
						return "Deactivated old cprc record"
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: deactivateCPRC - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	# adds new cprc record in the database
	def addCPRC(self,client_name, product_name, cluster_name, release_number):

		try:
			client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
			cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
			product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==release_number).first()

			if (client_id and cluster_id and product_release_id):
				cprc_value = CPRC(client_id=client_id[0], cluster_id=cluster_id[0], product_release_id=product_release_id[0])
				db.session.add(cprc_value)
				db.session.commit()
				print("Added new record in CPRC")
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: addCPRC - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	#uodates the environment for the given cluster
	def updateEnvironment(self,cluster_name,environment):

		try:
			cluster = db.session.query(Cluster).filter(Cluster.cluster_name==cluster_name).first()
			cluster.environment = environment
			db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: updateEnvironment - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	#updates product_release record
	def updateProductRelease(self, product_name, cluster_name, old_release_number, new_release_number):

		try:
			new_product_release_id = self.checkRelease(product_name, cluster_name, old_release_number, new_release_number)
			print( product_name, cluster_name, old_release_number, new_release_number)

			#hecks if the record already exists, if not then add the new record
			if new_product_release_id:
				print("release number already exists")
			else:
				product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
				product_release = Product_Release(product_id=product_id[0], release_number=new_release_number, inserted_at=datetime.utcnow())
				db.session.add(product_release)
				db.session.commit()
				print(product_release.release_number)

				print("added new product release")
				new_product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==new_release_number).first()
				print(new_product_release_id)
				#new_product_release_id = new_product_release_id[0]

			#update cprc record with new product_release_id
			cprc = db.session.query(CPRC).filter(CPRC.cluster_id==Cluster.cluster_id, Product_Release.product_release_id==CPRC.product_release_id).filter(Cluster.cluster_name==cluster_name).filter(Product_Release.release_number==old_release_number).distinct().all()

			print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTT',cprc)
			if(len(cprc)>0):
				for record in cprc:
					print("record.product_release_id",record.product_release_id)
					print(new_product_release_id)
					if isinstance(new_product_release_id, int):
						print("i am in isinstance if condition")
						record.product_release_id=new_product_release_id
					else:
						record.product_release_id=new_product_release_id[0]
				db.session.commit()

				print("updates the cprc records")
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: updateProductRelease - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#updates the task definition, replaces old_release_number with new_release_number
	def updateTaskDefinition(self, cluster_name, old_release_number, new_release_number):

		try:
			print("....................... i am in task definition..........................")
			print(cluster_name, old_release_number, new_release_number)
			# changed is active for task def
			search_result = db.session.query(Task_Definition).filter(Cluster.cluster_id==Component.cluster_id,Component.component_id==Task_Definition.component_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.release_number==old_release_number).all()
			print(search_result)
			for res in search_result:
				res.release_number = new_release_number
			db.session.commit()
			print("Updated task definition!!!")
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: updateTaskDefinition - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#Check validation for inserting new release number
	def checkRelease(self, product_name, cluster_name, old_release_number, new_release_number):

		try:
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
			product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id[0]).filter(Product_Release.release_number==new_release_number).first()
			print("product_id", product_id)
			print("product_release_id", product_release_id)
			if product_release_id:
				product_release_id = product_release_id[0]
				print("new release number already exists")
				return product_release_id
			else:
				return None

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: checkRelease - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#deactivates the client record if it belongs to only one cluster
	def deactivateClient(self, client_name):

		try:
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

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: deactivateClient - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	#updates the cprc record, changes product_release_id with new product_release_id
	def updateCPRC(self,client_name, old_product_name, new_product_name, cluster_name, release_number):

		try:
			print(client_name, old_product_name, new_product_name, cluster_name, release_number)
			cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
			cluster_id = cluster_id[0]
			print(cluster_id)
			old_product_id = db.session.query(Product.product_id).filter(Product.product_name==old_product_name).first()
			old_product_id = old_product_id[0]
			print(old_product_id)
			new_product_id = db.session.query(Product.product_id).filter(Product.product_name==new_product_name).first()
			new_product_id = new_product_id[0]
			print(new_product_id)
			client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
			client_id = client_id[0]
			print(client_id)
			old_product_release_id = db.session.query(Product_Release.product_release_id).filter(CPRC.product_release_id==Product_Release.product_release_id,Cluster.cluster_id==CPRC.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Product_Release.product_id==old_product_id).filter(CPRC.is_active==True).first()
			old_product_release_id = old_product_release_id[0]
			print(old_product_release_id)
			new_product_release_id = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==new_product_id).filter(Product_Release.release_number==release_number).first()
			new_product_release_id = new_product_release_id[0]
			print(new_product_release_id)
			cprc = db.session.query(CPRC).filter(CPRC.product_release_id==old_product_release_id).filter(CPRC.cluster_id==cluster_id).filter(CPRC.client_id==client_id).first()
			print(cprc)
			cprc.product_release_id = new_product_release_id

			db.session.commit()

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: addUpdateDB.py - Function: updateCPRC - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()
