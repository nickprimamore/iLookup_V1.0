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
