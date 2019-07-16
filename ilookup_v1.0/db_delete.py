from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json, boto3

class UpdateRecords:

	#def updateProductisActiveStatus(self, product_name,):

		#fetch list of all active products from aws


		#fetch list of all active products from database
		#activeProducts = db.session.query(Product.product_name).filter(Product.is_active=True)

		#for the given product name check if it belong to other cluster
		#checkForMultiple = db.session.query(Product.product_name).filter(Product.product_id==Product_Release.product_id, CPRC.product_release_id==Product_Release.product_release_id)

	def makeProductInactive

	def getClusterArn(self, cluster_name, region_name):
		client = boto3.client("ecs", region_name=region_name)
		cluster_list = client.list_clusters()
		cluster_list = cluster_list["clusterArns"]
		for cluster in cluster_list:
			if cluster_name in cluster:
				return cluster
		return None

	def fetchClusterTags(self,cluster_name,region_name):
		client = boto3.client("ecs", region_name=region_name)
		clusterArn = self.getClusterArn(cluster_name, region_name)
		res = client.list_tags_for_resource(resourceArn = clusterArn)
		tagsDict =  {}
		tagsDict["cluster_name"] = cluster_name
		for tag in res["tags"]:
			tagsDict[tag["key"]] = tag["value"]
		print(tagsDict)
		return tagsDict   


                                      
update = UpdateRecords()
update.fetchClusterTags("asg-uat-iconductor-cluster","eu-west-2")