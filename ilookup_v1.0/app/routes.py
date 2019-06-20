from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.models import Client, Product, Product_Release, Cluster, Component_Type, Component, Task_Definition, CPRC
import requests
import json
import boto3

@app.route('/', methods=['GET', 'POST'])
def search():
	return render_template('search.html')

@app.route('/result', methods=['POST'])
def result():
	result=request.form
	return render_template('result.html', result=result)
