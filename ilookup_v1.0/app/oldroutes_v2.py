from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
from sqlalchemy import create_engine, Table, select, MetaData
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import boto3
from awsdata import AWSData

@app.route('/', methods=['GET', 'POST'])
#This function gathers all the data from the SQL tables to generate the search filters
def search():
	# print("Result page")
	#getResultByProduct("iForms")
	###############################################################
	awsData = AWSData()
	clients = Client.query.all()
	products = Product.query.all()
	releases = Product_Release.query.all()
	clusters = Cluster.query.all()
	environments = []
	regions = []
	#Remove duplicate values such as "dev" and "qa"
	# for cluster in clusters:
	#  	if cluster.environment not in environments:
	# 	 	environments.append(cluster.environment)
	# 	if cluster.region not in regions:
	# 		regions.append(cluster.region)

	# components = Component.query.all()
	# #Renders the Result.html file which extends Search.html which extends Layout.html
	return render_template('search.html', clientsQ=clients,
	 productsQ=products, releasesQ=releases, clustersQ=clusters,
		componentsQ=components, environmentsQ=environments, regionsQ=regions)

#This function communicates with the HTML and gathers the responses in order to load the table data.
@app.route('/result', methods=['GET','POST'])
def result():
	results = []
	data = request.form.keys()
	for values in data:
		stringified = values
		objectified = json.loads(values)
		#print(objectified['Clients'], objectified['Products'])
		#print(objectified['Dates'])
		clients = objectified['Clients']
		products = objectified['Products']
		for client in clients:
			client_result = getResultByClient(client)
			results.append(client_result)
		for product in products:
			product_result = getResultByProduct(product)
			results.append(product_result)
	print(results)
	return render_template('result.html', results=results)

@app.route('/load', methods=['GET','POST'])
def loadAWSData():
	print("Loading")
	awsdata = AWSData()
	awsdata.populateClusters()
	db.session.commit()
	print("Loaded")
	return search()

def getCPRC(client_name):
	client = Client.query.filter_by(client_name=client_name).first()
	client_id = client.client_id
	cprc_result = CPRC.query.filter_by(client_id=client_id).all()
	cprc = []
	for cprc_record in cprc_result:
		record = {}
		cluster_id = cprc_record.cluster_id
		prid = cprc_record.product_release_id
		record["cluster_id"] = cluster_id
		record["prid"] = prid
		cprc.append(record)
	return cprc


def getClustersByClient(client_name):
	client = Client.query.filter_by(client_name=client_name).first()
	client_id = client.client_id
	cprc_result = CPRC.query.filter_by(client_id=client_id).all()
	clusters = []
	for record in cprc_result:
		cluster_id = record.cluster_id
		clusters.append(Cluster.query.get(cluster_id))
	return clusters

def getTaskDefinitions(cluster_id):
	components = Component.query.filter_by(cluster_id=cluster_id).all()
	print("Components")
	print(components)
	mylist = []
	task_definitions = []
	for component in components:
		component_id = component.component_id
		task_definitions = Task_Definition.query.filter_by(component_id=component_id).all()
		mylist.append(task_definitions)
		#print(task_definitions)
	#print("Getting TaskDefinition")
	#print(task_definitions)
	#print("Got TaskDefinition")
	print("List of Task Definitions")
	print(mylist)
	return task_definitions

def getProductByPRID(prid):
	product_dict = {}
	product_release = Product_Release.query.get(prid)
	product_id = product_release.product_id
	release = product_release.release_number

	product = Product.query.get(product_id)
	product_name = product.product_name

	product_dict["product_name"] = product_name
	product_dict["release"] = release
	return product_dict

@app.route('/mydb', methods=['GET', 'POST'])
def getResultByClient(client_name):
	result = []
	cprc = getCPRC(client_name)
	for record in cprc:
		cluster_id = record["cluster_id"]
		prid = record["prid"]
		cluster = getClusterInfo(cluster_id)
		cluster_name = cluster["cluster_name"]
		region = cluster["region"]
		environment = cluster["environment"]
		product = getProductByPRID(prid)
		product_name = product["product_name"]
		release = product["release"]
		task_definitions = getTaskDefinitions(cluster_id)
		for task_definition in task_definitions:
			# task_definition_name = task_definition.task_definition_name
			# image_tag = task_definition.image_tag
			# revision = task_definition.revision
			# date = task_definition.date
			# cpu = task_definition.cpu
			# memory = task_definition.memory
			#print(client_name,product_name, release,cluster_name,task_definition_name,image_tag,revision,date, environment, region, cpu,memory)
			result_record = {}
			result_record['client_name'] = client_name
			result_record['product_name'] = product_name
			result_record['release'] = release
			result_record['cluster_name'] = cluster_name
			result_record['region'] = region
			result_record['environment'] = environment
			result_record["task_definition_name"] = task_definition.task_definition_name
			result_record['image_tag'] = task_definition.image_tag
			result_record['revision'] = task_definition.revision
			result_record['date'] = task_definition.date
			result_record['cpu'] = task_definition.cpu
			result_record['memory'] = task_definition.memory
			result.append(result_record)
	return result

def getClusterInfo(cluster_id):
	cluster_info = {}
	cluster = Cluster.query.get(cluster_id)
	cluster_name = cluster.cluster_name
	region = cluster.region
	environment = cluster.environment
	cluster_info['cluster_name'] = cluster_name
	cluster_info["region"] = region
	cluster_info["environment"] = environment
	return cluster_info

################################################################

def getPIDByProduct(product_name):
	product = Product.query.filter_by(product_name=product_name).first()
	product_id = product.product_id
	return product_id

def getPRIDByProduct(product_id):
	product_release = Product_Release.query.filter_by(product_id=product_id).all()
	# prid_list = []
	# for record in product_release:
	# 	prid_list.append(record)
	#return prid_list
	return product_release

def getClientClusterByPRID(prid_list):
	client_cluster_list = []
	for prid_record in prid_list:
		cprc_record_list = []
		prid = prid_record["prid"]
		cprc_record_list = CPRC.query.filter_by(product_release_id=prid).all()
		for cprc_record in cprc_record_list:
			client_id = cprc_record.client_id
			cluster_id = cprc_record.cluster_id
			client_cluster_dict = {}
			client_cluster_dict["client_id"] = client_id
			client_cluster_dict["cluster_id"] = cluster_id
			client_cluster_list.append(client_cluster_dict)
	return client_cluster_list

def getClientInfo(client_id):
	client = Client.query.get(client_id)
	client_name = client.client_name
	return client_name

def getResultByProduct(product_name):
	result = []
	product_id = getPIDByProduct(product_name)
	product_releases = getPRIDByProduct(product_id)
	prid_list =[]
	for product_release in product_releases:
		product_release_record = {}
		product_release_record["prid"] = product_release.product_release_id
		product_release_record["release"] = product_release.release_number
		prid_list.append(product_release_record)
	client_cluster_list = getClientClusterByPRID(prid_list)
	for record in client_cluster_list:
		product_result_object = {}
		client_id = record["client_id"]
		cluster_id = record["cluster_id"]
		client_name = getClientInfo(client_id)
		cluster_info = getClusterInfo(cluster_id)
		task_definitions = getTaskDefinitions(cluster_id)
		for task_definition in task_definitions:
			product_result_object["client_name"]=client_name
			product_result_object["cluster_name"] = cluster_info["cluster_name"]
			product_result_object["environment"] = cluster_info["environment"]
			product_result_object["region"] = cluster_info["region"]
			product_result_object["product_name"] = product_name
			product_result_object["release"] = product_release.release_number
			product_result_object["task_definition_name"] = task_definition.task_definition_name
			product_result_object["image_tag"]= task_definition.image_tag
			product_result_object["revision"] = task_definition.revision
			product_result_object["cpu"] = task_definition.cpu
			product_result_object["memory"] = task_definition.memory
			product_result_object["date"] = task_definition.date
			result.append(product_result_object)
	#print(result)
	return result
