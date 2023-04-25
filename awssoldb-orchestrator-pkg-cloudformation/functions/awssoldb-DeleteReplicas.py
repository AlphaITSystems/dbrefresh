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

        rdsclient = boto3.client('rds', region_name=awsregion)
        
        if dbservice == 'rds':
            dbinstance = event['dbinstance']
            response = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )
            
            replicas = response['DBInstances'][0]['ReadReplicaDBInstanceIdentifiers']
            
            if len(replicas) == 0:
                result = "No replicas to delete"
            else:
                dbarn = response['DBInstances'][0]['DBInstanceArn']
                
                if VerifyTags(rdsclient, dbarn):
                    for rep in replicas:
                        response = rdsclient.delete_db_instance(
                            DBInstanceIdentifier=rep,
                            SkipFinalSnapshot=True,
                            DeleteAutomatedBackups=False
                        )
                        
                    result = "Replicas deletion initiated"
                else:
                    raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
        elif dbservice == 'aurora':
            cluster = event['cluster']
            
            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )
            
            replicas = response['DBClusters'][0]['DBClusterMembers']
            
            if len(replicas) == 0:
                result = "No replicas to delete"
            else:
                dbarn = response['DBClusters'][0]['DBClusterArn']
                
                if VerifyTags(rdsclient, dbarn):
                    for rep in replicas:
                        if rep["IsClusterWriter"] == False:
                            response = rdsclient.delete_db_instance(
                                DBInstanceIdentifier=rep["DBInstanceIdentifier"],
                                SkipFinalSnapshot=True,
                                DeleteAutomatedBackups=False
                            )

                    result = "Replicas deletion initiated"
                else:
                    raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
        else:
            raise ValueError("Database service specified unknown or not supported")
        
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