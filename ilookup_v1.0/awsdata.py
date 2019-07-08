from app import db
from app.models import Product, Client, Cluster, Component, Task_Definition, Product_Release, CPRC
import boto3
import json
import pprint
import re


# client = boto3.client("ecs")

class AWSData:
	def newMainFunction(self):
		nvirginia = "us-east-1"  
		london = "eu-west-2"
		print("Running London Region")
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		self.mainFunction(london)
		print("Running N. Virginia Region")
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		self.mainFunction(nvirginia)

	def mainFunction(self,region_name):
		client = boto3.client("ecs", region_name=region_name)
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]

		for cluster in clusters:
			cluster_split = cluster.split(":")
			region = cluster_split[3]
			if region=="us-east-1":
				region = "N. Virginia"
			else:
				region = "London"

			mysplit= cluster.split("/")

			cluster_name=mysplit[1]
			tags = self.fetchClusterTags(cluster,cluster_name,region_name)
			print(cluster_name)
			pprint.pprint(tags)
			client_names = []
			client_name = "unknown"
			product_name = "unknown"
			product_release_number = "unknown"
			for key in tags:
				if ("Client") in key:
					client_name = tags[key]
					client_names.append(client_name)
					self.populateClient(client_name) 
					#print("Tagging client name", client_name)
				if ("Product") in key:
					product_name = tags["Product"]
					self.populateProduct(product_name)
					#print("Tagging product name", product_name)
				if ("Release") in key:
					product_release_number = tags[key]
				if ("Environment") in key:
					environment = tags[key]
			
			if (product_name!="" and product_release_number!="" ):
				product_release_id = self.populateProductRelease(product_name,product_release_number)
			else:
				product_release_id = self.populateProductRelease("unknown","unknown")
			
			self.populateClusters(cluster, cluster_name,environment,region,product_release_number,region_name)
				#clients = Client.query.all()
			
			if (product_name!="" and product_release_number!="" ):
				for client in client_names:
					client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
							#print(client_id)
					self.populateCPRC(cluster_name,product_release_id, client_id[0])
			else:
				if len(client_names) > 0:
					for client in client_names:
						client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
								#print(client_id)
						self.populateCPRC(cluster_name,product_release_id, client_id[0])
				else:
					client_id = db.session.query(Client.client_id).filter_by(client_name=client_name).first()
					self.populateCPRC(cluster_name,product_release_id, client_id[0])

	def populateClusters(self, cluster,cluster_name,environment,region,product_release_number,region_name):
		
		exists_cluster = db.session.query(Cluster.cluster_name).filter_by(cluster_name=cluster_name).scalar() is not None
		if exists_cluster:
			print("nothing")
		else:
			cluster_value = Cluster(cluster_name=cluster_name, environment=environment,region=region)
			db.session.add(cluster_value)
				#print("New cluster is added to database")



				##get the cluster id by querying database
		cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster_name).first()
		self.populateComponent(cluster_id, cluster,product_release_number, region_name)


	def populateComponent(self, cluster_id, cluster, release_number, region_name):
		client = boto3.client("ecs", region_name=region_name)
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
			self.populateTaskDefinition(component_id, cluster, service, release_number, region_name)


	def populateTaskDefinition(self, component_id,cluster, service, release_number, region_name):
		client = boto3.client("ecs", region_name=region_name)
		tasks = client.list_tasks(cluster = cluster, serviceName = service)
		tasks = tasks["taskArns"]
		size = len(tasks)
		if size > 0:
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
				
				#if task_definition['taskDefinition'][release_number] is None:
				release_number = release_number # To be updated in later version
				

				if (lastStatus == "RUNNING"):
					date =  tasks_description["startedAt"]
				else:
					date = "None"

				##check if the task_definition entry exists in the database
				exists_task_definition = db.session.query(Task_Definition.task_definition_name).filter(Task_Definition.image_tag==image).filter(Task_Definition.release_number==release_number).scalar() is not None

				if exists_task_definition:
					print("Task_definition Already Exists")
				else:
					task_defi = Task_Definition(task_definition_name=task_def, image_tag= image, revision= revision, date=date, cpu=cpu, memory=memory, component_id=component_id[0], release_number= release_number)
					db.session.add(task_defi)
					#print("Added task_definition to database: " + task_def)


				#print("================================")

	def fetchClusterTags(self,clusterArn, cluster_name,region_name):
		client = boto3.client("ecs", region_name=region_name)
		res = client.list_tags_for_resource(resourceArn = clusterArn)
		tagsDict =  {}
		tagsDict["cluster_name"] = cluster_name
		for tag in res["tags"]: 
			tagsDict[tag["key"]] = tag["value"]
		return tagsDict   

	def populateProduct(self, product_name):
		product_id = db.session.query(Product.product_id).filter_by(product_name=product_name).first()
		print("This is product id for", product_name,product_id)
		if product_id is not None:
			product_id = product_id[0]
		# product_id = product_id[0]
		#print(product_id)
		exists_product = db.session.query(Product.product_id).filter_by(product_id=product_id).scalar() is not None
		if exists_product:
			print("Product already exists in database")
		else:
			productValue = Product(product_name=product_name)
			db.session.add(productValue)
			db.session.commit()
			#print("New entry is added in product table")
	
	def populateClient(self, client_name):
		client_id = db.session.query(Client.client_id).filter_by(client_name=client_name).first()
		print("this is client id.......", client_id, client_name)
		#print(client_id)
		if client_id is not None:
			client_id = client_id[0]
		#print(client_id)
		exists_client = db.session.query(Client.client_id).filter_by(client_id=client_id).scalar() is not None
		if exists_client:
			print("Client already exists in database")
		else:
			clientValue = Client(client_name=client_name)
			db.session.add(clientValue)
			db.session.commit()
			#print("New entry is added in client table")

	def populateProductRelease(self, product_name, release_number):

		product_id = db.session.query(Product.product_id).filter_by(product_name=product_name).first()
		if product_id is not None:
			product_id = product_id[0]
		#print(product_id)
		exists_product_release = db.session.query(Product_Release.product_release_id).filter_by(product_id=product_id).filter_by(release_number=release_number).scalar() is not None

		#print(exists_product_release)
		if exists_product_release:
			print("already exists record for product_release")		
		
		else:		
			product_release_value = Product_Release(product_id=product_id, release_number=release_number)
			db.session.add(product_release_value)
			#print('inserted new record in product_release table')

		product_release_id = db.session.query(Product_Release.product_release_id).filter_by(product_id=product_id).filter_by(release_number=release_number).first()
		product_release_id = product_release_id[0]
		#print(product_release_id)

		db.session.commit()
		return product_release_id



	def populateCPRC(self, cluster_name, product_release_id, client_id):
		cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster_name).first()
		if cluster_id is not None:
			cluster_id = cluster_id[0]

		exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id).filter_by(cluster_id=cluster_id).filter_by(product_release_id=product_release_id).scalar() is not None

		if exists_cprc:
			print("already exists record for cprc")	
		else:
			cprc_value = CPRC(client_id=client_id, cluster_id=cluster_id, product_release_id=product_release_id)
			db.session.add(cprc_value)
			#print('inserted new record in product_release table')
			db.session.commit()			

data = AWSData()

data.newMainFunction()

db.session.commit()

print("Completed")
