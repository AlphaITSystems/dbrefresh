import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def VerifyTags(rdsclient, dbarn):
    response = rdsclient.list_tags_for_resource(
	    ResourceName=dbarn
    )

    tagValue = ""
    
    for x in response['TagList']:
	    if x['Key'] == "refresh":
		    tagValue = x['Value']

    if tagValue == "true":
    	check = True
    else:
    	check =  False

    return check
    

def lambda_handler(event, context):
    torun = event['torun']
    
    if torun == "true":
        awsregion = os.environ['AWS_REGION']
        
        dbservice = event['dbservice']
        cluster = event['cluster']
        
        newcluster = cluster[:-4]
        
        rdsclient = boto3.client('rds', region_name=awsregion)
        
        if dbservice == 'aurora':
            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )
            
            dbarn = response['DBClusters'][0]['DBClusterArn']
                
            if VerifyTags(rdsclient, dbarn):
                response = rdsclient.modify_db_cluster(
                    DBClusterIdentifier=cluster,
                    NewDBClusterIdentifier=newcluster,
                    ApplyImmediately=True
                )
                
                result = "Rename of the cluster initiated"
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
            
        else:
            raise ValueError("Database service specified unknown or not supported by this function")
        
        return {
            "statusCode": 200,
            "body": result
        }
        
    else:
        result = "Lambda function skipped"
        
        return {
            "statusCode": 200,
            "body": result
        }