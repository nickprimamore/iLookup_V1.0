from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
import requests
import json
import boto3

@app.route('/', methods=['GET', 'POST'])
def search():
<<<<<<< HEAD
	return render_template('search.html')
=======
	return "Hello World"
>>>>>>> 37e8c9ef20153f01a1ba050b6baf534a9fd1389d
