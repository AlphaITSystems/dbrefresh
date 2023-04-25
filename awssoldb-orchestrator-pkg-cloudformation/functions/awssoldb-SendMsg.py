import json
import boto3
import os


def lambda_handler(event, context):
    
    torun = event['torun']

    if torun == "true":
        awsregion = os.environ['AWS_REGION']
        
        dbservice = event['dbservice']
        application = event["application"]
        environment = event['environment']
        source = event['source']
        dbinstance = event["dbinstance"]
        restoretype = event["restoretype"]
        topicarn = event["topicarn"]
        
        sns = boto3.client("sns", region_name = awsregion)

        rds = boto3.client("rds", region_name = awsregion)
        rdsresponse = rds.describe_db_instances(
            DBInstanceIdentifier=dbinstance
        )
        
        subj = "Application " + application + ": restore of the database instance " + dbinstance + " [COMPLETED]"
        msg = "The restore of the database instance " + dbinstance + " has completed. \r ** Here the details about the restore: \r _Service: " + dbservice + "\r _Application: " + application + "\r _Environment: " + environment + "\r _Source: " + source + "\r _DBInstance: " + dbinstance + "\r _RestoreType: " + restoretype + "\r **Here the details about the database instance: \r" + str(rdsresponse["DBInstances"])
        
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