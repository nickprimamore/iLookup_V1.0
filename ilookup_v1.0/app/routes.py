from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
from sqlalchemy import create_engine, Table, select, MetaData
from flask_sqlalchemy import SQLAlchemy
from awsdata import AWSData
from db_search import Search
import requests
import json
import boto3
import pprint


@app.route('/', methods=['GET', 'POST'])
#This function gathers all the data from the SQL tables to generate the search filters
def search():
	clients = Client.query.all()
	products = Product.query.all()
	releases = Product_Release.query.all()
	clusters = Cluster.query.all()
	components = Component.query.all()
	environments = []
	regions = []
	search(fromDate = "06/06/19")
	#Remove duplicate values such as "dev" and "qa"
	for cluster in clusters:
	 	if cluster.environment not in environments:
		 	environments.append(cluster.environment)
		if cluster.region not in regions:
			regions.append(cluster.region)
	#Renders the Result.html file which extends Search.html which extends Layout.html
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
		clients = objectified['Clients']
		products = objectified['Products']
		for client in clients:
			client_result = search(client_name=client)
			results.append(client_result)
		for product in products:
			product_result = search(product_name=product)
			results.append(product_result)
	return render_template('result.html', results=results)


def search(client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None):
	search = Search()
	print("calling search function.....")
	search_result = search.getSearchResult(client_name=client_name, product_name=product_name, release=release, cluster_name=cluster_name, region=region, environment=environment, toDate=toDate, fromDate=fromDate)
	pprint.pprint(search_result)
	return search_result



