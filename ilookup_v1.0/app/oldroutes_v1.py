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

@app.route('/db', methods=['GET','POST'])
def db():
	clients = Client.query.all()
	# products = Product.query.all()
	# product_release = Product_Release.query.all()
	# cluster = Cluster.query.all()
	# component_type = Component_Type.query.all()
	# component = Component.query.all()
	# task_definitions = Task_Definition.query.all()
	# cprc = CPRC.query.all()

	region_input = "North Virginia"
	client_input = "Aon"
	product_input = ""
	component_input = ""
	release_input= ""
	environment_input = ""
	cluster_input = ""

	print(clients)
	for client in clients:
		if (client_input==client.client_name):
			client_id = client.client_id

	# cprc = CPRC.query.filter_by(client_id=client_id).all()
	# print(cprc)

	# for res in cprc:
	# 	cluster_id = res.cluster_id
	# 	components = Component.query.filter_by(cluster_id=cluster_id).all()
	# 	print(components)
	# 	for component in components:
	# 		component_id = component.component_id
	# 		task_definitions = Task_Definition.query.filter_by(component_id=component_id).all()
	# 		print(task_definitions)
	# 		for task in task_definitions:
	# 			print(task.task_definition_name, task.image_tag)

		# print(res.client_id, res.cluster_id, res.product_release_id)


	## Client ID is known from client name after searching through CLient table
	client_id = 1

	## Using client id we get cluster, prid from cprc
	cprc_result = CPRC.query.filter_by(client_id=client_id).all()
	cprc= cprc_result[0]
	cluster_id = cprc.cluster_id
	prid = cprc.product_release
	mycluster = Cluster.query.get(cluster_id)

	## from Cluster table we get cluster name
	cluster_name = mycluster.cluster_name

	## from component table we get componenets using cluster id as a foreign key
	components = Component.query.filter_by(cluster_id=cluster_id).all()


	## For each compnent we print the correspnding task def details using component id as foreign key 
	for component in components:
		print(component.component_name)
		component_id = component.component_id

		task_definitions = Task_Definition.query.filter_by(component_id=component_id)

		for task_definition in task_definitions:
			print(cluster_name, task_definition.task_definition_name, task_definition.image_tag, task_definition.revision, task_definition.date, task_definition.cpu, task_definition.memory)

	#print(cluster_id)

	# component_results = Component.query.join(Cluster, Component.component_id==Cluster.cluster_id).filter_by(cluster_id=cluster_id).all()

	# for component in component_results:
	# 	component_id = component.component_id
	# 	task_definition = Task_Definition.query.join(Component, Task_Definition.component_id==Component.component_id).add_columns(Task_Definition.task_definition_name,Task_Definition.image_tag,Task_Definition.date).filter_by(component_id=component_id).all()
	# 	print(task_definition)
	print("Hello WOrld")
	#print(result)
	# print(client.client_id)
###################################################################################

###################################################################################

	# for task_definition in task_definitions:
	# 	result = task_definition.task_definition_name
	# 	print(result)
	# 	print(task_definition.task_definition_name, task_definition.image_tag)
	# mydb(db)
	return "Hello World"

# def mydb():
# 	search_result = db.session.query(Client, Product_Release, Product, Cluster,
# 	Component, Task_Definition).innerjoin(CPRC.client_id == Client.client_id, 
# 	CPRC.product_release_id == Product_Release.product_release_id, 
# 	Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id, 
# 	Component.cluster_id == Cluster.cluster_id, 
# 	Component.component_id == Task_Definition.component_id).add_columns(Client.client_name, Product.product_name).filter(Client.client_name=="Aon")

	# 			#result = CPRC.query.join(Client, Client.client_id==CPRC.client_id).add_columns(Client.client_name).filter(Client.client_id==1)
	# print(search_result)
	# return "Hello"			
# for res in search_result:
# 	print(res.Client.client_name, res.Product.product_name, res.Product_Release.release_number, res.Cluster.cluster_name)

