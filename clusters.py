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
	# Start

	mysplit= cluster.split("/")
	cluster_name = str(cluster_count)+ ". Cluster Name: " + mysplit[1] + ", "+region 

	print(cluster_name)
	print("|")
	print("|")
	print("|")
	print("V")

	# mysplit = cluster.split("-")
	# print(mysplit)
	# End
	for tasks_description in task_descriptions:
		lastStatus=tasks_description["lastStatus"]
		#print(tasks_description["startedAt"])
		#print(tasks_description["taskDefinitionArn"])
		task_def_description = tasks_description["taskDefinitionArn"]
		newsplit = task_def_description.split("/")
		task_def = " Task Definition: "+newsplit[1]
		task_definition = client.describe_task_definition(taskDefinition= task_def_description)
		image = "   Image: "+str(task_definition["taskDefinition"]["containerDefinitions"][0]["image"])
		cpu = "   CPU: "+ str(task_definition["taskDefinition"]["cpu"])
		memory = "   Memory: " + str(task_definition["taskDefinition"]["memory"])
		revision = "   Revision: "+ str(task_definition["taskDefinition"]["revision"])
		status = "   Last Status: " + lastStatus
		print(str(task_counter) + "." + task_def)
		#print(task_def)
		print(image)
		print(cpu)
		print(memory)
		print(revision)
		print(status)
		if (lastStatus == "RUNNING"):
			date = "   Date Started At: " + str(tasks_description["startedAt"])
			print(date)
		print("")	
		task_counter = task_counter + 1
	cluster_count = cluster_count + 1

