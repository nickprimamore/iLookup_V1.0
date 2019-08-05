import boto3
client = boto3.client("ecs", region_name=region_name)

		#this api call fetches list of clients for the region passed as argument
clusters = client.list_clusters()
clusters = clusters["clusterArns"]
for clusterArn in clusters:
	currentTags = uniClient.list_tags_for_resource(resourceArn=clusterArn)
	tags = currentTags["tags"]
	for tag in tags:
		uniClient.untag_resource(resourceArn=awsCluster, tag=[tag['key']])