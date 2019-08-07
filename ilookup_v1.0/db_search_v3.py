from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
import pprint, json
from sqlalchemy import and_, func, desc, cast, Date

class Search:

	#this function convertes uncicode to array
	def convertUnicodeToArray(self,unicodeArray):
		newArray = []
		for x in unicodeArray:
			strX = str(x)
			firstOccurance = strX.find("'")
			newArray.append(strX[firstOccurance+1: len(strX)-3])
		return newArray

	#This function does dynamic search based on the parameter passed 
	# search_result contains the result of generalised join query which joins all the required tables 
	# each if statement then filters this search_results and returns the final search result in the end
	# the return object "results" is a list of dictionaries of all required data
	def getSearchResult(self,client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None, is_active=None):

		search_result = db.session.query(CPRC.product_release_id, Cluster.cluster_name, Product.product_name, Product_Release.release_number,Cluster.region, Cluster.environment, Product_Release.inserted_at, Cluster.is_active).filter( CPRC.product_release_id == Product_Release.product_release_id,
			Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()

		#this if conditions filter out the search result
		if product_name:
			search_result = search_result.filter(Product.product_name== product_name)

		
		if cluster_name:
			search_result = search_result.filter(Cluster.cluster_name==cluster_name)

		if region:
			search_result = search_result.filter(Cluster.region==region)

		if environment:
			search_result = search_result.filter(Cluster.environment==environment)

		#this filter returns active or inactive clusters
		if is_active!= None:
			search_result = search_result.filter(Cluster.is_active==is_active)

		if (toDate and fromDate) is not None:
			search_result = search_result.filter(and_(func.date(Product_Release.inserted_at)>=fromDate), func.date(Product_Release.inserted_at)<=toDate)

		if (toDate and not fromDate):
			search_result = search_result.filter((func.date(Product_Release.inserted_at)<=toDate))

		if (fromDate and not toDate):
			search_result = search_result.filter((func.date(Product_Release.inserted_at)>=fromDate))

		#this query gives us product_release_id with max(latest) release number for each cluster 
		maxReleases = db.session.query(func.max(CPRC.product_release_id).label("product_release_id"), CPRC.cluster_id)
		maxReleases = maxReleases.group_by(CPRC.cluster_id).all()

		maxResult = []

		#this for loop will help to only get the record(rows) with max(latest) release number per cluster
		for res in maxReleases:
			tempResult = search_result.filter(CPRC.product_release_id==res.product_release_id).filter(CPRC.cluster_id==res.cluster_id).all()
			maxResult = maxResult + (tempResult)

		search_result = maxResult

		#this will remove the duplicate rows 
		search_result = list(set(search_result))
		
	
		results = []

		#this for loop will convert the search_result in the the format required by UI side i.e. list of dictionaries
		for res in search_result:
		
			result = {}
			clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).all()
			clients = self.convertUnicodeToArray(clients)

			#we are passing list of all active and inactive clients for each cluster 
			active_clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).filter(CPRC.is_active==True).filter(Client.client_name!="UNKNOWN").all()
			inactive_clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).filter(CPRC.is_active==False).filter(Client.client_name!="UNKNOWN").distinct().all()

			#this will remove the clients names from inactive_clients list which are also present in actve_clients list
			inactive_clients = set(inactive_clients) - set(active_clients)

			active_clients = self.convertUnicodeToArray(list(set(active_clients)))
			inactive_clients = self.convertUnicodeToArray(list(inactive_clients))
		
			result["client_names"] = clients
			result["active_clients"] = active_clients
			result["inactive_clients"] = inactive_clients
			result["product_name"] = res.product_name
			result["release"] = res.release_number
			result["cluster_name"] = res.cluster_name
			result["region"] = res.region
			result["environment"] = res.environment
			result["is_active"] = res.is_active
			result["inserted_at"] = res.inserted_at

			#this fetches all the release numbers associated with each cluster and corresponding product
			#release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==res.cluster_name).order_by(Product_Release.inserted_at.desc()).all()
			release_numbers = db.session.query(Task_Definition.release_number).filter(Component.component_id==Task_Definition.component_id, Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==res.cluster_name).all()
			release_numbers = list(set(release_numbers))
			result["releases"] = self.convertUnicodeToArray(release_numbers)

			results.append(result)
		
		#filter outs record on the basis of release_number
		if release:
			print("in release condition...................")
			release_results = []
			for res in results:
				releases= res["releases"]
				if release in releases:
					release_results.append(res)
			return release_results

		#filter outs record on the basis of client_name
		if client_name:
			client_results = []
			for res in results:
				client_names = res["client_names"]
				if client_name in client_names:
					client_results.append(res)
			return client_results

		return 	results

		# this function gives  latest release records for each cluster. 
		# this function is same as above function except for search filters and it will return only actve and latest result
	def getLatestReleases(self):
		search_result = db.session.query(CPRC.product_release_id, Cluster.cluster_name, Product.product_name, Product_Release.release_number,Cluster.region, Cluster.environment, Product_Release.inserted_at, Cluster.is_active).filter( CPRC.product_release_id == Product_Release.product_release_id,
			Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()

		maxResult = []
		#this query will get max(latest) product_release_id for each cluster
		maxReleases = db.session.query(func.max(CPRC.product_release_id).label("product_release_id"), CPRC.cluster_id)
		maxReleases = maxReleases.group_by(CPRC.cluster_id).all()

		#with the result of above query we can filter out search_result to get the latest records
		for res in maxReleases:
			tempResult = search_result.filter(CPRC.product_release_id==res.product_release_id).filter(CPRC.cluster_id==res.cluster_id).all()
			maxResult = maxResult + (tempResult)

		results = []
		for res in maxResult:
			result = {}
			clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).filter(Product_Release.release_number==res.release_number).all()
			clients = self.convertUnicodeToArray(clients)

			active_clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).filter(CPRC.is_active==True).filter(Client.client_name!="UNKNOWN").all()
			inactive_clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==res.cluster_name).filter(CPRC.is_active==False).filter(Client.client_name!="UNKNOWN").distinct().all()
			inactive_clients = set(inactive_clients)-set(active_clients)
			active_clients = self.convertUnicodeToArray(list(set(active_clients)))
			inactive_clients = self.convertUnicodeToArray(list(inactive_clients))

			result["client_names"] = clients
			result["active_clients"] = active_clients
			result["inactive_clients"] = inactive_clients
			result["product_name"] = res.product_name
			result["release"] = res.release_number
			result["cluster_name"] = res.cluster_name
			result["region"] = res.region
			result["environment"] = res.environment
			result["is_active"] = res.is_active
			result["inserted_at"] = res.inserted_at

			#release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==res.cluster_name).order_by(Product_Release.inserted_at.desc()).all()
			release_numbers = db.session.query(Task_Definition.release_number).filter(Component.component_id==Task_Definition.component_id, Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==res.cluster_name).all()

			release_numbers = list(set(release_numbers))
			result["releases"] = release_numbers
			results.append(result)

		return results


	#this function return information about task definitions for the cluster passed as a argument
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
		return result

	#this function return all the releases associated to cluster passed as a parameter
	def getReleases(self, cluster_name=None):
		release_numbers = []
		#release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).all()
		release_numbers = db.session.query(Task_Definition.release_number).filter(Component.component_id==Task_Definition.component_id, Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).all()

		release_numbers = list(set(release_numbers))

		return release_numbers

	#this function return all the clients associated to cluster passed as a parameter
	def getClients(self, cluster_name=None, release_number=None):
		clients = db.session.query(Client.client_name).filter(CPRC.client_id==Client.client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(Cluster.cluster_name==cluster_name).filter(Product_Release.release_number==release_number).all()
		clients = self.convertUnicodeToArray(clients)
		return clients

# search_result = Search()
# search_result.getLatestReleases()
# print("done!")

