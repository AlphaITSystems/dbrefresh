import json
import boto3
import os


def lambda_handler(event, context):
    
    torun = event['torun']

    if torun == "true":
        sns = boto3.client("sns", region_name = "us-east-1")
    
        service = event['dbservice']
        application = event["application"]
        environment = event['environment']
        source = event['source']
        dbinstance = event["dbinstance"]
        restoretype = event["restoretype"]
        topicarn = event["topicarn"]
        
        subj = "Application " + application + ": restore of the database instance " + dbinstance + " [FAILED]"
        msg = "The restore of the database instance " + dbinstance + " has failed."
        
        snsresponse = sns.publish(
            TargetArn=topicarn,
            Subject=subj,
            Message=msg
        )
        
        result = "Message published"
    else:
        result = "Notification skipped"
        
    return {
        "statusCode": 200,
        "body": result
    }