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
	data = request.form['data']
	print(data)
	return "<h1>Hello WOrld</h1>"
