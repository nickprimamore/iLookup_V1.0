import boto3

class Remove:

	def removeTags(self, region_name):
		client = boto3.client("ecs", region_name=region_name)

		#this api call fetches list of clients for the region passed as argument
		clusters = client.list_clusters()
		clusters = clusters["clusterArns"]
		for clusterArn in clusters:
			currentTags = client.list_tags_for_resource(resourceArn=clusterArn)
			tags = currentTags["tags"]
			for tag in tags:
				client.untag_resource(resourceArn=clusterArn, tagKeys=[tag['key']])

remove = Remove()
remove.removeTags("us-east-1")
remove.removeTags("eu-west-2")
