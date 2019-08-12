from app import db
from app.models import Product, Client, Cluster, Component, Task_Definition, Product_Release, CPRC
from sqlalchemy import func
from datetime import datetime
import boto3
import json
import pprint
import re
import sys
from regions import regionObject

# this client object will be used to make api calls to ecs
client = boto3.client("ecs")


f=open("errorLog.txt", "a+")
#this class contains functions to fetch data from AWS and feed them into database
class AWSData:

	#this is the main function and it calls mainFunction() and passes the region name as argument to mainFunction
	def newMainFunction(self):

		for region in regionObject:
			self.mainFunction(regionObject[region])



	#this function takes the region_name as argument and makes api calls to the aws resources in that region
	#first it fetches the all the clusters and then for each clusters it fetches the AWS resources
	#it calls fetchClusterTafs() function and fetches tag info like product name, clients, environment,
	#and release number, then populates Client and Product table
	#it also calls populateCluster() function and passes the required information to populate other
	#database tables
	def mainFunction(self,region_name):


		client = boto3.client("ecs", region_name=region_name)

		#this api call fetches list of clients for the region passed as argument
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]

		#this for loop fetches aws tags for each cluster listed above by calling fetchClusterTags() function
		for cluster in clusters:
			cluster_split = cluster.split(":")
			region = cluster_split[3]
			region = list(regionObject.keys())[list(regionObject.values()).index(region)]

			mysplit= cluster.split("/")

			cluster_name=mysplit[1]
			tags = self.fetchClusterTags(cluster,cluster_name,region_name)

			#the following variables are assigned with some default values in case if the tag value is missing
			client_names = []
			client_name = "UNKNOWN"
			product_name = "UNKNOWN"
			product_release_number = ""
			environment= "UNKNOWN"

			#this for loop fetches all the tag values for each key in the tag
			for key in tags:
				if ("Customer") in key:
					client_name = tags[key]
					client_names.append(client_name)
					self.populateClient(client_name)
				if ("Application") in key:
					product_name = tags["Application"]
					self.populateProduct(product_name)
				if ("Release") in key:
					product_release_number = tags[key]
				if ("Environment") in key:
					environment = tags[key]

			# #following if conditions check if particular tag is present in the AWS, if not it will add tag with "UNKNOWN" value
			if product_name == "UNKNOWN":
				client.tag_resource(resourceArn=cluster, tags=[{'key':"Application", 'value': product_name}])

			if client_name == "UNKNOWN":
				client.tag_resource(resourceArn=cluster, tags=[{'key':"Customer", 'value': client_name}])

			if environment == "UNKNOWN":
				client.tag_resource(resourceArn=cluster, tags=[{'key':"Environment", 'value': environment}])

			self.populateClusters(cluster, cluster_name,environment,region,product_release_number,region_name, product_name,client_names )

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: mainFunction - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#this function populates the cluster table and then calls populateComponent function
	#first it checks if the record already exists and if not then only adds new record
	def populateClusters(self, cluster,cluster_name,environment,region,product_release_number,region_name, product_name,client_names):

		try:
			exists_cluster = db.session.query(Cluster.cluster_name).filter_by(cluster_name=cluster_name).filter_by(region=region).scalar() is not None
			if exists_cluster:
				print("cluster already exists")

			else:
				cluster_value = Cluster(cluster_name=cluster_name, environment=environment,region=region,is_active=True)
				db.session.add(cluster_value)
				print("New cluster is added to database")

			cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster_name).first()
			self.populateComponent(cluster_id, cluster,cluster_name,product_release_number, region_name, product_name,client_names)

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: populateClusters - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()
	#this function populates the component table and then calls CompareTaskDefiniton() function
	#first it checks if the record already exists and if not then only adds new record
	def populateComponent(self, cluster_id, cluster,cluster_name, product_release_number, region_name, product_name,client_names):
		try:
			client = boto3.client("ecs", region_name=region_name)

			##fetch the services from AWS
			services = client.list_services(cluster = cluster)
			services = services["serviceArns"]
			cluster_task_list = []
			##iterate through each service in the cluster and store it in the database
			for service in services:
				#print(service)
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
				component_id = db.session.query(Component.component_id).filter_by(component_name=service_name).filter_by(cluster_id=cluster_id[0]).first()

				tasks = client.list_tasks(cluster=cluster, serviceName=service)
				tasks = tasks["taskArns"]
				task_component_dict = {}
				task_component_dict["component_id"] = component_id
				task_component_dict["task"] = tasks
				task_component_dict["service"] = service
				cluster_task_list.append(task_component_dict)


			#if self.checkRollback(cluster, cluster_name, product_release_number, region_name,cluster_task_list, product_name, client_names):
			#  	print("rollBACK")
			# else:
			self.compareTaskDefinition(cluster,cluster_name,product_release_number,region_name, cluster_task_list, product_name,client_names)

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: populateComponent - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	#this function checks if the task definition record already exists in the database
	#if not then it adds new record to the database
	def populateTaskDefinition(self, component_id,cluster, service, product_release_number, region_name ):

		try:
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
						print("Task_definition Already Exists.....................................", task_def )
					else:
						inserted_at = datetime.utcnow()
						task_defi = Task_Definition(task_definition_name=task_def, image_tag= image, revision= revision, date=date, cpu=cpu, memory=memory, component_id=component_id[0], release_number= release_number, is_active=True,inserted_at=inserted_at)
						db.session.add(task_defi)
						db.session.commit()
						print("Added task_definition to database: " + task_def)

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: populateTaskDefinition - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#this function checks for the latest release number and return the latest release number
	#also updates the aws tag with new release number
	def checkForLatestRelease(self, product_name, tag_release_number, cluster, region_name, cluster_name):

		try:
			print(product_name,tag_release_number)
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
			product_id = product_id[0]

			#gets the product_release_id with max release number for the give cluster
			latestTime = db.session.query(func.max(CPRC.product_release_id).label("product_release_id"),CPRC.cluster_id,Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name)
			latestTime = latestTime.group_by(CPRC.cluster_id).all()

			old_release_number = db.session.query(Product_Release.release_number).filter(Product_Release.product_release_id == latestTime[0][0]).first()
			#print(latestRelease)
			print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			print(latestTime)
			print("latest time release number", latestTime[0][2])

			# print(tag_release_number)
			print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			#release_number = latestTime[0]

			#this if-else statement makes sure to get the correct new release number
			#if latestTime is null and there is no aws tag value for release  number then new timestamp is created and
			#returned as the new release number
			# else if latestTime and tag release number is not none then both values are compared
			#if they are equal means new release number must be there i.e. timestamp needs to be created
			if (latestTime is None) or (len(latestTime)<1):
				tag_release_number = tag_release_number.lstrip()
				tag_release_number = tag_release_number.rstrip()

				if not tag_release_number:
					current_time = datetime.utcnow()
					release_number = current_time
				else:
					release_number = tag_release_number

			else:
				if tag_release_number:

					old_release_number = db.session.query(Product_Release.release_number).filter(Product_Release.product_release_id == latestTime[0][0]).first()
					print("/////////////////////////////////////////////////////////////////////////")
					print("old release_number", old_release_number[0])
					print(type(old_release_number))
					print("tag_release_number", tag_release_number)
					print(type(tag_release_number))
					print("/////////////////////////////////////////////////////////////////////////")

					if old_release_number[0] == tag_release_number:
						print("tag is not empty and two release numbers are equal!............")
						current_time = datetime.utcnow()
						release_number = current_time
					else:
						print("in the else part of else-if")
						release_number = tag_release_number


				else:
					print("release number aws tag is empty")
					current_time = datetime.utcnow()
					release_number = current_time


			client = boto3.client("ecs", region_name=region_name)
			release_number = str(release_number)

			print("?????????????????>>>>>>>>>>>>>>>>>>>????????????????????")
			print("Latest release_number is: " , release_number)
			print("?????????????????>>>>>>>>>>>>>>>>>>>????????????????????")

			#updates the AWS tag
			client.tag_resource(resourceArn=cluster, tags=[{'key':"Release", 'value': release_number}])

			return release_number

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: checkForLatestRelease - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#this function fetches the AWS tag for the given cluster and region and returns it in the key:value format
	def fetchClusterTags(self,clusterArn, cluster_name,region_name):

		try:
			client = boto3.client("ecs", region_name=region_name)
			res = client.list_tags_for_resource(resourceArn = clusterArn)
			tagsDict =  {}
			tagsDict["cluster_name"] = cluster_name
			for tag in res["tags"]:
				tagsDict[tag["key"]] = tag["value"]
			return tagsDict

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: fetchClusterTags - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()



	#this function populates the product table
	#it checks if the product already exists, if it does not exists then creates new record
	def populateProduct(self, product_name):

		try:
			product_id = db.session.query(Product.product_id).filter_by(product_name=product_name).first()
			if product_id is not None:
				product_id = product_id[0]

			exists_product = db.session.query(Product.product_id).filter_by(product_id=product_id).scalar() is not None

			if exists_product:
				print("Product already exists in database")
			else:
				productValue = Product(product_name=product_name, is_active=True)
				db.session.add(productValue)
				db.session.commit()
				print("new product is added")
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: populateProduct - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#this function populates the client table
	#it checks if the client already exists, if it does not exists then creates new record
	def populateClient(self, client_name):

		try:
			client_id = db.session.query(Client.client_id).filter_by(client_name=client_name).first()

			if client_id is not None:
				client_id = client_id[0]

			exists_client = db.session.query(Client.client_id).filter_by(client_id=client_id).scalar() is not None

			if exists_client:
				print("Client already exists in database")
			else:
				clientValue = Client(client_name=client_name,is_active=True)
				db.session.add(clientValue)
				db.session.commit()
				print("New entry is added in client table")

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: populateClient - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#this function populates the product_release table
	#it checks if the product_release record already exists, if it does not exists then creates new record
	def populateProductRelease(self, product_name, release_number):

		try:
			product_id = db.session.query(Product.product_id).filter_by(product_name=product_name).first()
			if product_id is not None:
				product_id = product_id[0]

			exists_product_release = db.session.query(Product_Release.product_release_id).filter_by(product_id=product_id).filter_by(release_number=release_number).scalar() is not None

			if exists_product_release:
				print("already exists record for product_release")

			else:
				product_release_value = Product_Release(product_id=product_id, release_number=release_number, inserted_at=datetime.utcnow())
				db.session.add(product_release_value)
				print('inserted new record in product_release table')

			product_release_id = db.session.query(Product_Release.product_release_id).filter_by(product_id=product_id).filter_by(release_number=release_number).first()
			product_release_id = product_release_id[0]

			db.session.commit()
			return product_release_id
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: populateProductRelease - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#this function populates the cprc table
	#it checks if the cprc record already exists, if it does not exists then creates new record
	#it also deactivates old cprc records
	def populateCPRC(self, cluster_name, product_release_id, client_id):

		try:
			cluster_id = db.session.query(Cluster.cluster_id).filter_by(cluster_name=cluster_name).first()
			if cluster_id is not None:
				cluster_id = cluster_id[0]

			exists_cprc = db.session.query(CPRC).filter_by(client_id=client_id).filter_by(cluster_id=cluster_id).filter_by(product_release_id=product_release_id).scalar() is not None

			if exists_cprc:
				print("already exists record for cprc")
			else:
				cprc = db.session.query(CPRC).filter(Cluster.cluster_id==CPRC.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(CPRC.client_id==client_id).all()
				if (len(cprc)> 0 ):
					for record in cprc:
						record.is_active = False
					db.session.commit()

				cprc_value = CPRC(client_id=client_id, cluster_id=cluster_id, product_release_id=product_release_id)
				db.session.add(cprc_value)
				db.session.commit()
				print("Added new record in CPRC")

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: populateCPRC - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()



	#this function fetches the task definitions from aws and fetches the active task definitons(latest ones) from database
	#compares both the task definitions, if they are not same means there is new release for that cluster and new task definitions are added to the database
	#if there are new prior records of the task_definitions for that cluster then we directly add new task_definitions from aws to database
	def compareTaskDefinition(self,cluster, cluster_name, product_release_number, region_name,cluster_task_list, product_name, client_names):
		try:
			client = boto3.client("ecs", region_name=region_name)

			size = len(cluster_task_list)


			if size > 0:
				#task_descriptions = client.describe_tasks(cluster=cluster, tasks= tasks)
				#task_descriptions = task_descriptions["tasks"]
				db_task_defs = db.session.query(Cluster.cluster_name, Component.component_name, Task_Definition.task_definition_name,Task_Definition.revision, Task_Definition.is_active).filter(Task_Definition.component_id==Component.component_id,Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.is_active==True).all()
				all_db_task_defs_details = db.session.query(Cluster.cluster_name, Component.component_name, Task_Definition.task_definition_name,Task_Definition.revision, Task_Definition.is_active).filter(Task_Definition.component_id==Component.component_id,Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).all()

				# print("==================================================")
				# print("In compareTaskDefinition function", product_name, product_release_number, client_names)
				# print("==================================================")

				if len(db_task_defs)>0:
					db_task_def_names = []
					for db_task in db_task_defs:
						db_task_def_names.append(db_task.task_definition_name)

					all_db_task_defs  = []
					for db_task in all_db_task_defs_details:
						all_db_task_defs.append(db_task.task_definition_name)



					for cluster_task in cluster_task_list:
						#print("printing aws task..........",cluster_task["task"])
						# Assuming no new task added or old task deleted just revision number changed

						# check for emtpy list or None type objec

						if len(cluster_task['task']) >0:

							task_descriptions = client.describe_tasks(cluster = cluster, tasks = cluster_task["task"])
							task_descriptions = task_descriptions["tasks"]
							task_def_description = task_descriptions[0]["taskDefinitionArn"]
							newsplit = task_def_description.split("/")
							task_def = newsplit[1]

							print(".................................................")
							print("task definition in aws", task_def)
							print(".................................................")

							##add the code to check the length of tasks from db and tasks from AWS ->because if some task from aws deleted then it can connsider as a new release

							if task_def not in db_task_def_names:
								# print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
								# print("task def in aws:", cluster_task["task"])
								# print(db_task_def_names)
								# print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
								#is_active = True



								print()
								print("got the new release for cluster",  cluster_name)
								latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number, cluster, region_name, cluster_name)


								for db_task in all_db_task_defs:
									print("deactivating the task definition............................................................",db_task)
									task = Task_Definition.query.filter_by(task_definition_name=db_task).all()
									for task_rec in task:
										task_rec.is_active = False
									db.session.commit()

								for cluster_task in cluster_task_list:
									component_id = cluster_task["component_id"]
									service = cluster_task["service"]
									self.populateTaskDefinition(component_id,cluster,service,latest_product_release_number,region_name)

								print("Added new taslk definitions to database")

								product_release_id = self.populateProductRelease(product_name,latest_product_release_number)

								if (product_name!="" and product_release_number!="" ):
									if len(client_names) > 0:
										for client in client_names:
											client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
													#print(client_id)
											self.populateCPRC(cluster_name,product_release_id, client_id[0])
									else:
										client_id = db.session.query(Client.client_id).filter_by(client_name="UNKNOWN").first()
										self.populateCPRC(cluster_name,product_release_id, client_id[0])

								else:
									if len(client_names) > 0:
										for client in client_names:
											client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
													#print(client_id)
											self.populateCPRC(cluster_name,product_release_id, client_id[0])
									else:
										client_id = db.session.query(Client.client_id).filter_by(client_name="UNKNOWN").first()
										self.populateCPRC(cluster_name,product_release_id, client_id[0])



								### This means there will also be a new entry in cprc

								break


							else:
								print("Already exists in the database! - Task Def")
				else:
					#is_active = True
					#self.populateTaskDefinition(component_id,cluster,service,release_number,region_name, is_active)

					latest_product_release_number = self.checkForLatestRelease(product_name,product_release_number,cluster, region_name, cluster_name)
					# print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					# print("latest release:",latest_product_release_number)
					# print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

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

					# if product_name == "iVerify":
					# 	print("product_release_id: ", product_release_id)
					# 	print("//////////////////////8888888888888888888888888888//////////////////////////////////////////888888888888888888888888888888888")

					if (product_name!="" and latest_product_release_number!="" ):
						if len(client_names) > 0:
							for client in client_names:
								client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
												#print(client_id)
								self.populateCPRC(cluster_name,product_release_id, client_id[0])
						else:
							client_id = db.session.query(Client.client_id).filter_by(client_name="UNKNOWN").first()
							self.populateCPRC(cluster_name,product_release_id, client_id[0])


					else:
						if len(client_names) > 0:
							for client in client_names:
								client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
												#print(client_id)
								self.populateCPRC(cluster_name,product_release_id, client_id[0])
						else:
							client_id = db.session.query(Client.client_id).filter_by(client_name="UNKNOWN").first()
							self.populateCPRC(cluster_name,product_release_id, client_id[0])
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - Function: compareTaskDefinition - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()



	# def checkRollback(self, cluster, cluster_name, product_release_number, region_name,cluster_task_list, product_name, client_names):
	# 	client = boto3.client("ecs", region_name=region_name)
	# 	#1. Fetch tasks from aws for any cluster
	# 	# #print(cluster_task_list)
	# 	# #2. get lastest task defs from AWS(active ones) and release numbers
	# 	# release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, Product.product_id==Product_Release.product_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Product.product_name==product_name).order_by(Product_Release.inserted_at.desc()).all()
	# 	# print(release_numbers[1][0])
	#
	#
	# 	# db_task_defs = db.session.query(Task_Definition.task_definition_name).filter(Task_Definition.component_id==Component.component_id,Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.release_number== release_numbers[1][0]).all()
	# 	# pprint.pprint(db_task_defs)
	#
	# 	# 3. compare aws task defs with latest ones in database
	#
	# 	#    if match then return
	# 	#    else get the second last task defs using releases list
	# 	#		 if match then
	# 	#
	# 	# 		else
	# 	# 			return false and call compareTaskDefinition()
	#
	# 	#print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&................")
	# 	#print(cluster, cluster_name, product_release_number, region_name,cluster_task_list, product_name, client_names)
	# 	release_numbers = db.session.query(Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id, Product.product_id==Product_Release.product_id, CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Product.product_name==product_name).order_by(Product_Release.inserted_at.desc()).all()
	# 	#print(release_numbers)
	#
	# 	if (len(release_numbers)>1):
	# 		rollback_defs = db.session.query(Cluster.cluster_name, Component.component_name, Task_Definition.task_definition_name,Task_Definition.revision, Task_Definition.is_active).filter(Task_Definition.component_id==Component.component_id,Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.release_number==release_numbers[1][0]).all()
	#
	# 		#db task defintion names list
	# 		db_task_def_names = []
	# 		for db_task in rollback_defs:
	# 			db_task_def_names.append(db_task.task_definition_name)
	#
	# 		#print(db_task_def_names)
	#
	# 		#AWS Tasks
	# 		aws_task_list = []
	#
	# 		#print(cluster_task_list)
	#
	# 		if(len(cluster_task_list)>0):
	# 			for cluster_task in cluster_task_list:
	# 				if cluster_task["task"]:
	# 					task_descriptions = client.describe_tasks(cluster = cluster, tasks = cluster_task["task"])
	# 					task_descriptions = task_descriptions["tasks"]
	# 					task_def_description = task_descriptions[0]["taskDefinitionArn"]
	# 					newsplit = task_def_description.split("/")
	# 					task_def = newsplit[1]
	# 					aws_task_list.append(task_def)
	#
	# 			print(aws_task_list)
	#
	# 			#check for length
	# 			if(len(db_task_def_names)!=len(aws_task_list)):
	# 				print("No rollBACK")
	# 				return False
	#
	# 			else:
	# 				db_task_def_names.sort()
	# 				aws_task_list.sort()
	# 				pprint.pprint(db_task_def_names)
	# 				pprint.pprint(aws_task_list)
	# 				#print("^^^^^^^^^^^^^^^^^^^^^^^^LISTTTT^^^^^^^^^^^^^^^^^^^^^")
	# 				if db_task_def_names==aws_task_list:
	# 					releaseNum = str(release_numbers[1][0])
	# 					oldReleaseNum = str(release_numbers[1][0])
	# 					newerVersion = ""
	# 					if "R" in str(releaseNum):
	# 						newInt = int(releaseNum[-1]) + 1
	# 						releaseNum = releaseNum[:-1] + str(newInt)
	#
	# 						product_release_id = self.populateProductRelease(product_name, releaseNum)
	# 						if len(client_names) > 0:
	# 							for client in client_names:
	# 								client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
	# 												#print(client_id)
	#
	# 								cprc = db.session.query(CPRC).filter(CPRC.client_id==Client.client_id,Cluster.cluster_id==CPRC.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Client.client_name==client).filter(CPRC.is_active==True).first()
	# 								if cprc:
	# 									cprc.is_active=False
	# 									db.session.commit()
	# 								self.populateCPRC(cluster_name,product_release_id, client_id[0])
	# 						else:
	# 							cprc = db.session.query(CPRC).filter(CPRC.client_id==Client.client_id,Cluster.cluster_id==CPRC.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Client.client_name=="UNKNOWN").filter(CPRC.is_active==True).first()
	# 							if cprc:
	# 								cprc.is_active=False
	# 								db.session.commit()
	# 							client_id = db.session.query(Client.client_id).filter_by(client_name="UNKNOWN").first()
	# 							self.populateCPRC(cluster_name,product_release_id, client_id[0])
	#
	# 						db_task_defs = db.session.query(Task_Definition.task_definition_name).filter(Task_Definition.component_id==Component.component_id,Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.is_active==True).all()
	# 						for db_task in db_task_defs:
	# 							task = Task_Definition.query.filter_by(task_definition_name=db_task[0]).first()
	# 							task.is_active = False
	# 						db.session.commit()
	#
	#
	# 						for cluster_task in cluster_task_list:
	# 							component_id = cluster_task["component_id"]
	# 							service = cluster_task["service"]
	# 							self.populateTaskDefinition(component_id,cluster,service,releaseNum,region_name)
	#
	#
	# 						print("deactivated")
	#
	# 						return False
	#
	# 					else:
	# 					   	releaseNum = releaseNum + " R1"
	# 					   	newerVersion = oldReleaseNum + " R2"
	#
	# 						product_release = db.session.query(Product_Release).filter(Product.product_id==Product_Release.product_id).filter(Product_Release.release_number==oldReleaseNum).filter(Product.product_name==product_name).first()
	# 						product_release.release_number = releaseNum
	# 						db.session.commit()
	#
	# 						task_defs = db.session.query(Task_Definition).filter(Cluster.cluster_id==Component.cluster_id,Component.component_id==Task_Definition.component_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.release_number==oldReleaseNum).all()
	# 						#print(task_defs)
	# 						for res in task_defs:
	# 							res.release_number = releaseNum
	# 						db.session.commit()
	#
	# 						new_product_release_id = self.populateProductRelease(product_name, newerVersion)
	# 						if len(client_names) > 0:
	# 							for client in client_names:
	# 								client_id = db.session.query(Client.client_id).filter_by(client_name=client).first()
	# 												#print(client_id)
	# 								cprc = db.session.query(CPRC).filter(CPRC.client_id==Client.client_id,Cluster.cluster_id==CPRC.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Client.client_name==client).filter(CPRC.is_active==True).first()
	# 								if cprc:
	# 									cprc.is_active=False
	# 									db.session.commit()
	# 								self.populateCPRC(cluster_name, new_product_release_id, client_id[0])
	# 						else:
	# 							cprc = db.session.query(CPRC).filter(CPRC.client_id==Client.client_id,Cluster.cluster_id==CPRC.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Client.client_name=="UNKNOWN").filter(CPRC.is_active==True).first()
	# 							if cprc:
	# 								cprc.is_active=False
	# 								db.session.commit()
	# 							client_id = db.session.query(Client.client_id).filter_by(client_name="UNKNOWN").first()
	# 							self.populateCPRC(cluster_name, new_product_release_id, client_id[0])
	#
	# 						#deactivate the task definitions in database
	# 						db_task_defs = db.session.query(Task_Definition.task_definition_name).filter(Task_Definition.component_id==Component.component_id,Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(Task_Definition.is_active==True).all()
	# 						for db_task in db_task_defs:
	# 							task = Task_Definition.query.filter_by(task_definition_name=db_task[0]).first()
	# 							task.is_active = False
	# 						db.session.commit()
	#
	# 						for cluster_task in cluster_task_list:
	# 							component_id = cluster_task["component_id"]
	# 							service = cluster_task["service"]
	# 							self.populateTaskDefinition(component_id,cluster,service,newerVersion,region_name)
	#
	#
	#
	# 						print("deactivated in else")
	#
	#
	#
	# 						#print("populaed task definition")
	#
	#
	# 						return True
	#
	# 				else:
	# 					print("not same")
	# 					return False
	#
	#
	#
	#











# data = AWSData()

# # # # #data.checkRollback('arn:aws:ecs:us-east-1:735360830536:cluster/Bnft-CarConn-qa-us-cluster', 'Bnft-CarConn-qa-us-cluster', '2019-08-07 15:50:36.408291 R1', 'us-east-1', [{'component_id': (56,), 'service': 'arn:aws:ecs:us-east-1:735360830536:service/Bnft-CarConn-qa-us-cluster/iasg-qa-carrier-connect-fuse-svc', 'task': ['arn:aws:ecs:us-east-1:735360830536:task/Bnft-CarConn-qa-us-cluster/f601e386d37642e7bd0e6ce2fc05c064']}], 'UNKNOWN', ['UNKNOWN'])
# data.newMainFunction()

# db.session.commit()

# print("Completed")

# latestRelease = db.session.query(func.max(CPRC.product_release_id).label("product_release_id"),CPRC.cluster_id,Product_Release.release_number).filter(CPRC.product_release_id==Product_Release.product_release_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name=="asg-dev-iconductor-cluster")

# latestRelease = latestRelease.group_by(CPRC.cluster_id).all()

# print(latestRelease[0][2])
