from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json
from sqlalchemy import and_, func, desc, cast, Date

class Search:

	def convertUnicodeToArray(self,unicodeArray):
		newArray = []
		for x in unicodeArray:
			strX = str(x)
			firstOccurance = strX.find("'")
			newArray.append(strX[firstOccurance+1: len(strX)-3])
		return newArray

	def getSearchResult(self,client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None, is_active=None):


		print("in search condition")
		print(is_active)
		search_result = db.session.query(Cluster.cluster_name, Product.product_name, Product_Release.release_number,Cluster.region, Cluster.environment, Product_Release.inserted_at, CPRC.is_active).filter( CPRC.product_release_id == Product_Release.product_release_id,
			Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()

		results = []

		# if client_name:
		# 	search_result = search_result.filter(Client.client_name== client_name)

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

		if is_active!= None:
			#print("Is active condition detected")
			search_result = search_result.filter(CPRC.is_active==is_active)

		#to date and from date
		if (toDate and fromDate) is not None:
			search_result = search_result.filter(and_(func.date(Product_Release.inserted_at)>=fromDate), func.date(Product_Release.inserted_at)<=toDate)
	
		if (toDate and not fromDate):
			search_result = search_result.filter((func.date(Product_Release.inserted_at)<=toDate))

		if (fromDate and not toDate):
			search_result = search_result.filter((func.date(Product_Release.inserted_at)>=fromDate))


		search_result = list(set(search_result))
		#pprint.pprint(search_result)

		# task_definitions = []
		# results = []
		for res in search_result:
			#print(res)
			result = {}
			clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).filter(Product_Release.release_number==res.release_number).all()

			clients = self.convertUnicodeToArray(clients)
			# if res.CPRC.cprc_id 

			result["client_names"] = clients
			result["product_name"] = res.product_name
			result["release"] = res.release_number
			result["cluster_name"] = res.cluster_name
			result["region"] = res.region
			result["environment"] = res.environment
			result["is_active"] = res.is_active
			result["inserted_at"] = res.inserted_at
			
		# 	#call cprc to fetch records based on same client, cluster
		# 	# get prid and the  corresponding release numbers from PRID Table
		# 	# shove it here

			release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==res.cluster_name).all()
			release_numbers = list(set(release_numbers))
			result["releases"] = release_numbers
		# # 	#print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		# # 	#print(result)
		# # 	#print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			results.append(result)
		# print(results)
		if client_name:
			# print(client_name)
			client_results = []
			for res in results:
				# print(res["client_names"][0][0])
				client_names = res["client_names"]
				if client_name in client_names:
					client_results.append(res)
					pprint.pprint(res)
			return client_results
		pprint.pprint(results)
		print(len(results))
		return 	results

	def getLatestReleases(self):
		search_result = db.session.query(CPRC.product_release_id, Cluster.cluster_name, Product.product_name, Product_Release.release_number,Cluster.region, Cluster.environment, Product_Release.inserted_at, CPRC.is_active).filter( CPRC.product_release_id == Product_Release.product_release_id,
			Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()

		# search_result = db.session.query(CPRC, Client, Product_Release, Product, Cluster).filter(CPRC.client_id == Client.client_id, CPRC.product_release_id == Product_Release.product_release_id,
		# 	Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).filter(CPRC.is_active==True).distinct()
		maxResult = []
		maxReleases = db.session.query(func.max(CPRC.product_release_id).label("product_release_id"), CPRC.cluster_id)
		print("before..............")
		print(maxReleases)
		maxReleases = maxReleases.group_by(CPRC.cluster_id).all()
		print("after..............")
		print(maxReleases)
		for res in maxReleases:
			#print(res.release_number, res.product_release_id)
			tempResult = search_result.filter(CPRC.product_release_id==res.product_release_id).all()
			#print(tempResult)
			maxResult = maxResult + (tempResult)
		# for res in maxResult:
		# 	print(res.Client.client_name, res.Product.product_name, res.Product_Release.release_number, res.Cluster.cluster_name)

		results = []
		for res in maxResult:
			#print(res)
			result = {}
			clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).filter(Product_Release.release_number==res.release_number).all()

			clients = self.convertUnicodeToArray(clients)
			# if res.CPRC.cprc_id 

			result["client_names"] = clients
			result["product_name"] = res.product_name
			result["release"] = res.release_number
			result["cluster_name"] = res.cluster_name
			result["region"] = res.region
			result["environment"] = res.environment
			result["is_active"] = res.is_active
			result["inserted_at"] = res.inserted_at
			
		# 	#call cprc to fetch records based on same client, cluster
		# 	# get prid and the  corresponding release numbers from PRID Table
		# 	# shove it here

			release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==res.cluster_name).all()
			release_numbers = list(set(release_numbers))
			result["releases"] = release_numbers
		# # 	#print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		# # 	#print(result)
		# # 	#print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			results.append(result)
		pprint.pprint(results)
		print(len(results))
		
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
			task["is_active"] = task_definition.Task_Definition.is_active
			result.append(task)
		#pprint.pprint(result)
		return result

	def getReleases(self, cluster_name=None):
		release_numbers = []
		release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).all()
		release_numbers = list(set(release_numbers))

		return release_numbers


	def getClients(self, cluster_name=None, release_number=None):
		clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==cluster_name).filter(Product_Release.release_number==release_number).all()
		clients = self.convertUnicodeToArray(clients)
		print(clients)
		return clients

# search_result = Search()
# search_result.getLatestReleases()

# print("Searching for client_name")
# search_result.getSearchResult(product_name="iConductor",client_name="Willis", environment="dev", cluster_name="test", region="N. Virginia")
# print("done!")

#search_result.getClients("asg-dev-iforms-cluster", "5.5.5.5")		
#search_result.getTaskDefinitions("asg-dev-iforms-cluster", "1.2.1.4")
#print("done!")
