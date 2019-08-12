from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component, Task_Definition, CPRC
from sqlalchemy import create_engine, Table, select, MetaData
from flask_sqlalchemy import SQLAlchemy
from awsdata import AWSData
#from checkData import CheckAWSData
from db_search_v3 import Search
from db_update_release import Update_Release
from db_dynamic_filter import DynamicFilter
from addUpdateDB import AddUpdateRecords
from db_delete_v3 import DeactivateRecords
import requests
import json
import boto3
import pprint
#this regions is to get all the regions
from regions import regionObject

#This is to initial AWS client to the N. Virginia region  -- You need to have it so theres another client for the other regions
client = boto3.client('ecs')

#This function is to convert the unicode arrays that you get from SQL and change them into a normal array -- THE DECODE IS NECESSARY OTHERWISE BYTECODE ISSUES
def convertUnicodeToArray(unicodeArray):
	newArray = []
	counter = 0
	for x in range(len(unicodeArray)):
		utf8string = unicodeArray[x].encode("utf-8").decode('utf-8')
		newArray.append(utf8string)
	return newArray

@app.route('/', methods=['GET', 'POST'])
#This function gathers all the data from the SQL tables to generate the search filters
def load():
	return render_template('search.html')

@app.route('/search', methods=['GET'])
#This search function populats all the search bars with every potential search query from our SQL database
def search():

	clients = db.session.query(Client).order_by(Client.is_active.desc(), Client.client_name).all()
	products = db.session.query(Product).order_by(Product.is_active.desc(), Product.product_name).filter(Product.is_active==True).all()
	releases = db.session.query(Product_Release).order_by(Product_Release.inserted_at).all()
	#releases = Product_Release.query.all()
	clusters = db.session.query(Cluster).order_by(Cluster.cluster_name).all()
	components = Component.query.all()

	#creates empty arrays to return back to the front end
	clientsQ = []
	productsQ = []
	releasesQ = []
	clustersQ = []
	componentsQ = []
	environmentsQ = []
	regionsQ = []
	productsTagQ = []
	clustersTagQ = []

	#this takes the individual search results and puts them into the arrays
	for client in clients:
		clientsQ.append(client.client_name)
	for product in products:
		productsQ.append(product.product_name)
		productsTagQ.append(product.product_name)
	for release in releases:
		releasesQ.append(release.release_number)
	for cluster in clusters:
		clustersQ.append(cluster.cluster_name)
		clustersTagQ.append(cluster.cluster_name)
		if cluster.environment not in environmentsQ:
	 		environmentsQ.append(cluster.environment)
		if cluster.region not in regionsQ:
			regionsQ.append(cluster.region)

	#This converts the unicode array generated from those forloops and changes them into an Array
	clientsQ = convertUnicodeToArray(clientsQ)
	productsQ = convertUnicodeToArray(productsQ)
	releasesQ = convertUnicodeToArray(releasesQ)
	clustersQ = convertUnicodeToArray(clustersQ)
	clustersTagQ = convertUnicodeToArray(clustersTagQ)
	environmentsQ = convertUnicodeToArray(environmentsQ)
	regionsQ = convertUnicodeToArray(regionsQ)
	productsTagQ = convertUnicodeToArray(productsTagQ)

	clientsQ = sorted(clientsQ)
	clustersQ = sorted(clustersQ)
	productsQ = sorted(productsQ)
	releasesQ = sorted(releasesQ)
	regionsQ = sorted(regionsQ)
	environmentsQ = sorted(environmentsQ)

	return jsonify(clientsQ=clientsQ, productsQ=productsQ, releasesQ=releasesQ, clustersQ=clustersQ, environmentsQ=environmentsQ, regionsQ=regionsQ, productsTagQ=productsTagQ, clustersTagQ=clustersTagQ)


@app.route('/update', methods=['GET', 'POST'])
def update():
	#This update function takes the selected queries from the frontend and then generates the new search bar queries based on that filter
	#request.form.keys() gets the data that send request.form
	data = request.form.keys()
	for values in data:
		stringified = values
		objectified = json.loads(values)
		print(objectified)
		client=""
		product=""
		release=""
		region=""
		cluster=""
		environment=""


		if len(objectified["Clients"]) > 0:
			client = objectified["Clients"][0]
		if len(objectified["Products"]) > 0:
			product = objectified["Products"][0]
		if len(objectified["Releases"]) > 0:
			release = objectified["Releases"][0]
		if len(objectified["Regions"]) >  0:
			region = objectified["Regions"][0]
		if len(objectified["Clusters"]) > 0:
			cluster = objectified["Clusters"][0]
		if len(objectified["Environments"]) > 0:
			environment = objectified["Environments"][0]
		# if "Active" in objectified.keys():
		# 	is_active = objectified["Active"]
		# else:
		# 	is_active = None
		# print(is_active)
		is_active = None
		if "Active" in objectified:
			print("*******************************************************@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@******************")
			print(objectified["Active"])
			print("*******************************************************@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@******************")

			is_active = objectified['Active']
			if is_active ==True:
				is_active = True
			if is_active == False:
				is_active = False
			if is_active == "None":
				is_active = None
		# print("............................")
		# print(is_active)


	#This calls the function of DynamicFilter where it gets the actual results
	dynamicFilter = DynamicFilter()
	result = dynamicFilter.getFirstFilterResult(client_name=client,product_name=product,release=release,region=region,cluster_name=cluster,environment=environment, is_active=is_active)
	pprint.pprint(result)
	clients = []
	products = []
	releases = []
	environments = []
	regions = []
	clusters = []

	#This for loop takes the results from the DynamicFilter() and pushes them into the necessary arrays
	for res in result:
		clients.append(res.Client.client_name)
		products.append(res.Product.product_name)
		clusters.append(res.Cluster.cluster_name)
		releases.append(res.Product_Release.release_number)
		environments.append(res.Cluster.environment)
		regions.append(res.Cluster.region)


	# clients = sorted(clients)
	# products = sorted(products)
	# clusters = sorted(clusters)
	# releases = sorted(releases)
	# environments = sorted(environments)
	# regions = sorted(regions)

	#This once again takes care of changing Unicode into normal Arrays

	clients = convertUnicodeToArray(list(set(clients)))
	products = convertUnicodeToArray(list(set(products)))
	clusters = convertUnicodeToArray(list(set(clusters)))
	releases = convertUnicodeToArray(list(set(releases)))
	environments = convertUnicodeToArray(list(set(environments)))
	regions = convertUnicodeToArray(list(set(regions)))

	clients = sorted(clients)
	products = sorted(products)
	clusters = sorted(clusters)
	releases = sorted(releases)
	environments = sorted(environments)
	regions = sorted(regions)

	return jsonify(clientsUp=clients, productsUp=products, clustersUp=clusters, environmentsUp=environments, regionsUp=regions, releasesUp=releases)


#This route is to have a POST request in order to create a new release tag or update.
@app.route('/newTag', methods=['GET', 'POST'])
def createTag():
	data = request.form.keys()
	for values in data:
		objectified = json.loads(values)
	#This is put in all the functions to take care of both the London and N.Virginia region
	region = regionObject[objectified['tagQuery']['region']]
	uniClient = boto3.client("ecs", region_name=region)
	clusters = uniClient.list_clusters()
	clusterArns = clusters["clusterArns"]
	client_names = []
	old_product_name = "UNKNOWN"

	#This forloop goes through the clusters selected, then the one below goes through each Cluster in the AWS data, and then we parse through that and then find the selected cluster on AWS updating that cluster's tag
	for cluster in objectified["tagQuery"]["clusters"]:
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split("/")
			if (cluster == cluster_split[1]):
				currentTags = uniClient.list_tags_for_resource(resourceArn=awsCluster) # old key value pairs
				tags = currentTags["tags"]
				for tag in tags:
					if tag["key"] == "Application":
						old_product_name = tag["value"]
					#This checks to see if it's a Release Tag, cause it will be called afterwards in order to update SQL side
					if tag['key'] == "Release":
						old_release_number = tag['value']
					if "Custome" in tag['key']:
						client_names.append(tag['value'])
						if objectified['tagQuery']['tagValue'] == tag['value']:
							return "Client already exists"
					if tag['key'] == objectified['tagQuery']['tagKey']:
						uniClient.untag_resource(resourceArn=awsCluster, tagKeys=[objectified['tagQuery']['tagKey']])

				#This makes sure that there are no empty spaces, getting rid of empty spaces at the end
				noSpaces = objectified['tagQuery']['tagKey']
				for x in objectified['tagQuery']['tagKey']:
					if objectified['tagQuery']['tagKey'] == " ":
						noSpaces = objectified['tagQuery']['tagKey'][:-1]
				value = objectified['tagQuery']['tagValue']
				if "Environmen" in noSpaces:
					value = value.upper()
				uniClient.tag_resource(resourceArn=awsCluster, tags=[{'key':noSpaces, 'value': value}])

				#This checks to see if its a Product and goes to update the Product tags and active/inactive on the SQL sides
				if "Applicatio" in objectified['tagQuery']['tagKey']:
					new_product_name = objectified['tagQuery']['tagValue']
					cluster_name = cluster_split[1]
					addUpdateRecord = AddUpdateRecords()
					addUpdateRecord.addUpdateProduct(old_product_name,new_product_name,client_names,cluster_name,old_release_number)
				#This checks to see if its a Client and goes to update the Client tags and active/inactive on the SQL sides
				if "Custome" in objectified['tagQuery']['tagKey']:
					new_client_key = objectified['tagQuery']['tagKey']
					new_client_name = objectified['tagQuery']['tagValue']
					cluster_name = cluster_split[1]
					fetchClientKeyValue(new_client_key,new_client_name,cluster_name,currentTags)
				#This checks to see if its an Environment and updates the SQL side with the new environment
				if "Environmen" in objectified['tagQuery']['tagKey']:
					cluster_name = cluster_split[1]
					addUpdateRecord = AddUpdateRecords()
					addUpdateRecord.updateEnvironment(cluster_name,objectified['tagQuery']['tagValue'].upper())

				#This checks to update Release functionality and change multiple tables
				if objectified['tagQuery']['tagKey'] == 'Release':
					cluster_name = cluster_split[1]
					product_name = old_product_name
					new_release_number = objectified['tagQuery']['tagValue']

					addUpdateRecord = AddUpdateRecords()
					#updateRelease(objectified['tagQuery']["product"], objectified['tagQuery']['tagValue'], cluster)
					print("MMMMMMMMMMMMMMMMMMMMMMMMMMMWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
					print(old_release_number)
					print("MMMMMMMMMMMMMMMMMMMMMMMMMMMWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
					addUpdateRecord.updateProductRelease(product_name, cluster_name, old_release_number, new_release_number)
					addUpdateRecord.updateTaskDefinition(cluster_name, old_release_number, new_release_number)
	return 'Successfully updated the cluster(s)'

@app.route('/deleteTag', methods=['GET', 'POST'])
def deleteTag():
	data = request.form.keys()
	region = ""
	for values in data:
		objectified = json.loads(values)
	region = regionObject[objectified['tagQuery']['region']]
	uniClient = boto3.client("ecs", region_name=region)
	clusters = uniClient.list_clusters()
	clusterArns = clusters["clusterArns"]
	for cluster in objectified['tagQuery']['clusters']:
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split('/')
			if (cluster == cluster_split[1]):
				currentTags = uniClient.list_tags_for_resource(resourceArn=awsCluster)
				tags = currentTags["tags"]
				clientCounter = -1
				clientNumber = 1
				for tag in tags:
					print(tag)
					if "Release" in tag['key']:
						release_number = tag['value']
						print(release_number)
					if "Application" in tag['key']:
						product_name = tag['value']
					if "Custome" in tag['key']:
						clientCounter = clientCounter + 1
					if tag['key'] == objectified['tagQuery']['tagKey']:
						# ADDED NEW CODE
						print(objectified['tagQuery']['tagKey'])
						if "Custome" in tag['key']:
							print(objectified['tagQuery'])
							client_name = tag['value']
							# print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
							# print("Trying to delete a client", )
							# print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
						# 	deactivateRecords = DeactivateRecords()
						# 	deactivateRecords.deactivateClient(client_name, cluster, product_name, release_number)
						# # END OF NEW CODE
						# uniClient.untag_resource(resourceArn=awsCluster, tagKeys=[objectified['tagQuery']['tagKey']])

				if "Customer" in objectified['tagQuery']['tagKey']:
					deactivateRecords = DeactivateRecords()
					deactivateRecords.deactivateClient(client_name, cluster, product_name, release_number)
					uniClient.untag_resource(resourceArn=awsCluster, tagKeys=[objectified['tagQuery']['tagKey']])


				updatedTags = uniClient.list_tags_for_resource(resourceArn=awsCluster)
				tagzs = updatedTags["tags"]
				print(tagzs)
				for tagz in tagzs:
					if "Custome" in tagz['key']:
						if clientNumber <= clientCounter:
							value = tagz['value']
							if str(clientNumber) == "1":
								key="Customer"
							else:
								key = "Customer" + str(clientNumber)
							clientNumber = clientNumber + 1
							uniClient.untag_resource(resourceArn=awsCluster, tagKeys=[tagz['key']])
							uniClient.tag_resource(resourceArn=awsCluster, tags=[{"key": key, 'value': value}])
	return "Successfully deleted the tag"

#Retrieves the tags for given AWS clusters
@app.route('/getTags', methods=['GET', 'POST'])
def getTags():
	data = request.form.keys()
	clusterList = []
	totalTagList = []
	clusterTagObj = {}
	region = ""
	for values in data:
		objectified = json.loads(values)
		clusterList = objectified['clusterList']

	# clusterList = convertUnicodeToArray(clusterList)
	if 'region' in objectified.keys():
		region = regionObject[objectified['region']]
	else:
		return ""
	uniClient = boto3.client("ecs", region_name=region)
	for cluster in clusterList:
		clusters = uniClient.list_clusters()
		clusterArns = clusters["clusterArns"]
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split("/")
			if (cluster == cluster_split[1]):
				currentTags = uniClient.list_tags_for_resource(resourceArn=awsCluster)
				if(currentTags["tags"] != []):
					for tag in currentTags["tags"]:
						totalTagList.append(tag["key"])
	totalTagList = convertUnicodeToArray(list(set(totalTagList)))
	for tag in totalTagList:
		clusterTagObj[tag] = {}
	counter = -1
	for cluster in clusterList:
		counter = counter + 1
		clusters = uniClient.list_clusters()
		clusterArns = clusters["clusterArns"]
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split("/")
			if(cluster == cluster_split[1]):
				currentTags = uniClient.list_tags_for_resource(resourceArn=awsCluster)
				if (currentTags["tags"] != []):
					for awsTag in currentTags["tags"]:
						key = awsTag["key"]
						value = awsTag["value"]
						clusterTagObj[str(key)][counter] = str(value)
	return jsonify(clusterTagObj)

#This function communicates with the HTML and gathers the responses in order to load the table data.
@app.route('/result', methods=['GET','POST'])
def result():

	if request.method == 'GET':
		recentReleases = mostRecentReleases()
		return render_template('result.html', results=recentReleases)

	results = []
	data = request.form.keys()
	product = None
	client= None
	region = None
	release = None
	environment = None
	cluster = None
	toDate = None
	fromDate = None
	for values in data:
		objectified = json.loads(values)
		clients = objectified['Clients']
		products = objectified['Products']
		releases = objectified['Releases']
		regions = objectified['Regions']
		clusters = objectified['Clusters']
		environments = objectified['Environments']
		components = objectified['Components']
		dates = objectified['Dates']
		active = objectified['Active']
		if active == "None":
			active = None
		toDate = None
		if len(clients) > 0:
			client = clients[0]
		if len(products) > 0:
			product = products[0]
		if len(releases) > 0:
			release = releases[0]
		if len(regions) > 0:
			region = regions[0]
		if len(clusters) > 0:
			cluster = clusters[0]
		if len(environments) > 0:
			environment = environments[0]
		if len(components) > 0:
			component = components[0]
		if len(dates) > 0:
			toDate = dates[1]
			fromDate = dates[0]
			if toDate == "":
				toDate = None
			if fromDate == "":
				fromDate = None
		result  = search(is_active=active, client_name=client, product_name=product,release=release, cluster_name=cluster,region=region,environment=environment, toDate=toDate, fromDate=fromDate)
		results = results + (result)
		# Within results, create an object that {cluster_name: [releases] or {Release: 1.1.1.1, Info: Etc}} and pass it into the front end, where we map it by connecting release numbers - Having it as hidden dropdowns
	return render_template('result.html', results=results)

@app.route('/getTasks', methods=["GET", "POST"])
def sendTasks():
	data = request.form.keys()

	for values in data:
		objectified = json.loads(values)
	print(objectified["releaseNum"])
	tasks = getTaskDefinitions(objectified["clusterName"], objectified["releaseNum"])
	return jsonify(tasks)

@app.route('/getClients', methods=["GET", "POST"])
def sendClients():
	data = request.form.keys()
	for values in data:
		objectified = json.loads(values)
	clients = getClients(objectified["clusterName"], objectified["release"])
	return jsonify(clients)

@app.route('/getReleaseHistory', methods=["GET", "POST"])
def sendReleases():
	data = request.form.keys()
	for values in data:
		objectified = json.loads(values)
	releases = getReleases(objectified["clusterName"])
	releasesStrArray = []
	for x in releases:
		strX = str(x)
		firstOccurance = strX.find("'")
		releasesStrArray.append(strX[firstOccurance+1: len(strX)-3])
	return jsonify(releasesStrArray)


@app.route('/updateReleaseTable', methods=["GET", "POST"])
def updateReleaseTable():
	print("?????///////////////////////???????/////////////////????????/?/////////")
	data = request.form.keys()
	for values in data:
		objectified = json.loads(values)

		region = regionObject[objectified['region']]

	uniClient = boto3.client("ecs", region_name=region)
	print(data)
	clusters = uniClient.list_clusters()
	clusterArns = clusters["clusterArns"]

	# this is where you will add the code to update the Task Definition and PRID table with the newRelease using objectified["newRelease"]
	product_name = objectified["product"]
	cluster_name = objectified["clusterName"]
	old_release_number = objectified["oldRelease"]
	new_release_number = objectified["newRelease"]
	addUpdateRecord = AddUpdateRecords	#product_release_exists = db.session.query(Product_Release.release_number).filter(Product_Release.product)
	print("Hello/")
	product_release_exists = db.session.query(Product_Release.release_number).filter(Product_Release.product_id==Product.product_id, Product_Release.product_release_id==CPRC.product_release_id, CPRC.cluster_id==Cluster.cluster_id).filter(Product_Release.release_number==new_release_number).filter(Product.product_name==product_name).filter(Cluster.cluster_name==cluster_name).first()
	print(".................................",product_release_exists)

	if product_release_exists != None:
		print("Do we keep coming in here?", product_release_exists)
		return jsonify(value=True)

	else:
		#addUpdateRecord.updateTaskDefinition(cluster_name, old_release_number, new_release_number)
		addUpdateRecord.updateProductRelease(product_name,cluster_name, old_release_number, new_release_number)
		addUpdateRecord.updateTaskDefinition(cluster_name, old_release_number, new_release_number)
		
		print("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split("/")
			if (objectified["clusterName"] == cluster_split[1]):
				currentTags = uniClient.list_tags_for_resource(resourceArn=awsCluster)
				tags = currentTags["tags"]
				for tag in tags:
					if tag["key"] == "Release":
						if tag["value"] == objectified["oldRelease"]:
							uniClient.untag_resource(resourceArn=awsCluster, tagKeys=['Release'])
						uniClient.tag_resource(resourceArn=awsCluster, tags=[{'key': 'Release', 'value': objectified["newRelease"]}])
	return jsonify(value=False)


def search(client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None, is_active=None):
	search = Search()
	search_result = search.getSearchResult(client_name=client_name, product_name=product_name, release=release, cluster_name=cluster_name, region=region, environment=environment, toDate=toDate, fromDate=fromDate, is_active=is_active)
	return search_result

# main function that triggers other helper functions to
def updateRelease(product_name=None, release_number=None, cluster_name=None):
	update_release = Update_Release()
	product_release_id = update_release.populateProductRelease(product_name,release_number)
	update_release.populateCPRC(cluster_name, product_release_id)
	update_release.populateTaskDefinition(cluster_name)

def mostRecentReleases():
	search = Search()
	search_result = search.getLatestReleases()
	return search_result

def getTaskDefinitions(cluster_name, release_number):
	search = Search()
	task_definitions = search.getTaskDefinitions(cluster_name,release_number)
	return task_definitions

def fetchClientKeyValue(new_client_key, new_client_name, cluster_name, currentTags):
	print(currentTags)
	old_client_name = ""
	currentTags = currentTags['tags']
	for tag in currentTags:
		if tag['key'] == new_client_key:
			old_client_name = tag['value']
		if tag['key'] == "Application":
			product_name = tag['value']
		if tag['key'] == "Release":
			release_number = tag['value']
		if tag['key'] == "Environment":
			environment = tag['value']
	addUpdateRecord = AddUpdateRecords()
	addUpdateRecord.addUpdateClient(old_client_name,new_client_name,product_name,cluster_name,release_number)

def getReleases(cluster_name):
	search = Search()
	releases = search.getReleases(cluster_name)
	return releases

def getClients(cluster_name, release_number):
	search = Search()
	clients = search.getClients(cluster_name, release_number)
	return clients

@app.route('/load', methods=['GET','POST'])
def loadAWSData():
	print("Loading")
	# checkData = CheckAWSData()
	# checkData.checkData()
	# db.session.commit()
	# print("Loaded")
	awsdata = AWSData()
	awsdata.newMainFunction()
	#db.session.commit()
	return redirect(url_for("load"))
