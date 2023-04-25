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
        temppwd = event['temppwd']
        
        rdsclient = boto3.client('rds', region_name=awsregion)
        
        if dbservice == 'rds':
            dbinstance = event['dbinstance']
            
            responsedb = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )
            
            dbarn = responsedb['DBInstances'][0]['DBInstanceArn']
            
            if VerifyTags(rdsclient, dbarn):
                secclient = boto3.client('secretsmanager', region_name=awsregion)
                
                secretname = event['secretname']
                
                masterusr = responsedb['DBInstances'][0]['MasterUsername']
                password = temppwd
                engine = responsedb['DBInstances'][0]['Engine']
                host = responsedb['DBInstances'][0]['Endpoint']['Address']
                port = responsedb['DBInstances'][0]['Endpoint']['Port']
                dbname = responsedb['DBInstances'][0]['DBName']
                dbInstanceIdentifier = responsedb['DBInstances'][0]['DBInstanceIdentifier']
                
                secretstring = '{ "username": "' + masterusr + '", "password": "' + password + '", "engine": "' + engine + '", "host": "' + host + '", "port": "' + str(port) + '", "dbname": "' + dbname + '", "dbInstanceIdentifier": "' + dbInstanceIdentifier + '" }'
                
                responsesec = secclient.create_secret(
                    Name=secretname,
                    Description=secretname,
                    SecretString=secretstring,
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': 'DbRestore'
                        },
                    ]
                )
                
                logger.info("Secret created")
                
                rotation = event['rotation']
                rotationdays = event['rotationdays']
                lambdaarn = event['lambdaarn']
                
                logger.info(rotation)
                
                if rotation == "true":
                    responserot = secclient.rotate_secret(
                        SecretId=secretname,
                        RotationLambdaARN=lambdaarn,
                        RotationRules={
                            'AutomaticallyAfterDays': rotationdays
                        }
                    )
                
                    logger.info("Rotation enabled")
                    result = "Secret created with rotation enabled"
                else:
                    result = "Secret created with rotation disabled"
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
        elif dbservice == 'aurora':
            cluster = event['cluster']
            
            responsedb = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )
            
            dbarn = responsedb['DBClusters'][0]['DBClusterArn']
            
            if VerifyTags(rdsclient, dbarn):
                secclient = boto3.client('secretsmanager', region_name=awsregion)

                secretname = event['secretname']
                
                masterusr = responsedb['DBClusters'][0]['MasterUsername']
                password = temppwd
                engine = responsedb['DBClusters'][0]['Engine']
                host = responsedb['DBClusters'][0]['Endpoint']
                port = responsedb['DBClusters'][0]['Port']
                dbname = responsedb['DBClusters'][0]['DatabaseName']
                dbClusterIdentifier = responsedb['DBClusters'][0]['DBClusterIdentifier']
                
                secretstring = '{ "username": "' + masterusr + '", "password": "' + password + '", "engine": "' + engine + '", "host": "' + host + '", "port": "' + str(port) + '", "dbname": "' + dbname + '", "dbClusterIdentifier": "' + dbClusterIdentifier + '" }'
                
                responsesec = secclient.create_secret(
                    Name=secretname,
                    Description=secretname,
                    SecretString=secretstring,
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': 'DbRestore'
                        },
                    ]
                )
                
                logger.info("Secret created")
                
                rotation = event['rotation']
                rotationdays = event['rotationdays']
                lambdaarn = event['lambdaarn']
                
                if rotation == "true":
                    responserot = secclient.rotate_secret(
                        SecretId=secretname,
                        RotationLambdaARN=lambdaarn,
                        RotationRules={
                            'AutomaticallyAfterDays': rotationdays
                        }
                    )
                
                    logger.info("Rotation enabled")
                    result = "Secret created with rotation enabled"
                else:
                    result = "Secret created with rotation disabled"
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
        else:
            raise ValueError("Database service specified unknown or not supported by this function")
        
        return {
            "statusCode": 200,
            "body": result
        }
        
    else:
        result = "Creation of the secret skipped"
        
        return {
            "statusCode": 200,
            "body": result
        }
