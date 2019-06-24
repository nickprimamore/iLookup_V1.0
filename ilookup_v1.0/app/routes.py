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
	print("Hello")
	data = request.form
	data = data.values()
	print(data)
	data = json.dumps(data)
	data = json.loads(data)
	print(type(data))
	data = json.dumps(data)
	# client = data[0]
	# client = json.loads(client)
	data = json.loads(data)
	print(data[0])
	client = data[0]

	client = str(client)
	print(type(client))
	print(client)
	# client = json.dumps(client)
	# client = json.loads(client)
	# print(type(client))
	# value = data["Client"]
	# print(data[0])
	# data = json.loads(data[0])
	# # data = json.dumps(data[0])
	# print(type(data))
	# client = data["Client"]
	return "<h1>Hello WOrld</h1>"
