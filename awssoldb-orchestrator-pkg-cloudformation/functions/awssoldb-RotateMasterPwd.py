import boto3
import logging
import json
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
            
            dbarn = response['DBInstances'][0]['DBInstanceArn']
            
            if VerifyTags(rdsclient, dbarn):
                secclient = boto3.client('secretsmanager', region_name=awsregion)
    
                secretname = event['secretname']

                response = secclient.describe_secret(
                    SecretId=secretname
                )
                    
                try:
                    if response['RotationEnabled'] == True:
                        response_rotation = secclient.rotate_secret(
                            SecretId=secretname
                        )
                        
                        result = "Secret rotated"
                    else:
                        result = "Secret not rotated, rotation not enabled"
                except:
                    result = "Secret not rotated, rotation not enabled"
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
            
        elif dbservice == 'aurora':
            cluster = event['cluster']
            
            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )
            
            dbarn = response['DBClusters'][0]['DBClusterArn']
            
            if VerifyTags(rdsclient, dbarn):
                secclient = boto3.client('secretsmanager', region_name=awsregion)

                secretname = event['secretname']
                
                response = secclient.describe_secret(
                    SecretId=secretname
                )
                
                try:
                    if response['RotationEnabled'] == True:
                        response_rotation = secclient.rotate_secret(
                            SecretId=secretname
                        )
                        
                        result = "Secret rotated"
                    else:
                        result = "Secret not rotated, rotation not enabled"
                except:
                    result = "Secret not rotated, rotation not enabled"
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
        else:
            raise ValueError("Database service specified unknown or not supported by this function")
        
        return {
            "statusCode": 200,
            "body": result
        }
        
    else:
        result = "Rotation master password skipped"
        
        return {
            "statusCode": 200,
            "body": result
        }
