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
        check = False

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
            masterusr = response['DBInstances'][0]['MasterUsername']
            engine = response['DBInstances'][0]['Engine']
            host = response['DBInstances'][0]['Endpoint']['Address']
            port = response['DBInstances'][0]['Endpoint']['Port']
            dbname = response['DBInstances'][0]['DBName']
            dbInstanceIdentifier = response['DBInstances'][0]['DBInstanceIdentifier']

            if VerifyTags(rdsclient, dbarn):
                temppwd = event['temppwd']

                response = rdsclient.modify_db_instance(
                    DBInstanceIdentifier=dbinstance,
                    MasterUserPassword=temppwd,
                    ApplyImmediately=True
                )

                logger.info("Master password changed")

                secret = event['secret']

                if secret == "true":
                    secretname = event['secretname']
                    secclient = boto3.client(
                        'secretsmanager', region_name=awsregion)

                    response = secclient.get_secret_value(
                        SecretId=secretname,
                    )

                    secretstring = str(response['SecretString'])
                    obj = json.loads(secretstring)

                    obj['password'] = temppwd
                    obj['username'] = masterusr
                    obj['engine'] = engine
                    obj['host'] = host
                    obj['port'] = port
                    obj['dbname'] = dbname
                    obj['dbInstanceIdentifier'] = dbInstanceIdentifier

                    objstr = json.dumps(obj)

                    response = secclient.update_secret(
                        SecretId=secretname,
                        SecretString=objstr
                    )

                    logger.info("Secret modified")
                    result = "Master password changed and secret modified"
                else:
                    result = "Master password changed"
            else:
                raise ValueError(
                    "Action not permitted. Tag 'refresh' missing or invalid")

        elif dbservice == 'aurora':
            cluster = event['cluster']

            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )

            cluarn = response['DBClusters'][0]['DBClusterArn']
            masterusr = response['DBClusters'][0]['MasterUsername']
            engine = response['DBClusters'][0]['Engine']
            host = response['DBClusters'][0]['Endpoint']
            port = response['DBClusters'][0]['Port']
            # dbname = response['DBClusters'][0]['DatabaseName']
            dbClusterIdentifier = response['DBClusters'][0]['DBClusterIdentifier']

            if VerifyTags(rdsclient, cluarn):
                temppwd = event['temppwd']

                response = rdsclient.modify_db_cluster(
                    DBClusterIdentifier=cluster,
                    MasterUserPassword=temppwd,
                    ApplyImmediately=True
                )

                logger.info("Master password changed")

                secret = event['secret']

                if secret == "true":
                    secclient = boto3.client(
                        'secretsmanager', region_name=awsregion)
                    secretname = event['secretname']

                    response = secclient.get_secret_value(
                        SecretId=secretname,
                    )

                    secretstring = str(response['SecretString'])
                    obj = json.loads(secretstring)

                    obj['password'] = temppwd
                    obj['username'] = masterusr
                    obj['engine'] = engine
                    obj['host'] = host
                    obj['port'] = port
                    obj['dbname'] = dbname
                    obj['dbClusterIdentifier'] = dbClusterIdentifier

                    objstr = json.dumps(obj)

                    response = secclient.update_secret(
                        SecretId=secretname,
                        SecretString=objstr
                    )

                    logger.info("Secret modified")
                    result = "Master password changed and secret modified"
                else:
                    result = "Master password changed"
            else:
                raise ValueError(
                    "Action not permitted. Tag 'refresh' missing or invalid")
        else:
            raise ValueError(
                "Database service specified unknown or not supported by this function")

        return {
            "statusCode": 200,
            "body": result
        }

    else:
        result = "Change master password skipped"

        return {
            "statusCode": 200,
            "body": result
        }
