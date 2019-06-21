from app import db
from app.models import Product, Client, Cluster
import boto3
import json
import pprint 
import re

client = boto3.client("ecs")


clusters = client.list_clusters()

clusters = clusters["clusterArns"]
cluster_count = 1
for cluster in clusters:
	task_counter = 1
	tasks = client.list_tasks(cluster = cluster)
	tasks = tasks["taskArns"]
	task_descriptions = client.describe_tasks(cluster = cluster, tasks = tasks)
	task_descriptions = task_descriptions["tasks"]
	cluster_split = cluster.split(":")
	region = cluster_split[3]
	if region=="us-east-1":
		region = "N. Virginia"

	mysplit= cluster.split("/")
	#cluster_name = str(cluster_count)+ ". Cluster Name: " + mysplit[1] + ", "+region 
	cluster_name=mysplit[1]
	cluster = Cluster(cluster_name=cluster_name, environment="dev",region=region)
	db.session.add(cluster)

db.session.commit()

print("Completed")


