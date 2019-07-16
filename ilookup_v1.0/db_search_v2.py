from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json
from sqlalchemy import and_, func, desc

class Search:

	def getSearchResult(self,client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None):

		search_result = db.session.query(CPRC, Client, Product_Release, Product, Cluster).filter(CPRC.client_id == Client.client_id, CPRC.product_release_id == Product_Release.product_release_id,
			Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()

		results = []

		if client_name:
			search_result = search_result.filter(Client.client_name== client_name)

		if product_name:
			search_result = search_result.filter(Product.product_name== product_name)

		if release:
			search_result = search_result.filter(Product_Release.release_number==release)

		if cluster_name:
			search_result = search_result.filter(Cluster.cluster_name==cluster_name)
			#pprint.pprint(search_result)

		if region:
			search_result = search_result.filter(Cluster.region==region)

		if environment:
			search_result = search_result.filter(Cluster.environment==environment)

		task_definitions = []
		results = []
		for res in search_result:
			result = {}
			result["client_name"] = res.Client.client_name
			result["product_name"] = res.Product.product_name
			result["release"] = res.Product_Release.release_number
			result["cluster_name"] = res.Cluster.cluster_name
			result["region"] = res.Cluster.region
			result["environment"] = res.Cluster.environment

			#call cprc to fetch records based on same client, cluster
			# get prid and the  corresponding release numbers from PRID Table
			# shove it here
			
			release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==res.Cluster.cluster_name).all()
			release_numbers = list(set(release_numbers))
			result["releases"] = release_numbers
			print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			#print(result)
			#print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			results.append(result)
		pprint.pprint(results)
		return 	results

	def getLatestReleases(self):



		search_result = db.session.query(CPRC, Client, Product_Release, Product, Cluster).filter(CPRC.client_id == Client.client_id, CPRC.product_release_id == Product_Release.product_release_id,
			Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()
		maxResult = []
		maxReleases = db.session.query(func.max(Product_Release.release_number).label("release_number"),Product_Release.product_release_id, Product_Release.product_id)
		maxReleases = maxReleases.group_by(Product_Release.product_id).all()
		for res in maxReleases:
			#print(res.release_number, res.product_release_id)
			tempResult = search_result.filter(Product_Release.product_release_id == res.product_release_id).all()
			#print(tempResult)
			maxResult = maxResult + (tempResult)
		for res in maxResult:
			print(res.Client.client_name, res.Product.product_name, res.Product_Release.release_number, res.Cluster.cluster_name)


	    # print("Before")
	    # print(maxReleases)
	    # print("After")
	    # maxReleases = maxReleases.group_by(Product_Release.product_id, Client.client_id).all()
	    # print(maxReleases)
			   #maxReleases = db.session.query(func.max(Product_Release.release_number).label("release_number"),CPRC, Client, Product_Release, Product, Cluster).filter(CPRC.client_id==Client.client_id,CPRC.product_release_id == Product_Release.product_release_id,Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id)


		task_definitions = []
		results=[]
		for res in maxResult:
			result = {}
			result["client_name"] = res.Client.client_name
			result["product_name"] = res.Product.product_name
			result["release"] = res.Product_Release.release_number
			result["cluster_name"] = res.Cluster.cluster_name
			result["region"] = res.Cluster.region
			result["environment"] = res.Cluster.environment
			task_definition_result = db.session.query(Cluster, Component, Task_Definition).filter(Component.cluster_id == Cluster.cluster_id, Component.component_id == Task_Definition.component_id).filter(Cluster.cluster_name==res.Cluster.cluster_name).filter(Task_Definition.release_number==res.Product_Release.release_number).all()
			task_definition_list = []
			for task_definition in task_definition_result:
				task = {}
				task["task_definition_name"] = task_definition.Task_Definition.task_definition_name
				task["image_tag"] = task_definition.Task_Definition.image_tag
				task["revision"] = task_definition.Task_Definition.revision
				task["date"] = task_definition.Task_Definition.date
				task["cpu"] = task_definition.Task_Definition.cpu
				task["memory"] = task_definition.Task_Definition.memory
				task["release"] = task_definition.Task_Definition.release_number
				task_definition_list.append(task)
				result["task_definitions"] = task_definition_list
			if len(task_definition_list)>0:
				results.append(result)
		print(len(results))
		#pprint.pprint(results)
		return results


### NEW FUNCTION
	def getTaskDefinitions(self,cluster_name=None,release_number=None):
		result = []
		task_definition_list = db.session.query(Cluster, Component, Task_Definition).filter(Component.cluster_id == Cluster.cluster_id, Component.component_id == Task_Definition.component_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.release_number==release_number).all()
		for task_definition in task_definition_list:
			task = {}
			task["task_definition_name"] = task_definition.Task_Definition.task_definition_name
			task["image_tag"] = task_definition.Task_Definition.image_tag
			task["revision"] = task_definition.Task_Definition.revision
			task["date"] = task_definition.Task_Definition.date
			task["cpu"] = task_definition.Task_Definition.cpu
			task["memory"] = task_definition.Task_Definition.memory
			task["release"] = task_definition.Task_Definition.release_number
			result.append(task)
		pprint.pprint(result)
		return result




#search_result = Search()
# search_result.getLatestReleases()

# print("Searching for client_name")
# search_result.getSearchResult(product_name="iConductor",client_name="Willis", environment="dev", cluster_name="test", region="N. Virginia")
# print("done!")

#search_result.getSearchResult()
#search_result.getTaskDefinitions("asg-dev-iforms-cluster", "1.2.1.4")
#print("done!")
