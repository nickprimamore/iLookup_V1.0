from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
import requests
import json
import boto3

@app.route('/', methods=['GET', 'POST'])
def search():
	clients = Client.query.all()
	products = Product.query.all()
	releases = Product_Release.query.all()
	clusters = Cluster.query.all()
	components = Component.query.all()
	return render_template('search.html', clientsQ=clients, productsQ=products, releasesQ=releases, clustersQ=clusters, componentsQ=components)

@app.route('/result', methods=['GET','POST'])
def result():
	data = request.form.keys()
	print(data)
	for values in data:
		stringified = values
		objectified = json.loads(values)
		print(objectified['Clients'], objectified['Products'])
	return "<h1>Hello WOrld</h1>"
