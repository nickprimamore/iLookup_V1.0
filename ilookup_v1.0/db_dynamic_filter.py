from app import db
from app.models import Product, Client, Cluster, Task_Definition, Product_Release, CPRC, Component
from datetime import datetime
import pprint, json
import sys

f=open("errorLog.txt", "a+")
class DynamicFilter:

	# this function is used to dynamically filter the search dropdowns
	def getFirstFilterResult(self,client_name=None, product_name=None, release=None, cluster_name=None, region=None, environment=None, toDate=None, fromDate=None, is_active=None):
		try:
			#this query fetches all the records
			search_result = db.session.query(CPRC, Client, Product_Release, Product, Cluster).filter(CPRC.client_id == Client.client_id, CPRC.product_release_id == Product_Release.product_release_id,
				Product_Release.product_id ==  Product.product_id, CPRC.cluster_id == Cluster.cluster_id).distinct()

			products = []
			releases = []
			environments = []
			regions = []
			clusters = []
			clients = []

			# each if condition filter out the search_result if some value is passed for that parameter
			if client_name:
				search_result = search_result.filter(Client.client_name== client_name)

			if product_name:
				search_result = search_result.filter(Product.product_name== product_name)

			if release:
				search_result = search_result.filter(Product_Release.release_number==release)

			if cluster_name:
				search_result = search_result.filter(Cluster.cluster_name==cluster_name)

			if region:
				search_result = search_result.filter(Cluster.region==region)

			if environment:
				search_result = search_result.filter(Cluster.environment==environment)

			return search_result

		except Exception as ex:
			date = datetime.utcnow()
			tb = sys.exc_info()[2]
			errorMsg = str(date) + " - File: db_dynamic_filter.py - Function: getFirstFilterResult - " + str(ex.args) + " - on line " + str(tb.tb_lineno) + " \r\n"
			f.write(errorMsg)
			f.close()
