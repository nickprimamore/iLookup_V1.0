from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
import requests
import json
import boto3

@app.route('/', methods=['GET', 'POST'])
#This function gathers all the data from the SQL tables to generate the search filters
def search():
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
	return render_template('result.html', clientsQ=clients, productsQ=products, releasesQ=releases, clustersQ=clusters, componentsQ=components, environmentsQ=environments, regionsQ=regions)

@app.route('/result', methods=['GET','POST'])
#This function communicates with the HTML and gathers the responses in order to load the table data.
def result():
	#Parsing through the Immutable Multi Dictionary in order to get values that can be used within SQL
	data = request.form.keys()
	for values in data:
		stringified = values
		objectified = json.loads(values)
	return render_template('result.html')
