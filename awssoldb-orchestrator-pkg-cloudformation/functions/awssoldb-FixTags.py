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
        
        if dbservice == 'rds':
            dbinstance = event['dbinstance']
            dbarn = event['dbarn']
    
            rdsclient = boto3.client('rds', region_name=awsregion)
            
            if VerifyTags(rdsclient, dbarn):
                response = rdsclient.add_tags_to_resource(
                    ResourceName=dbarn,
                    Tags=[
                        {
                            'Key': 'refresh-instance',
                            'Value': dbinstance
                        }
                    ]
                )
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
                
            result = "Tags modified"
        elif dbservice == 'aurora':
            cluster = event['cluster']
            cluarn = event['cluarn']
            
            dbinstance = event['dbinstance']
            dbarn = event['dbarn']
            
            rdsclient = boto3.client('rds', region_name='us-east-1')

            if VerifyTags(rdsclient, dbarn):
                response = rdsclient.add_tags_to_resource(
                    ResourceName=cluarn,
                    Tags=[
                        {
                            'Key': 'refresh-cluster',
                            'Value': cluster
                        }
                    ]
                )
            
                response = rdsclient.add_tags_to_resource(
                    ResourceName=dbarn,
                    Tags=[
                        {
                            'Key': 'refresh-instance',
                            'Value': dbinstance
                        }
                    ]
                )
                    
                result = "Tags modified"
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