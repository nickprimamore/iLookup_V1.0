from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component, Task_Definition, CPRC
from sqlalchemy import create_engine, Table, select, MetaData
from flask_sqlalchemy import SQLAlchemy
from awsdata import AWSData
from db_search_v3 import Search
from db_update_release import Update_Release
from db_dynamic_filter import DynamicFilter
from addUpdateDB import AddUpdateRecords
import requests
import json
import boto3
import pprint

client = boto3.client('ecs')

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
def search():
	clients = Client.query.all()
	products = Product.query.all()
	releases = Product_Release.query.all()
	clusters = Cluster.query.all()
	components = Component.query.all()

	clientsQ = []
	productsQ = []
	releasesQ = []
	clustersQ = []
	componentsQ = []
	environmentsQ = []
	regionsQ = []
	productsTagQ = []
	clustersTagQ = []

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
	for component in components:
		componentsQ.append(component.component_name)

	clientsQ = convertUnicodeToArray(clientsQ)
	productsQ = convertUnicodeToArray(productsQ)
	releasesQ = convertUnicodeToArray(releasesQ)
	clustersQ = convertUnicodeToArray(clustersQ)
	clustersTagQ = convertUnicodeToArray(clustersTagQ)
	environmentsQ = convertUnicodeToArray(environmentsQ)
	regionsQ = convertUnicodeToArray(regionsQ)
	componentsQ = convertUnicodeToArray(componentsQ)
	productsTagQ = convertUnicodeToArray(productsTagQ)

	return jsonify(clientsQ=clientsQ, productsQ=productsQ, releasesQ=releasesQ, clustersQ=clustersQ, environmentsQ=environmentsQ, regionsQ=regionsQ, componentsQ=componentsQ, productsTagQ=productsTagQ, clustersTagQ=clustersTagQ)

@app.route('/update', methods=['GET', 'POST'])
def update():
	data = request.form.keys()
	for values in data:
		stringified = values
		objectified = json.loads(values)
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

	dynamicFilter = DynamicFilter()
	result = dynamicFilter.getFirstFilterResult(client_name=client,product_name=product,release=release,region=region,cluster_name=cluster,environment=environment)
	clients = []
	products = []
	releases = []
	environments = []
	regions = []
	clusters = []
	components = []

	for res in result:
		clients.append(res.Client.client_name)
		products.append(res.Product.product_name)
		clusters.append(res.Cluster.cluster_name)
		releases.append(res.Product_Release.release_number)
		environments.append(res.Cluster.environment)
		regions.append(res.Cluster.region)

	clients = convertUnicodeToArray(list(set(clients)))
	products = convertUnicodeToArray(list(set(products)))
	clusters = convertUnicodeToArray(list(set(clusters)))
	releases = convertUnicodeToArray(list(set(releases)))
	environments = convertUnicodeToArray(list(set(environments)))
	regions = convertUnicodeToArray(list(set(regions)))

	return jsonify(clientsUp=clients, productsUp=products, clustersUp=clusters, environmentsUp=environments, regionsUp=regions, releasesUp=releases)


#This route is to have a POST request in order to create a new release tag or update.
@app.route('/newTag', methods=['GET', 'POST'])
def createTag():
	data = request.form.keys()
	for values in data:
		objectified = json.loads(values)
	if (objectified['tagQuery']['region'] == "London"):
		region = "eu-west-2"
	else:
		region = "us-east-1"
	uniClient = boto3.client("ecs", region_name=region)
	clusters = uniClient.list_clusters()
	clusterArns = clusters["clusterArns"]
	for cluster in objectified["tagQuery"]["clusters"]:
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split("/")
			if (cluster == cluster_split[1]):
				currentTags = uniClient.list_tags_for_resource(resourceArn=awsCluster) # old key value pairs
				tags = currentTags["tags"]
				for tag in tags:
					if tag['key'] == "Release":
						old_release_number = tag['value']
					# get old tag value here
					print(tag['key'],tag["value"])
					if tag['key'] == objectified['tagQuery']['tagKey']:
						uniClient.untag_resource(resourceArn=awsCluster, tagKeys=[objectified['tagQuery']['tagKey']])

				noSpaces = objectified['tagQuery']['tagKey']
				for x in objectified['tagQuery']['tagKey']:
					if objectified['tagQuery']['tagKey'] == " ":
						noSpaces = objectified['tagQuery']['tagKey'][:-1]
				uniClient.tag_resource(resourceArn=awsCluster, tags=[{'key':noSpaces, 'value': objectified['tagQuery']['tagValue']}])

				if "Client" in objectified['tagQuery']['tagKey']:
					new_client_key = objectified['tagQuery']['tagKey']
					new_client_name = objectified['tagQuery']['tagValue']
					cluster_name = cluster_split[1]
					fetchClientKeyValue(new_client_key,new_client_name,cluster_name,currentTags)
				if "Environment" in objectified['tagQuery']['tagKey']:
					cluster_name = cluster_split[1]
					addUpdateRecord = AddUpdateRecords()
					addUpdateRecord.updateEnvironment(cluster_name,objectified['tagQuery']['tagValue'])

				if objectified['tagQuery']['tagKey'] == 'Release':
					cluster_name = cluster_split[1]
					if objectified['tagQuery']["product"]:
						product_name = objectified['tagQuery']['product']
					else:
						product_name = "unknown"
					new_release_number = objectified['tagQuery']['tagValue']
					# get old release tag
					# get new release tag
					addUpdateRecord = AddUpdateRecords()
					#updateRelease(objectified['tagQuery']["product"], objectified['tagQuery']['tagValue'], cluster)
					addUpdateRecord.updateProductRelease(product_name, old_release_number, new_release_number)
					addUpdateRecord.updateTaskDefinition(cluster_name, old_release_number, new_release_number)
	return 'Successfully updated the cluster(s)'

@app.route('/deleteTag', methods=['GET', 'POST'])
def deleteTag():
	data = request.form.keys()
	region = ""
	for values in data:
		objectified = json.loads(values)
	if (objectified['tagQuery']['region'] == "London"):
		region = "eu-west-2"
	else:
		region = "us-east-1"
	uniClient = boto3.client("ecs", region_name=region)
	clusters = uniClient.list_clusters()
	clusterArns = clusters["clusterArns"]
	for cluster in objectified['tagQuery']['clusters']:
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split('/')
			if (cluster == cluster_split[1]):
				currentTags = uniClient.list_tags_for_resource(resourceArn=awsCluster)
				tags = currentTags["tags"]
				for tag in tags:
					if tag['key'] == objectified['tagQuery']['tagKey']:
						uniClient.untag_resource(resourceArn=awsCluster, tagKeys=[objectified['tagQuery']['tagKey']])
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
	if (objectified['region'] == "London"):
		region = "eu-west-2"
	else:
		region = "us-east-1"
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
	tasks = getTaskDefinitions(objectified["clusterName"], objectified["releaseNum"])
	return jsonify(tasks)

@app.route('/getClients', methods=["GET", "POST"])
def sendClients():
	data = request.form.keys()
	for values in data:
		objectified = json.loads(values)
	clients = getClients(objectified["clusterName"], objectified["release"])
	print(clients)
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
	if (objectified['region'] == "London"):
		region = "eu-west-2"
	else:
		region = "us-east-1"
	uniClient = boto3.client("ecs", region_name=region)
	print(data)
	clusters = uniClient.list_clusters()
	clusterArns = clusters["clusterArns"]

	# this is where you will add the code to update the Task Definition and PRID table with the newRelease using objectified["newRelease"]
	product_name = objectified["product"]
	cluster_name = objectified["clusterName"]
	old_release_number = objectified["oldRelease"]
	new_release_number = objectified["newRelease"]
	addUpdateRecord = AddUpdateRecords()
	addUpdateRecord.updateProductRelease(product_name, old_release_number, new_release_number)
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
	return "Helo"


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
	currentTags = currentTags['tags']
	for tag in currentTags:
		if tag['key'] == new_client_key:
			old_client_name = tag['value']
		if tag['key'] == "Product":
			product_name = tag['value']
		if tag['key'] == "Release":
			release_number = tag['value']
		if tag['key'] == "Environment":
			environment = tag['value']
	addUpdateRecord = AddUpdateRecords()
	addUpdateRecord.addUpdateClient(old_client_name,new_client_name,product_name,cluster_name,release_number)
	#addUpdateRecord.updateEnvironment(cluster_name,environment)
	# call other addUpdate functions here


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
	awsdata = AWSData()
	awsdata.newMainFunction()
	db.session.commit()
	print("Loaded")
	return redirect(url_for("load"))
