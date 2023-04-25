import json
import boto3
import logging
from datetime import datetime
import os


def lambda_handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    torun = event['torun']

    if torun == "true":
        dbservice = event['dbservice']
        application = event['application']
        environment = event['environment']
        dbinstance = event['dbinstance']
        source = event['source']
        restoretype = event['restoretype']
        tablename = event['tablename']
        
        #errormsg = event['errormsg']
        #logger.info(errormsg)
        #status = "incomplete - error: " + errormsg['Error']
        status = "failed"
    
        #https://www.programiz.com/python-programming/datetime/strftime
        recordingtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dynamoDbClient = boto3.client('dynamodb', region_name='us-east-1')
        
        if restoretype == "fromsnapshot":
            rdsClient = boto3.client('rds', region_name='us-east-1')
            
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
        
        result = "Lambda function completed succesfully"
    else:
        result = "Lambda function skipped"
        
    return {
        "statusCode": 200,
        "body": result
    }