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

@app.route('/', methods=['GET', 'POST'])
#This function gathers all the data from the SQL tables to generate the search filters
def search():
	clients = Client.query.all()
	products = Product.query.all()
	releases = Product_Release.query.all()
	clusters = Cluster.query.all()
	components = Component.query.all()
	productsQ = Product.query.all()
	clustersQ = Cluster.query.all()
	environments = []
	regions = []
	for cluster in clusters:
	 	if cluster.environment not in environments:
	 		environments.append(cluster.environment)
		if cluster.region not in regions:
			regions.append(cluster.region)

	#Renders the Result.html file which extends Search.html which extends Layout.html
	return render_template('search.html', clientsQ=clients,
	productsQ=products, releasesQ=releases, clustersQ=clusters,
	componentsQ=components, environmentsQ=environments, regionsQ=regions, productsTag=productsQ, clustersTag=clustersQ)

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
	environment = []
	regions = []
	clusters = []
	components = []
	for res in result:
		clients.append(res.Client)
		products.append(res.Product)
		clusters.append(res.Cluster)
		releases.append(res.Product_Release)

	clients = list(set(clients))
	products = list(set(products))
	clusters = list(set(clusters))
	releases = list(set(releases))
	environments = []
	regions = []
	for cluster in clusters:
	 	if cluster.environment not in environments:
	 		environments.append(cluster.environment)
		if cluster.region not in regions:
			regions.append(cluster.region)

	return str(clients + products + clusters + environments + regions + releases)


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
	return 'Succeeded in updating the cluster(s)'



#This function communicates with the HTML and gathers the responses in order to load the table data.
@app.route('/result', methods=['GET','POST'])
def result():
	results = []
	data = request.form.keys()
	for values in data:
		objectified = json.loads(values)
		clients = objectified['Clients']
		products = objectified['Products']
		for client in clients:
			client_result = search(client_name=client)
			results = results + (client_result)
		for product in products:
			product_result = search(product_name=product)
			results = results + (product_result)
	return render_template('result.html', results=results)

def search(client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None):
	search = Search()
	print("calling search function.....")
	search_result = search.getSearchResult(client_name=client_name, product_name=product_name, release=release, cluster_name=cluster_name, region=region, environment=environment, toDate=toDate, fromDate=fromDate)
	#pprint.pprint(search_result)
	return search_result

# main function that triggers other helper functions to
def updateRelease(product_name=None, release_number=None, cluster_name=None):
	update_release = Update_Release()
	product_release_id = update_release.populateProductRelease(product_name,release_number)
	update_release.populateCPRC(cluster_name, product_release_id)
	update_release.populateTaskDefinition(cluster_name)
