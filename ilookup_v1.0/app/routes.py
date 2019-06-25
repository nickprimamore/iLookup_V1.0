from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
from sqlalchemy import create_engine, Table, select, MetaData
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import boto3

@app.route('/', methods=['GET', 'POST'])
def search():
	clients = Client.query.all()
	products = Product.query.all()
	return render_template('search.html', clients=clients, products=products)

@app.route('/result', methods=['GET','POST'])
def result():
	data = request.form.keys()
	print(data)
	for values in data:
		stringified = values
		objectified = json.loads(values)
		print(objectified['Clients'], objectified['Products'])
	return "<h1>Hello World</h1>"

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
def getResultByClient():
	input_client_name = "Marsh"
	cprc = getCPRC(input_client_name)

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
			client_name = input_client_name
			task_definition_name = task_definition.task_definition_name
			image_tag = task_definition.image_tag
			revision = task_definition.revision
			date = task_definition.date
			cpu = task_definition.cpu
			memory = task_definition.memory
			print(client_name,product_name, release,cluster_name,task_definition_name,image_tag,revision,date, environment, region, cpu,memory)
	return "MyDB"

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