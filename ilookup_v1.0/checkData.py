from app import db
from app.models import Cluster, Client, Product, Product_Release, CPRC
from db_delete_v3 import DeactivateRecords
import boto3
import json, pprint

class CheckAWSData:

	def mainFunction(self):
		london_region = "eu-west-2"
		north_virginia_region = "us-east-1"

		client = boto3.client("ecs")


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

	def checkProducts(self,region_name): 	
		client = boto3.client("ecs", region_name=region_name)
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]
		aws_products = []
		for cluster in clusters:
			tags = self.fetchClusterTags(cluster,region_name)
			if tags["Product"]:
				product_name = tags["Product"]
				aws_products.append(product_name)
		db_products = db.session.query(Product.product_name).all()

		for product_name in db_products:
			if product_name not in aws_products:
				deactivateRecords = DeactivateRecords()
				deactivateRecords.deactivateProduct(product_name)

	def checkClients(slef,region):
		client = boto3.client("ecs", region_name=region_name)
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]
		aws_clients = []
		for cluster in clusters:
			tags = self.fetchClusterTags(cluster,region_name)
			for key in tags:
				if ("Client") in key:
					client_name = tags[key]
					aws_clients.append(client_name)
					
		db_clients = db.session.query(Client.client_name).all()

		for client_name in db_clients:
			if client_name not in aws_clients:
				deactivateRecords = DeactivateRecords()
				deactivateRecords.deactivateClients(client_name)
		# for aws_client in aws_clients:
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


checkData = CheckAWSData()
checkData.checkProducts("us-east-1")
checkData.checkProducts("eu-west-2")
# checkData.checkClusters("London", "eu-west-2")