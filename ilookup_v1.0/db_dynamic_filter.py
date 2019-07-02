from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json

class DynamicFilter:

	def getFirstFilterResult(self,client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None):

			search_result = db.session.query(CPRC, Client, Product_Release, Product, Cluster).filter(CPRC.client_id == Client.client_id, CPRC.product_release_id == Product_Release.product_release_id,
				Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()

			products = []
			releases = []
			environments = []
			regions = []
			clusters = []
			clients = []
			if client_name:
				search_result = search_result.filter(Client.client_name== client_name)

			if product_name:
				search_result = search_result.filter(Product.product_name== product_name)
		
			if release:
				search_result = search_result.filter(Product_Release.release_number==release)

			if cluster_name:
				search_result = search_result.filter(Cluster.cluster_name==cluster_name)

			if region:
				search_result = search_result.filter(Cluster.region==region)

			if environment:
				search_result = search_result.filter(Cluster.environment==environment)

			# for res in search_result:
			# 		clients.append(res.Client.client_name)
			# 		products.append(res.Product.product_name)
			# 		environments.append(res.Cluster.environment)
			# 		clients.append(res.Client.client_name)
			# 		releases.append(res.Product_Release.release_number)
			# 		clusters.append(res.Cluster.cluster_name)

			# result = {}
			# result["search_result"] = search_result
			# result["products"] = products
			# result["clients"] = clients
			# result["regions"] = regions
			# result["environments"] = environments
			# result["clusters"] = clusters
			# result["releases"] = releases

			# pprint.pprint(result)
			return search_result

