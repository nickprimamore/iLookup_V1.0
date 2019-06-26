from app import db
from app.models import Product, Client, Cluster, Component, Task_Definition
import boto3
import json
import pprint
import re

client = boto3.client("ecs")

class AWSData:

	def populateClusters(self):
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]

		for cluster in clusters:
			cluster_split = cluster.split(":")
			region = cluster_split[3]
			if region=="us-east-1":
				region = "N. Virginia"

			mysplit= cluster.split("/")

			cluster_name=mysplit[1]

			##check if the cluster entry already exists in database tanle
			exists_cluster = db.session.query(Cluster.cluster_name).filter_by(cluster_name=cluster_name).scalar() is not None
			if exists_cluster:
				print("Already Exists")
			else:
				##add the cluster to the database
				cluster_value = Cluster(cluster_name=cluster_name, environment="dev",region=region)
				db.session.add(cluster_value)
				print("New cluster is added to database")



			##get the cluster id by querying database
			cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster_name).first()
			self.populateComponent(cluster_id, cluster)

		print("done all!")


	def populateComponent(self, cluster_id, cluster):

		##fetch the services from AWS
		services = client.list_services(cluster = cluster)
		services = services["serviceArns"]

		##iterate through each service in the cluster and store it in the database
		for service in services:
			mysplit= service.split("/")
			service_name = mysplit[1]

			##check if the component exists in the database
			exists_component = db.session.query(Component.component_name).filter_by(component_name=service_name).scalar() is not None
			if exists_component:
				print(" Component Already Exists")
			else:
				component = Component(component_name = service_name, cluster_id= cluster_id[0])
				db.session.add(component)
				print("Added component to database: " + service_name)

			##get the component_id of the corresponding component
			component_id = db.session.query(Component.component_id).filter_by(component_name=service_name).first()
			self.populateTaskDefinition(component_id, cluster, service)

		print(" ")



	def populateTaskDefinition(self, component_id,cluster, service):
		tasks = client.list_tasks(cluster = cluster, serviceName = service)
		tasks = tasks["taskArns"]
		size = len(tasks)
		if size  > 0:
			task_descriptions = client.describe_tasks(cluster = cluster, tasks = tasks)
			task_descriptions = task_descriptions["tasks"]

			##iterate through all the tasks in the component
			for tasks_description in task_descriptions:
				lastStatus=tasks_description["lastStatus"]

				task_def_description = tasks_description["taskDefinitionArn"]
				newsplit = task_def_description.split("/")
				task_def = newsplit[1]
				task_definition = client.describe_task_definition(taskDefinition= task_def_description)
				image = str(task_definition["taskDefinition"]["containerDefinitions"][0]["image"])
				cpu =  str(task_definition["taskDefinition"]["cpu"])
				memory =  str(task_definition["taskDefinition"]["memory"])
				revision = str(task_definition["taskDefinition"]["revision"])
				if (lastStatus == "RUNNING"):
					date =  tasks_description["startedAt"]
				else:
					date = None

				##check if the task_definition entry exists in the database
				exists_task_definition = db.session.query(Task_Definition.task_definition_name).filter_by(task_definition_name=task_def).scalar() is not None

				if exists_task_definition:
					print("Task_definition Already Exists")
				else:
					task_defi = Task_Definition(task_definition_name=task_def, image_tag= image, revision= revision, date=date, cpu=cpu, memory=memory, component_id=component_id[0])
					db.session.add(task_defi)
					print("Added task_definition to database: " + task_def)


				print("================================")



data = AWSData()

data.populateClusters()

db.session.commit()

print("Completed")
