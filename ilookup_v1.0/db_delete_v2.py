from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json, boto3

class DeactivateRecords:

	def deactiveClient(self, client_name=None, cluster_name=None):
		client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
		client_id = client_id[0]
		print(client_id)
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		cluster_id = cluster_id[0]
		cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.client_id==client_id).distinct().all()
		print(cluster_count)
		if(len(cluster_count)>1):
			#just disable the cprc record 
			cprc_records = db.session.query(CPRC).filter(CPRC.client_id==client_id).filter(CPRC.cluster_id==cluster_id).all()
			for cprc in cprc_records:
				cprc.is_active = False
	
		else:
			#deactivate client and cprc 
			print("only one cluster and one client")
			client = db.session.query(Client).filter(Client.client_id==client_id).first()
			client.is_active = False
			cprc_records = db.session.query(CPRC).filter(CPRC.client_id==client_id).filter(CPRC.cluster_id==cluster_id).all()
			#print(CPRC.is_active)
			for cprc in cprc_records:
				cprc.is_active = False

		db.session.commit()
	
	def deactivateProduct(self, product_name=None, cluster_name=None):

		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		product_id = product_id[0]
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		cluster_id = cluster_id[0]
		cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id, Product.product_id==Product_Release.product_id).filter(Product.product_id==product_id).distinct().all()
		print(cluster_count)

		#if len(cluster_count)>1:
		



	def deactivateCluster(self, cluster_name):	
		cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
		cluster_id = cluster_id[0]
		cluster = db.session.query(Cluster).filter(Cluster.cluster_id==cluster_id).first()
		cluster.is_active = False

		#deactivating cprc records 
		cprc_records = db.session.query(CPRC).filter(CPRC.cluster_id==cluster_id).all()
			#print(CPRC.is_active)
		for cprc in cprc_records:
			cprc.is_active = False

		db.session.commit()



	#def updateProductisActiveStatus(self, product_name,):

		#fetch list of all active products from aws


		#fetch list of all active products from database
		#activeProducts = db.session.query(Product.product_name).filter(Product.is_active=True)

		#for the given product name check if it belong to other cluster
		#checkForMultiple = db.session.query(Product.product_name).filter(Product.product_id==Product_Release.product_id, CPRC.product_release_id==Product_Release.product_release_id)

	# def makeProductInactive

	# def getClusterArn(self, cluster_name, region_name):
	# 	client = boto3.client("ecs", region_name=region_name)
	# 	cluster_list = client.list_clusters()
	# 	cluster_list = cluster_list["clusterArns"]
	# 	for cluster in cluster_list:
	# 		if cluster_name in cluster:
	# 			return cluster
	# 	return None

	# def fetchClusterTags(self,cluster_name,region_name):
	# 	client = boto3.client("ecs", region_name=region_name)
	# 	clusterArn = self.getClusterArn(cluster_name, region_name)
	# 	res = client.list_tags_for_resource(resourceArn = clusterArn)
	# 	tagsDict =  {}
	# 	tagsDict["cluster_name"] = cluster_name
	# 	for tag in res["tags"]:
	# 		tagsDict[tag["key"]] = tag["value"]
	# 	print(tagsDict)
	# 	return tagsDict   


                                      
update = DeactivateRecords()
#update.deactiveClient(client_name="Aon")
update.deactivateProduct(product_name="iVerify")

# update.fetchClusterTags("asg-uat-iconductor-cluster","eu-west-2")