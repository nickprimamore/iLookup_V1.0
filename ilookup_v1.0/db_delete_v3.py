from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
from datetime import datetime
import pprint, json, boto3
import sys

f=open("errorLog.txt", "a+")
class DeactivateRecords:

	def deactivateClient(self, client_name=None, cluster_name=None, product_name=None, release_number=None):
		try:
			client_id = db.session.query(Client.client_id).filter(Client.client_name==client_name).first()
			product_id = db.session.query(Product.product_id).filter(Product.product_id==Product_Release.product_id).filter(Product.product_name==product_name).first()
			product_id = product_id[0]
			if product_id:
				prid = db.session.query(Product_Release.product_release_id).filter(Product_Release.product_id==product_id).filter(Product_Release.release_number==release_number).first()
				if prid:
					prid = prid[0]
					print("deactivate client function is called......................")
					if client_id:
						client_id = client_id[0]
						print(client_id)


						cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.client_id==client_id).distinct().all()
						print(cluster_count)

						if cluster_count:
							cprc_record= db.session.query(CPRC).filter(CPRC.client_id==client_id).filter(CPRC.cluster_id==Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).filter(CPRC.product_release_id==prid).first()
							cprc_record.is_active=False
							db.session.commit()
							# if(len(cluster_count)>1):
								#just disable the cprc record
								# for cluster_id in cluster_count:
								# 	print("_-_-_-_-_-_-_-_-_-_-_-_-_-__-___----____---_____-----_________--------___________---------------------")
								# 	print(cluster_id[0])
								# 	cprc_records = db.session.query(CPRC).filter(CPRC.client_id==client_id).filter(CPRC.cluster_id==cluster_id[0]).filter(CPRC.product_release_id==prid).all()
								# 	for cprc in cprc_records:
								# 		cprc.is_active = False


							if (len(cluster_count)==1):
								#deactivate client and cprc
								print("only one cluster and one client")
								client = db.session.query(Client).filter(Client.client_id==client_id).first()
								client.is_active = False
								cprc_records = db.session.query(CPRC).filter(CPRC.client_id==client_id).filter(CPRC.cluster_id==cluster_count[0][0]).all()
								#print(CPRC.is_active)
								if len(cprc_records)>0:
									for cprc in cprc_records:
										cprc.is_active = False
								print("deactivated the client")

							db.session.commit()

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_delete_v3.py - Function: deactivateClient - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()

	def deactivateProduct(self, product_name=None):

		try:
			product_id = db.session.query(Product.product_id).filter(Product.product_name==product_name).first()
			product_id = product_id[0]
			# cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
			# cluster_id = cluster_id[0]
			cluster_count = db.session.query(CPRC.cluster_id).filter(CPRC.product_release_id==Product_Release.product_release_id, Product.product_id==Product_Release.product_id).filter(Product.product_id==product_id).distinct().all()
			print(cluster_count)

			if len(cluster_count)>1:
				for cluster_id in cluster_count:
					cprc_records = db.session.query(CPRC).filter(CPRC.cluster_id==cluster_id).all()
					for cprc in cprc_records:
						cprc.is_active = False

			else:
				#deactivate client and cprc
				print("only one cluster and one product")
				product = db.session.query(Product).filter(Product.product_id==product_id).first()
				product.is_active = False
				print(cluster_count[0][0])
				cprc_records = db.session.query(CPRC).filter(CPRC.cluster_id==cluster_count[0][0]).all()
				#print(CPRC.is_active)
				for cprc in cprc_records:
					cprc.is_active = False

			db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_delete_v3.py - Function: deactivateProduct - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()




	def deactivateCluster(self, cluster_name):
		try:
			cluster_id = db.session.query(Cluster.cluster_id).filter(Cluster.cluster_name==cluster_name).first()
			cluster_id = cluster_id[0]
			cluster = db.session.query(Cluster).filter(Cluster.cluster_id==cluster_id).first()
			cluster.is_active = False

			#deactivating cprc records
			cprc_records = db.session.query(CPRC).filter(CPRC.cluster_id==cluster_id).all()
				#print(CPRC.is_active)
			for cprc in cprc_records:
				cprc.is_active = False
			self.deactivateTaskDef(cluster_name)
			db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_delete_v3.py - Function: deactivateCluster - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	def deactivateTaskDef(self, cluster_name):
		try:
			components = db.session.query(Component).filter(Cluster.cluster_id==Component.cluster_id).filter(Cluster.cluster_name==cluster_name).all()
			if len(components)>0:
				for component in components:
					component.is_active = False
					task_definitions = db.sessiomn.query(Task_Definition).filter(Task_Definition.component_id==component.component_id).all()
					for task_definition in task_definitions:
						task_definition.is_active = False
				db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_delete_v3.py - Function: deactivateTaskDef - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	def activateTaskDef(self, service_arn, cluster_arn, uniClient):
		try:
			tasks = uniClient.list_tasks(cluster = cluster_arn, serviceName = service_arn)
			tasks = tasks["taskArns"]
			size = len(tasks)
			if size > 0:
				task_descriptions = uniClient.describe_tasks(cluster = cluster_arn, tasks = tasks)
				task_descriptions = task_descriptions["tasks"]
				##iterate through all the tasks in the component
				for tasks_description in task_descriptions:
					lastStatus=tasks_description["lastStatus"]
					task_def_description = tasks_description["taskDefinitionArn"]
					newsplit = task_def_description.split("/")
					task_def = newsplit[1]
					task_definition = uniClient.describe_task_definition(taskDefinition = task_def_description)
					image = str(task_definition["taskDefinition"]["containerDefinitions"][0]["image"])
					revision = str(task_definition["taskDefinition"]["revision"])

					td_exists = db.session.query(Task_Definition).filter(Task_Definition.task_definition_name==task_def).filter(Task_Definition.image_tag==image).filter(Task_Definition.revision==revision).filter(Task_Definition.is_active==False).first()

					if td_exists:
						td_exists.is_active = True

				db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_delete_v3.py - Function: activateTaskDef - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	def activateComponent(self, cluster_id, cluster_arn, uniClient):
		try:
			db_components = db.session.query(Component).filter(Component.cluster_id==cluster_id).all()

			services = uniClient.list_services(cluster = cluster_arn)
			services = services["serviceArns"]
			cluster_task_list = []
			aws_components = []
			##iterate through each service in the cluster and store it in the database
			for service in services:
				print(service)
				self.activateTaskDef(service,cluster_arn,uniClient)
				# get task def objects here here
				mysplit= service.split("/")
				service_name = mysplit[-1]
				aws_components.append(service_name)

			if len(db_components) > 0:
				if len(aws_components) > 0:
					for component in db_components:
						component_name = component.component_name
						if component_name in aws_components:
							component.is_active= True

					db.session.commit()
		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_delete_v3.py - Function: activateComponent - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()


	#def updateProductisActiveStatus(self, product_name,):

		#fetch list of all active products from aws


		#fetch list of all active products from database
		#activeProducts = db.session.query(Product.product_name).filter(Product.is_active=True)

		#for the given product name check if it belong to other cluster
		#checkForMultiple = db.session.query(Product.product_name).filter(Product.product_id==Product_Release.product_id, CPRC.product_release_id==Product_Release.product_release_id)

	# def makeProductInactive

	# def getClusterArn(self, cluster_name, region_name):
	# 	client = boto3.client("ecs", region_name=region_name)
	# 	cluster_list = client.list_clusters()
	# 	cluster_list = cluster_list["clusterArns"]
	# 	for cluster in cluster_list:
	# 		if cluster_name in cluster:
	# 			return cluster
	# 	return None

	# def fetchClusterTags(self,cluster_name,region_name):
	# 	client = boto3.client("ecs", region_name=region_name)
	# 	clusterArn = self.getClusterArn(cluster_name, region_name)
	# 	res = client.list_tags_for_resource(resourceArn = clusterArn)
	# 	tagsDict =  {}
	# 	tagsDict["cluster_name"] = cluster_name
	# 	for tag in res["tags"]:
	# 		tagsDict[tag["key"]] = tag["value"]
	# 	print(tagsDict)
	# 	return tagsDict



# update = DeactivateRecords()
# #update.deactiveClient(client_name="Aon")
# update.deactivateProduct(product_name="iVerify")

# update.fetchClusterTags("asg-uat-iconductor-cluster","eu-west-2")
