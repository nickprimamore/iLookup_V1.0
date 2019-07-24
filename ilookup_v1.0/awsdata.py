from app import db
from app.models import Product, Client, Cluster, Component, Task_Definition, Product_Release, CPRC
from sqlalchemy import func
from datetime import datetime
import boto3
import json
import pprint
import re


client = boto3.client("ecs")

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
			#pprint.pprint(tags)
			client_names = []
			client_name = "unknown"
			product_name = "unknown"
			product_release_number = ""
			environment= "UNKNOWN"
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

			self.populateClusters(cluster, cluster_name,environment,region,product_release_number,region_name, product_name,client_names )
				#clients = Client.query.all()
			# if (product_name!="unknown" and product_release_number!=""):
			# 	print(product_release_number) # tag/time
			# 	latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number)
			# 	product_release_id = self.populateProductRelease(product_name,latest_product_release_number)
			# if (product_name=="unknown" and product_release_number!=""):
			# 	print("------------------------------------------calling populateproduct----------------------------------------------")
			# 	# product_release_number = datetime.utcnow()
			# 	print(product_release_number) # time
			# 	latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number)
			# 	product_release_id = self.populateProductRelease("unknown",latest_product_release_number)
			# if (product_name!="unknown" and product_release_number==""):
			# 	product_release_number = datetime.utcnow()
			# 	latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number)
			# 	product_release_id = self.populateProductRelease(product_name,latest_product_release_number)
			# if (product_name=="unknown" and product_release_number==""):
			# 	product_release_number = datetime.utcnow()
			# 	latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number)
			# 	product_release_id = self.populateProductRelease("unknown",latest_product_release_number)


			# if (product_name!="" and product_release_number!="" ):
			# 	for client in client_names:
			# 		client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
			# 				#print(client_id)
			# 		self.populateCPRC(cluster_name,product_release_id, client_id[0])
			# else:
			# 	if len(client_names) > 0:
			# 		for client in client_names:
			# 			client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
			# 					#print(client_id)
			# 			self.populateCPRC(cluster_name,product_release_id, client_id[0])
			# 	else:
			# 		client_id = db.session.query(Client.client_id).filter_by(client_name=client_name).first()
			# 		self.populateCPRC(cluster_name,product_release_id, client_id[0])

	def populateClusters(self, cluster,cluster_name,environment,region,product_release_number,region_name, product_name,client_names):

		exists_cluster = db.session.query(Cluster.cluster_name).filter_by(cluster_name=cluster_name).filter_by(region=region).scalar() is not None
		if exists_cluster:

			print("nothing")
		else:
			cluster_value = Cluster(cluster_name=cluster_name, environment=environment,region=region,is_active=True)
			db.session.add(cluster_value)
				#print("New cluster is added to database")



				##get the cluster id by querying database
		cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster_name).first()
		print("Printing cluster  from populate cluster", cluster)
		self.populateComponent(cluster_id, cluster,cluster_name,product_release_number, region_name, product_name,client_names)


	def populateComponent(self, cluster_id, cluster,cluster_name, product_release_number, region_name, product_name,client_names):
		client = boto3.client("ecs", region_name=region_name)
		##fetch the services from AWS
		services = client.list_services(cluster = cluster)
		services = services["serviceArns"]
		cluster_task_list = []
		##iterate through each service in the cluster and store it in the database
		for service in services:
			print(service)
			mysplit= service.split("/")
			service_name = mysplit[-1]

			##check if the component exists in the database
			exists_component = db.session.query(Component.component_name).filter_by(component_name=service_name).filter_by(cluster_id=cluster_id[0]).scalar() is not None
			if exists_component:
				print(" Component Already Exists")
			else:
				print(service_name)
				component = Component(component_name = service_name, cluster_id= cluster_id[0], is_active=True)
				db.session.add(component)
				print("Added component to database: " + service_name)

			##get the component_id of the corresponding component
			component_id = db.session.query(Component.component_id).filter_by(component_name=service_name).first()

			tasks = client.list_tasks(cluster=cluster, serviceName=service)
			tasks = tasks["taskArns"]
			task_component_dict = {}
			task_component_dict["component_id"] = component_id
			print(tasks)
			task_component_dict["task"] = tasks
			task_component_dict["service"] = service
			cluster_task_list.append(task_component_dict)

			print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
			print(tasks)
			print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
		self.compareTaskDefinition(cluster,cluster_name,product_release_number,region_name, cluster_task_list, product_name,client_names)
			#self.populateTaskDefinition(component_id, cluster, service, latest_product_release_number, region_name)


	def populateTaskDefinition(self, component_id,cluster, service, product_release_number, region_name ):
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
				task_definition = client.describe_task_definition(taskDefinition = task_def_description)
				image = str(task_definition["taskDefinition"]["containerDefinitions"][0]["image"])
				cpu =  str(task_definition["taskDefinition"]["cpu"])
				memory =  str(task_definition["taskDefinition"]["memory"])
				revision = str(task_definition["taskDefinition"]["revision"])

				#if task_definition['taskDefinition'][release_number] is None:
				release_number = product_release_number # To be updated in later version


				if (lastStatus == "RUNNING"):
					date =  tasks_description["startedAt"]
				else:
					date = "None"

				##check if the task_definition entry exists in the database
				exists_task_definition = db.session.query(Task_Definition.task_definition_name).filter(Task_Definition.image_tag==image).filter(Task_Definition.revision==revision).filter(Task_Definition.release_number==release_number).scalar() is not None

				if exists_task_definition:
					print("Task_definition Already Exists")
				else:
					inserted_at = datetime.utcnow()
					task_defi = Task_Definition(task_definition_name=task_def, image_tag= image, revision= revision, date=date, cpu=cpu, memory=memory, component_id=component_id[0], release_number= release_number, is_active=True,inserted_at=inserted_at)
					db.session.add(task_defi)
					db.session.commit()
					#print("Added task_definition to database: " + task_def)


				#print("================================")


	def checkForLatestRelease(self, product_name, tag_release_number, cluster, region_name, cluster_name):

		print(product_name,tag_release_number)
		product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
		product_id = product_id[0]
		#print(product_id)
		# latestTime = db.session.query(func.max(Product_Release.inserted_at).label("inserted_at"), Product_Release.release_number, Product_Release.product_id)
		# #print(latestTime)
		# latestTime = latestTime.group_by(Product_Release.product_id).filter(Product_Release.product_id==product_id).first()

		latestTime = db.session.query(func.max(CPRC.product_release_id).label("product_release_id"),CPRC.cluster_id,Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name)

		latestTime = latestTime.group_by(CPRC.cluster_id).all()
		#print(latestRelease)
		print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		print(latestTime)
		# print(tag_release_number)
		# print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		#release_number = latestTime[0]

		if latestTime is None:
			tag_release_number = tag_release_number.lstrip()
			tag_release_number = tag_release_number.rstrip()
			#if tag_release_number == "" or tag_release_number=="unknown":
			print("JWNDNWDNWINDIWNDIWNDIWNDIWNIDNIWNDIWNDIWN")
			if not tag_release_number:
				print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
				print("Tag rrelease is:", tag_release_number)
				print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
				current_time = datetime.utcnow()
				release_number = current_time
			else:
				release_number = tag_release_number
				print("im in loop 1")
		elif latestTime[0][2]:
			if tag_release_number:
				print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
				print("latest time release number, tag_release_number", latestTime[0][2], tag_release_number)
				print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

				if latestTime[0][2] == tag_release_number:
					print("tag is not empty and two release numbers are equal!............")
					current_time = datetime.utcnow()
					release_number = current_time
				else:
					release_number = tag_release_number
			else:
				print("release number aws tag is empty")
				current_time = datetime.utcnow()
				release_number = current_time




			# update aws release tag here
		#if (tag_release_number != "") and (tag_release_number!=None):
		else:
			print(latestTime)
			release_number = tag_release_number
			print("im in loop 2")

		print(release_number)

		# call aws
		print("?????????????????>>>>>>>>>>>>>>>>>>>????????????????????")
		print(cluster)
		print("?????????????????>>>>>>>>>>>>>>>>>>>????????????????????")
		client = boto3.client("ecs", region_name=region_name)
		release_number = str(release_number)
		print(release_number)
		client.tag_resource(resourceArn=cluster, tags=[{'key':"Release", 'value': release_number}])

		return release_number


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

		#print("New entry is added in product table")y(Product.product_id).filter_by(product_id=product_id).scalar() is not None
		if exists_product:
			print("Product already exists in database")
		else:
			productValue = Product(product_name=product_name, is_active=True)
			db.session.add(productValue)
			db.session.commit()

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
			clientValue = Client(client_name=client_name,is_active=True)
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
			product_release_value = Product_Release(product_id=product_id, release_number=release_number, inserted_at=datetime.utcnow())
			db.session.add(product_release_value)
			#print('inserted new record in product_release table')

		product_release_id = db.session.query(Product_Release.product_release_id).filter_by(product_id=product_id).filter_by(release_number=release_number).first()
		product_release_id = product_release_id[0]
		#print(product_release_id)

		db.session.commit()
		return product_release_id



	def populateCPRC(self, cluster_name, product_release_id, client_id):

		print("////////////////////////////////////////////////////////////////////////////////")
		print("in cprc function: ", cluster_name, product_release_id, client_id)
		print("////////////////////////////////////////////////////////////////////////////////")


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
			print("Added new record in CPRC")

	def compareTaskDefinition(self,cluster, cluster_name, product_release_number, region_name,cluster_task_list, product_name, client_names):
		client = boto3.client("ecs", region_name=region_name)
		# print("Printing cluster and service", cluster,service)
		# tasks = client.list_tasks(cluster = cluster, serviceName = service)
		# tasks = tasks["taskArns"]
		#tasks = []
		# for cluster_task in cluster_task_list:
		# 	component_id = cluster_task["component_id"]
		# 	task = cluster_task["task"]
		# 	tasks.append(task)

		size = len(cluster_task_list)

		pprint.pprint(cluster_task_list)

		if size > 0:
			#task_descriptions = client.describe_tasks(cluster=cluster, tasks= tasks)
			#task_descriptions = task_descriptions["tasks"]
			db_task_defs = db.session.query(Cluster.cluster_name, Component.component_name, Task_Definition.task_definition_name,Task_Definition.revision, Task_Definition.is_active).filter(Task_Definition.component_id==Component.component_id,Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.is_active==True).all()

			print("==================================================")
			print("In compareTaskDefinition function", product_name, product_release_number, client_names)
			print("==================================================")

			if len(db_task_defs)>0:
				db_task_def_names = []
				for db_task in db_task_defs:
					db_task_def_names.append(db_task.task_definition_name)
				for cluster_task in cluster_task_list:
					#print("printing aws task..........",cluster_task["task"])
					# Assuming no new task added or old task deleted just revision number changed

					# check for emtpy list or None type object
					if len(cluster_task['task']) >0:

						task_descriptions = client.describe_tasks(cluster = cluster, tasks = cluster_task["task"])
						task_descriptions = task_descriptions["tasks"]
						task_def_description = task_descriptions[0]["taskDefinitionArn"]
						newsplit = task_def_description.split("/")
						task_def = newsplit[1]

						print(".................................................")
						print("task definition in aws", task_def)
						print(".................................................")



						if task_def not in db_task_def_names:
							print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
							print("task def in aws:", cluster_task["task"])
							print(db_task_def_names)
							print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
							#is_active = True
							latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number, cluster, region_name, cluster_name)

							for cluster_task in cluster_task_list:
								component_id = cluster_task["component_id"]
								service = cluster_task["service"]
								self.populateTaskDefinition(component_id,cluster,service,latest_product_release_number,region_name)

							product_release_id = self.populateProductRelease(product_name,latest_product_release_number)

							if (product_name!="" and product_release_number!="" ):
								if len(client_names) > 0:
									for client in client_names:
										client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
												#print(client_id)
										self.populateCPRC(cluster_name,product_release_id, client_id[0])
								else:
									client_id = db.session.query(Client.client_id).filter_by(client_name="unknown").first()
									self.populateCPRC(cluster_name,product_release_id, client_id[0])

							else:
								if len(client_names) > 0:
									for client in client_names:
										client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
												#print(client_id)
										self.populateCPRC(cluster_name,product_release_id, client_id[0])
								else:
									client_id = db.session.query(Client.client_id).filter_by(client_name="unknown").first()
									self.populateCPRC(cluster_name,product_release_id, client_id[0])


							### This means there will also be a new entry in cprc
							for db_task in db_task_def_names:
								task = Task_Definition.query.filter_by(task_definition_name=db_task).first()
								task.is_active = False
								db.session.commit()
							break


						else:
							print("Already exists in the database! - Task Def")
			else:
				#is_active = True
				#self.populateTaskDefinition(component_id,cluster,service,release_number,region_name, is_active)

				latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number,cluster, region_name, cluster_name)
				print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print("latest release:",latest_product_release_number)
				print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

				for cluster_task in cluster_task_list:
					component_id = cluster_task["component_id"]
					service = cluster_task["service"]
					self.populateTaskDefinition(component_id,cluster,service,latest_product_release_number,region_name)

				# if (product_name!="unknown" and product_release_number!=""):
				# 	print(product_release_number) # tag/time
				# 	product_release_id = self.populateProductRelease(product_name,latest_product_release_number)
				# if (product_name=="unknown" and product_release_number!=""):
				# 	print("------------------------------------------calling populateproduct----------------------------------------------")
				# 			# product_release_number = datetime.utcnow()
				# 	print(product_release_number) # time
				# 			#latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number)
				# 	product_release_id = self.populateProductRelease("unknown",latest_product_release_number)
				# if (product_name!="unknown" and product_release_number==""):
				# 	product_release_number = datetime.utcnow()
				# 			#latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number)
				# 	product_release_id = self.populateProductRelease(product_name,latest_product_release_number)
				# if (product_name=="unknown" and product_release_number==""):
				# 	product_release_number = datetime.utcnow()
				# 			#latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number)
				# 	product_release_id = self.populateProductRelease("unknown",latest_product_release_number)

				product_release_id = self.populateProductRelease(product_name,latest_product_release_number)

				if product_name == "iVerify":
					print("product_release_id: ", product_release_id)
					print("//////////////////////8888888888888888888888888888//////////////////////////////////////////888888888888888888888888888888888")

				if (product_name!="" and latest_product_release_number!="" ):
					if len(client_names) > 0:
						for client in client_names:
							client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
											#print(client_id)
							self.populateCPRC(cluster_name,product_release_id, client_id[0])
					else:
						client_id = db.session.query(Client.client_id).filter_by(client_name="unknown").first()
						self.populateCPRC(cluster_name,product_release_id, client_id[0])


				else:
					if len(client_names) > 0:
						for client in client_names:
							client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
											#print(client_id)
							self.populateCPRC(cluster_name,product_release_id, client_id[0])
					else:
						client_id = db.session.query(Client.client_id).filter_by(client_name="unknown").first()
						self.populateCPRC(cluster_name,product_release_id, client_id[0])








data = AWSData()

data.newMainFunction()

db.session.commit()

print("Completed")

latestRelease = db.session.query(func.max(CPRC.product_release_id).label("product_release_id"),CPRC.cluster_id,Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name=="asg-dev-iconductor-cluster")

latestRelease = latestRelease.group_by(CPRC.cluster_id).all()

print(latestRelease[0][2])
