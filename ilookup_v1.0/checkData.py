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


	def checkClusters(self, region_name):
		client = boto3.client("ecs", region_name=region_name)
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]
		aws_clusters = []
		for cluster in clusters:
			cluster_split = cluster.split(":")
			mysplit= cluster.split("/")
			cluster_name=mysplit[1]
			aws_clusters.append(cluster_name)

		db_clusters = db.session.query(Cluster.cluster_name).all()

		for cluster_name in db_clusters:
			if cluster_name not in aws_clusters:
				deactivateRecords = DeactivateRecords()
				deactivateRecords.deactivateClusters(cluster_name)
	
	def checkProducts(self,region_name): 	
		client = boto3.client("ecs", region_name=region_name)
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]
		aws_products = []
		for cluster in clusters:
			tags = fetchClusterTags(cluster,region_name)
			if tag["Product"]:
				product_name = tag["Product"]
				aws_products.append(product_name)
		db_products = db.session.query(Product.product_name).all()

		for product_name in db_products:
			if product_name not in aws_products:
				deactivateRecords = DeactivateRecords()
				deactivateRecords.deactivateProducts(product_name)

	def checkClients(slef,region):
		client = boto3.client("ecs", region_name=region_name)
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]
		aws_clients = []
		for cluster in clusters:
			tags = fetchClusterTags(cluster,region_name)
			for key in tags:
				if ("Client") in key:
					client_name = tags[key]
					aws_clients.append(client_name)
					
		db_clients = db.session.query(Client.client_name).all()

		for client_name in db_clientss:
			if client_name not in aws_clients:
				deactivateRecords = DeactivateRecords()
				deactivateRecords.deactivateClients(client_name)



			

	def fetchClusterTags(self,clusterArn,region_name):
		client = boto3.client("ecs", region_name=region_name)
		res = client.list_tags_for_resource(resourceArn = clusterArn)
		tagsDict =  {}
		for tag in res["tags"]:
			tagsDict[tag["key"]] = tag["value"]
		return tagsDict
