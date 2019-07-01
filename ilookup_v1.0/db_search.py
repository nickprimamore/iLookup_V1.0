from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json
class Search:

	def getSearchResult(self,client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None):
		
		search_result = db.session.query(CPRC, Client, Product_Release, Product, Cluster).filter(CPRC.client_id == Client.client_id, CPRC.product_release_id == Product_Release.product_release_id, 
			Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()
		   
		
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

		task_definitions = []
		results = []
		for res in search_result:
			result = {}
			result['client_name'] = res.Client.client_name
			result['product_name'] = res.Product.product_name
			result['release'] = res.Product_Release.release_number
			result['cluster_name'] = res.Cluster.cluster_name
			result['region'] = res.Cluster.region
			result['environment'] = res.Cluster.environment
			print(result)

			if (toDate and fromDate) is None:
				#print("toDate and fromDate is None")
				task_definition_result = db.session.query(Cluster, Component, Task_Definition).filter(Component.cluster_id == Cluster.cluster_id, Component.component_id == Task_Definition.component_id).filter(Cluster.cluster_name==res.Cluster.cluster_name).all()
				task_definition_list = []
				for task_definition in task_definition_result:
					task = {}
					#print(task_definition.Task_Definition.task_definition_name)
					task["task_definition_name"] = task_definition.Task_Definition.task_definition_name
					task["image_tag"] = task_definition.Task_Definition.image_tag
					task["revision"] = task_definition.Task_Definition.revision
					task["date"] = task_definition.Task_Definition.date
					task["cpu"] = task_definition.Task_Definition.cpu
					task["memory"] = task_definition.Task_Definition.memory
					task_definition_list.append(task)
				result["task_definitions"] = task_definition_list
				results.append(result)

			if (toDate and fromDate) is not None:
				print("toDate and fromDate")
				task_definition_result = db.session.query(Cluster, Component, Task_Definition).filter(Component.cluster_id == Cluster.cluster_id, Component.component_id == Task_Definition.component_id).filter(Cluster.cluster_name==res.Cluster.cluster_name).filter(Task_Definition.date >= fromDate).filter(Task_Definition.date <= toDate).all()
				task_definition_list = []
				for task_definition in task_definition_result:
					task = {}
					task["task_definition_name"] = task_definition.Task_Definition.task_definition_name
					task["image_tag"] = task_definition.Task_Definition.image_tag
					task["revision"] = task_definition.Task_Definition.revision
					task["date"] = task_definition.Task_Definition.date
					task["cpu"] = task_definition.Task_Definition.cpu
					task["memory"] = task_definition.Task_Definition.memory
					task_definition_list.append(task)
				result["task_definitions"] = task_definition_list
				results.append(result)

			if (toDate) is not None:
				print("toDate")
				task_definition_result = db.session.query(Cluster, Component, Task_Definition).filter(Component.cluster_id == Cluster.cluster_id, Component.component_id == Task_Definition.component_id).filter(Cluster.cluster_name==res.Cluster.cluster_name).filter(Task_Definition.date <= toDate).all()
				task_definition_list = []
				for task_definition in task_definition_result:
					task = {}
					task["task_definition_name"] = task_definition.Task_Definition.task_definition_name
					task["image_tag"] = task_definition.Task_Definition.image_tag
					task["revision"] = task_definition.Task_Definition.revision
					task["date"] = task_definition.Task_Definition.date
					task["cpu"] = task_definition.Task_Definition.cpu
					task["memory"] = task_definition.Task_Definition.memory
					task_definition_list.append(task)
				result["task_definitions"] = task_definition_list
				results.append(result)

			if (fromDate) is not None:
				print("fromDate")
				task_definition_result = db.session.query(Cluster, Component, Task_Definition).filter(Component.cluster_id == Cluster.cluster_id, Component.component_id == Task_Definition.component_id).filter(Cluster.cluster_name==res.Cluster.cluster_name).filter(Task_Definition.date >= fromDate).all()
				task_definition_list = []
				for task_definition in task_definition_result:
					task = {}
					task["task_definition_name"] = task_definition.Task_Definition.task_definition_name
					task["image_tag"] = task_definition.Task_Definition.image_tag
					task["revision"] = task_definition.Task_Definition.revision
					task["date"] = task_definition.Task_Definition.date
					task["cpu"] = task_definition.Task_Definition.cpu
					task["memory"] = task_definition.Task_Definition.memory
					task_definition_list.append(task)
				result["task_definitions"] = task_definition_list
				results.append(result)
			#results.append(result)
		print(results)
		return 	results

search_result = Search()
print("Searching for client_name")
search_result.getSearchResult(product_name="iConductor")
print("done!")