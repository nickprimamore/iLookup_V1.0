from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
from sqlalchemy import create_engine, Table, select, MetaData
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import boto3

@app.route('/', methods=['GET', 'POST'])
#This function gathers all the data from the SQL tables to generate the search filters
def search():
	# print("Result page")
	###############################################################
	clients = Client.query.all()
	products = Product.query.all()
	releases = Product_Release.query.all()
	clusters = Cluster.query.all()
	environments = []
	regions = []
	#Remove duplicate values such as "dev" and "qa"
	for cluster in clusters:
	 	if cluster.environment not in environments:
		 	environments.append(cluster.environment)
		if cluster.region not in regions:
			regions.append(cluster.region)
	components = Component.query.all()
	#Renders the Result.html file which extends Search.html which extends Layout.html
	return render_template('search.html', clientsQ=clients,
	 productsQ=products, releasesQ=releases, clustersQ=clusters,
	 componentsQ=components, environmentsQ=environments, regionsQ=regions)

#This function communicates with the HTML and gathers the responses in order to load the table data.
@app.route('/result', methods=['GET','POST'])
def result():
	client_results = []
	data = request.form.keys()
	for values in data:
		stringified = values
		objectified = json.loads(values)
		#print(objectified['Clients'], objectified['Products'])
		clients = objectified['Clients']
		for client in clients:
			results = getResultByClient(client)
			client_results.append(results)
	return render_template('result.html',client_results=client_results)


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
	task_definitions = []
	for component in components:
		component_id = component.component_id
		task_definitions = Task_Definition.query.filter_by(component_id=component_id).all()
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
			result_record ={}
			result_record['client_name'] = client_name
			result_record['product_name'] = product_name
			result_record['release'] = release
			result_record['cluster_name'] = cluster_name
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
