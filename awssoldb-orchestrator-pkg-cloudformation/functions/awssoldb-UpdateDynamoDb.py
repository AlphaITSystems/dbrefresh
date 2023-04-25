import json
import boto3
import logging
from datetime import datetime
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    torun = event['torun']
    
    if torun == "true":
        awsregion = os.environ['AWS_REGION']
        
        dbservice = event['dbservice']
        dbinstance = event['dbinstance']
        application = event['application']
        environment = event['environment']
        source = event['source']
        restoretype = event['restoretype']
        tablename = event['tablename']
        
        status = "completed"
    
        #https://www.programiz.com/python-programming/datetime/strftime
        recordingtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dynamoDbClient = boto3.client('dynamodb', region_name=awsregion)
        
        if restoretype == "fromsnapshot":
            rdsClient = boto3.client('rds', region_name=awsregion)
            
            snapshot = event['snapshot']
            
            if dbservice == "rds":
                responserds = rdsClient.describe_db_snapshots(
                    DBSnapshotIdentifier=snapshot
                )
                
                restoredatetemp = responserds['DBSnapshots'][0]['SnapshotCreateTime']
                restoredate = str(restoredatetemp.strftime("%Y-%m-%d %H:%M:%S"))
            elif dbservice == "aurora":
                responseaurora = rdsClient.describe_db_cluster_snapshots(
                    DBClusterSnapshotIdentifier=snapshot
                )
            else:
                raise ValueError("Database service specified unknown or not supported by this function")
                
                restoredatetemp = responseaurora['DBClusterSnapshots'][0]['SnapshotCreateTime']
                restoredate = str(restoredatetemp.strftime("%Y-%m-%d %H:%M:%S"))
        elif restoretype == "restorepoint":
            restoredatetemp = datetime.strptime(event['restoretime'],"%Y-%m-%d %H:%M:%S")
            restoredate = restoredatetemp.strftime("%Y-%m-%d %H:%M:%S")
            snapshot = "null"
        elif restoretype == "latestpoint":
            restoredate = recordingtime
            snapshot = "null"
        elif restoretype == "fastcloning":
            restoredate = recordingtime
            snapshot = "null"
            
        response = dynamoDbClient.put_item(
            TableName=tablename,
            Item={
                'appname': {
                    'S': application
                },
                'environment': {
                    'S': environment
                },
                'dbinstance': {
                    'S': dbinstance
                },
                'source': {
                    'S': source
                },
                'restoretype': {
                    'S': restoretype
                },
                'snapshot': {
                    'S': snapshot
                },
                'status': {
                    'S': status
                },
                'restoredate': {
                    'S': restoredate
                },
                'recordingtime': {
                    'S': recordingtime
                }
            }
        )
            
        logger.info("DynamoDB table updated")
        result = 'Lambda function completed successfully'
            
        return {
            "statusCode": 200,
            "body": result
        }
    else:
        result = 'Lambda function skipped'
        
        return {
            "statusCode": 200,
            "body": result
        }