from app import db
from app.models import Cluster, Client, Product, Product_Release, CPRC
from db_delete_v3 import DeactivateRecords
from addUpdateDB import AddUpdateRecords
from datetime import datetime
import boto3
import json, pprint
from regions import regionObject

class CheckAWSData:

	# def mainFunction(self):
	# 	london_region = "eu-west-2"
	# 	north_virginia_region = "us-east-1"

	# 	client = boto3.client("ecs")

	def checkData(self):
		# self.mainFunction("eu-west-2")
		for region in regionObject:
			self.mainFunction(regionObject[region])


	def checkClusters(self, region, region_name):
		uniClient = boto3.client("ecs", region_name=region_name)
		clusters = uniClient.list_clusters()
		clusters = clusters["clusterArns"]
		aws_clusters = []
		for cluster in clusters:
			cluster_split = cluster.split(":")
			mysplit= cluster.split("/")
			cluster_name=mysplit[1]
			aws_clusters.append(cluster_name)
			db_cluster_exists = db.session.query(Cluster).filter(Cluster.cluster_name==cluster_name).filter(Cluster.region==region).first()

			if db_cluster_exists:
				print(db_cluster_exists)
				if db_cluster_exists.is_active==False:
					db_cluster_exists.is_active=True
					db.session.commit()
					deactivateRecords = DeactivateRecords()
					deactivateRecords.activateComponent(db_cluster_exists.cluster_id, cluster, uniClient)
					print("activating cluster and component")

		db_clusters = db.session.query(Cluster).filter(Cluster.region==region).all()

		for cluster in db_clusters:
			cluster_name = cluster.cluster_name
			if cluster_name not in aws_clusters:
				deactivateRecords = DeactivateRecords()
				deactivateRecords.deactivateCluster(cluster_name)
				print("Deactivating cluster", cluster_name)

		# 		# Deactive CPRC
		# 		# Deactivate Task Def

	def mainFunction(self, region_name):
		client = boto3.client("ecs", region_name=region_name)
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]
		aws_products = []
		for cluster in clusters:
			tags = self.fetchClusterTags(cluster,region_name)
			cluster_name = cluster.split("/")
			cluster_name = cluster_name[1]
			# self.checkProduct(cluster_name)
			client_names = []
			for key in tags:
				if "Product" in key:
					product_name = tags[key]
				if "Client" in key:
					client_name = tags[key]
					client_names.append(client_name)
				if "Release" in key:
					release = tags[key]
				if "Environment" in key:
					environment = tags[key]

			self.checkProduct(product_name,client_names,cluster_name,release)
			self.checkClients(product_name,client_names,cluster_name,release)
			self.checkEnvironmnent(cluster_name, environment)

	def checkProduct(self,product_name,client_names,cluster_name,release):
		# activate in sql side
		# 1. check if product already exists in database-> if exists then set is_active = true else add a new entry
		# 2. find the old product and deactivate that record if to belongs to only one cluster, also deactivate cprc records
		# 3. find if there is cprc record for the new product
		#    if it is there for each client and if it is inactive-> make it as active
		#    else create new cprc records with each client in client_names list

		exists_product = db.session.query(Product).filter(Product.product_name==product_name).first()
		print(exists_product)
		if exists_product:
			exists_product.is_active = True
			product_release = db.session.query(Product_Release).filter(Product.product_id==Product_Release.product_id).filter(Product.product_name==product_name).filter(Product_Release.release_number==release).first()
			if not product_release:
				product_release = Product_Release(product_id=exists_product.product_id,release_number=release, inserted_at=datetime.utcnow())
				db.session.add(product_release)
				db.session.commit()
				print("...........////////////////////.............new product release.........................")

		else:
			product = Product(product_name=product_name, is_active=True)
			db.session.add(product)
			db.session.commit()

			print("Added new product................................................................")
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
			print(product_id)
			product_release = Product_Release(product_id=product_id[0],release_number=release, inserted_at=datetime.utcnow())
			db.session.add(product_release)
			db.session.commit()
			print("......................................................................")

		old_products= db.session.query(Product).filter(Product.product_id==Product_Release.product_id,CPRC.product_release_id==Product_Release.product_release_id,CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).all()
		print(old_products)
		for old_product in old_products:
			cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id,CPRC.cluster_id==Cluster.cluster_id).filter(Product.product_name==old_product.product_name).all()
			if cluster_count:
				if(len(cluster_count)==1):
					old_product.is_active= False
					db.session.commit()
			cprc = db.session.query(CPRC).filter(CPRC.product_release_id==Product_Release.product_release_id,Product.product_id==Product_Release.product_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).all()
			for record in cprc:
				record.is_active = False
				db.session.commit()
			# addUpdateRecord.deactivateProduct(old_product.product_name)

		addUpdateRecord = AddUpdateRecords()

		for client_name in client_names:

			exists_cprc = addUpdateRecord.checkCPRCExists(client_name,cluster_name,product_name,release)

			if exists_cprc is not None:
				if exists_cprc.is_active == False:
					exists_cprc.is_active = True
					db.session.commit()
			else:
				addUpdateRecord.addCPRC(client_name,product_name,cluster_name,release)
		print("End of check aws function")


	def checkClients(self,product_name,client_names,cluster_name,release):
		# activate in sql side
		# repeat this procedure for all clients in client_names list
		# 1. check if client already exists in database-> if exists then set is_active = true else add a new entry
		# 2. find the old client and deactivate that record if to belongs to only one cluster, also deactivate cprc records
		# 3. find if there is cprc record for the new product
		#    if it is there for each client and if it is inactive-> make it as active
		#    else create new cprc records
		for client_name in client_names:
			exists_client = db.session.query(Client).filter(Client.client_name==client_name).first()
			print(exists_client)
			if exists_client:
				exists_client.is_active = True
			else:
				client = Client(client_name=client_name, is_active=True)
				db.session.add(client)
				db.session.commit()
				print("new client is added")

			old_clients = db.session.query(Client.client_name).filter(Client.client_id==CPRC.client_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).all()
			print("list of all old clients", old_clients)

			for old_client in old_clients:
				old_client = old_client[0]
				if old_client not in client_names:
					client = db.session.query(Client).filter(Client.client_name==old_client).first()
					if client:
						cprc = db.session.query(CPRC).filter(CPRC.product_release_id==Product_Release.product_release_id,Product.product_id==Product_Release.product_id, CPRC.cluster_id==Cluster.cluster_id, CPRC.client_id==Client.client_id).filter(Cluster.cluster_name==cluster_name).filter(Client.client_name==client_name).all()
						for record in cprc:
							record.is_active = False
							db.session.commit()

						cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.client_id==client.client_id).filter(client.is_active==True).all()
						if(len(cluster_count)==1):
							client.is_active=False
							db.session.commit()

			addUpdateRecord = AddUpdateRecords()

			exists_cprc = addUpdateRecord.checkCPRCExists(client_name,cluster_name,product_name,release)
			if exists_cprc is not None:
				if exists_cprc.is_active == False:
					exists_cprc.is_active = True
					db.session.commit()
			else:
				addUpdateRecord.addCPRC(client_name,product_name,cluster_name,release)
				print("End of check client function")







		# deactivate in sql side






	# def checkProducts(self,region_name):
	# 	client = boto3.client("ecs", region_name=region_name)
	# 	clusters = client.list_clusters()
	# 	clusters = clusters["clusterArns"]
	# 	aws_products = []
	# 	for cluster in clusters:
	# 		tags = self.fetchClusterTags(cluster,region_name)
	# 		if tags["Product"]:
	# 			product_name = tags["Product"]
	# 			aws_products.append(product_name)
	# 	db_products = db.session.query(Product.product_name).all()

	# 	for product_name in db_products:
	# 		if product_name not in aws_products:
	# # 			deactivateRecords = DeactivateRecords()
	# # 			deactivateRecords.deactivateProduct(product_name)

	# def checkClients(slef,region):
	# 	client = boto3.client("ecs", region_name=region_name)
	# 	clusters = client.list_clusters()
	# 	clusters = clusters["clusterArns"]
	# 	aws_clients = []
	# 	for cluster in clusters:
	# 		tags = self.fetchClusterTags(cluster,region_name)
	# 		for key in tags:
	# 			if ("Client") in key:
	# 				client_name = tags[key]
	# 				aws_clients.append(client_name)

	# 	db_clients = db.session.query(Client.client_name).all()

	# 	for client_name in db_clients:
	# 		if client_name not in aws_clients:
	# 			deactivateRecords = DeactivateRecords()
	# 			deactivateRecords.deactivateClients(client_name)
	# 	# for aws_client in aws_clients:
		# 	if aws_client not in db_clients:
				# call populate client function

	def fetchClusterTags(self,clusterArn,region_name):
		client = boto3.client("ecs", region_name=region_name)
		res = client.list_tags_for_resource(resourceArn = clusterArn)

		mysplit= clusterArn.split("/")
		cluster_name=mysplit[1]

		print(cluster_name)
		tagsDict =  {}
		for tag in res["tags"]:
			tagsDict[tag["key"]] = tag["value"]
		return tagsDict


	def checkEnvironmnent(self, cluster_name, environment):
		cluster = db.session.query(Cluster).filter(Cluster.cluster_name==cluster_name).first()
		if cluster:
			cluster.environment= environment
			db.session.commit()



# checkData = CheckAWSData()
# checkData.checkData()
# checkData.mainFunction("us-east-1")
# checkData.checkClusters("London", "eu-west-2")
