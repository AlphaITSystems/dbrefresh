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
    import os
    
    torun = event['torun']
    
    if torun == "true":
        dbservice = event['dbservice']
        dbinstance = event['dbinstance']
        
        newdbinstance = dbinstance[:-4]
        
        rdsclient = boto3.client('rds', region_name='us-east-1')
        
        if dbservice == 'rds' or dbservice == 'aurora':
            response = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )            
            
            dbarn = response['DBInstances'][0]['DBInstanceArn']

            if VerifyTags(rdsclient, dbarn):
                response = rdsclient.modify_db_instance(
                    DBInstanceIdentifier=dbinstance,
                    NewDBInstanceIdentifier=newdbinstance,
                    ApplyImmediately=True
                )
                
                #logger.info("Rename of the database initiated")
                result = "Rename of the database initiated"
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
        else:
            result = "Database service unknown"
        
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