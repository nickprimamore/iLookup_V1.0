from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
from sqlalchemy import create_engine, Table, select, MetaData
from flask_sqlalchemy import SQLAlchemy
from awsdata import AWSData
from db_search import Search
from db_update_release import Update_Release
from db_dynamic_filter import DynamicFilter
import requests
import json
import boto3
import pprint

client = boto3.client('ecs')

def convertUnicodeToArray(unicodeArray):
	newArray = []
	counter = 0
	for x in range(len(unicodeArray)):
		utf8string = unicodeArray[x].encode("utf-8")
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
	clusters = client.list_clusters()
	clusterArns = clusters["clusterArns"]
	for values in data:
		objectified = json.loads(values)
	for cluster in objectified['tagQuery']['clusters']:
		for awsCluster in clusterArns:
			cluster_split = awsCluster.split("/")
			if (cluster == cluster_split[1]):
				currentTags = client.list_tags_for_resource(resourceArn=awsCluster)
				tags = currentTags["tags"]
				for tag in tags:
					if tag['key'] == 'Release':
						client.untag_resource(resourceArn=awsCluster, tagKeys=['Release'])
				client.tag_resource(resourceArn=awsCluster, tags=[{'key':'Release', 'value': objectified['tagQuery']['releaseNum']}])
				updateRelease(objectified['tagQuery']["product"], objectified['tagQuery']['releaseNum'], cluster)
	return 'Successfully updated the cluster(s)'

#Retrieves the tags for a given AWS cluster
@app.route('/getTags', methods=['GET', 'POST'])
def getTags():
	data = request.form.keys()
	clusterName = ''
	for values in data:
		objectified = json.loads(values)
		clusterName = objectified['clusterName']
	clusters = client.list_clusters()
	clusterArns = clusters["clusterArns"]
	for cluster in clusterArns:
		cluster_split = cluster.split("/")
		if(clusterName == cluster_split[1]):
			currentTags = client.list_tags_for_resource(resourceArn=cluster)
			tags = currentTags["tags"]
			if(tags == []):
				return 'No tags for the selected cluster'
			return jsonify(tags)
	return 'tags'

#This function communicates with the HTML and gathers the responses in order to load the table data.
@app.route('/result', methods=['GET','POST'])
def result():
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
		result  = search(client_name=client, product_name=product,release=release, cluster_name=cluster,region=region,environment=environment, toDate=toDate, fromDate=fromDate)
		results = results + (result)
	return render_template('result.html', results=results)

def search(client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None):
	search = Search()
	search_result = search.getSearchResult(client_name=client_name, product_name=product_name, release=release, cluster_name=cluster_name, region=region, environment=environment, toDate=toDate, fromDate=fromDate)
	return search_result

# main function that triggers other helper functions to
def updateRelease(product_name=None, release_number=None, cluster_name=None):
	update_release = Update_Release()
	product_release_id = update_release.populateProductRelease(product_name,release_number)
	update_release.populateCPRC(cluster_name, product_release_id)
	update_release.populateTaskDefinition(cluster_name)
