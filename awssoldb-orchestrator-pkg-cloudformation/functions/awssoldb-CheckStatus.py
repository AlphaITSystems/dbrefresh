import boto3
import json
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def CheckDeleteReplicas(rdsclient, event):

    dbservice = event['dbservice']

    if dbservice == 'rds':
        dbinstance = event['dbinstance']

        try:
            response = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )

            logger.info("List of the replicas verified")
            replicas = response['DBInstances'][0]['ReadReplicaDBInstanceIdentifiers']

            if len(replicas) == 0:
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'
        except:
            logger.info("Status of the instance verified")
            result = 'SUCCEEDED'

    elif dbservice == 'aurora':
        cluster = event['cluster']

        try:
            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )

            logger.info("List of the replicas verified")
            replicas = response['DBClusters'][0]['DBClusterMembers']

            if len(replicas) == 1:
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'

        except:
            logger.info("Status of the instance verified")
            result = 'SUCCEEDED'
    else:
        logger.info("Service not supported by this function")
        result = 'FAILED'

    logger.info(result)
    return result


def CheckStopDb(rdsclient, event):

    dbservice = event['dbservice']
    dbinstance = event['dbinstance']

    if dbservice == 'rds':
        try:
            response = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )

            logger.info("Status of the instance verified")
            dbstatus = response['DBInstances'][0]['DBInstanceStatus']
            logger.info(dbstatus)

            if dbstatus == 'stopped':
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'
        except:
            logger.info("Status of the instance verified")
            result = 'SUCCEEDED'

    elif dbservice == 'aurora':
        result = 'SUCCEEDED'

    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    logger.info(result)
    return result


def CheckStopCluster(rdsclient, event):

    dbservice = event['dbservice']
    cluster = event['cluster']

    if dbservice == 'rds':
        result = 'SUCCEEDED'

    elif dbservice == 'aurora':
        try:
            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )

            logger.info("Status of the cluster verified")
            clusterstatus = response['DBClusters'][0]['Status']
            logger.info(clusterstatus)

            if clusterstatus == 'stopped':
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'
        except:
            logger.info("Status of the cluster verified")
            result = 'SUCCEEDED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    logger.info(result)
    return result


def CheckRestore(rdsclient, event):
    dbservice = event['dbservice']

    if dbservice == 'rds':
        dbinstance = event['dbinstance']

        response = rdsclient.describe_db_instances(
            DBInstanceIdentifier=dbinstance
        )

        logger.info("Status of the instance verified")

        dbstatus = response['DBInstances'][0]['DBInstanceStatus']

        if dbstatus == 'available':
            result = 'SUCCEEDED'
        else:
            result = 'FAILED'

    elif dbservice == 'aurora':
        cluster = event['cluster']

        response = rdsclient.describe_db_clusters(
            DBClusterIdentifier=cluster
        )

        logger.info("Status of the cluster verified")

        clusterstatus = response['DBClusters'][0]['Status']

        if clusterstatus == 'available':
            result = 'SUCCEEDED'
        else:
            result = 'FAILED'

    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def CheckDelete(rdsclient, event):

    dbservice = event['dbservice']
    dbinstance = event['dbinstance']

    if dbservice == 'rds' or dbservice == 'aurora':
        try:
            response = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )

            logger.info("Instance still exists")
            result = 'FAILED'
        except:
            logger.info("Status of the instance verified")
            result = 'SUCCEEDED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def CheckDeleteCluster(rdsclient, event):

    dbservice = event['dbservice']
    cluster = event['cluster']

    if dbservice == 'aurora':
        try:
            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )

            logger.info("Cluster still exists")
            result = 'FAILED'

        except:
            logger.info("Status of the cluster verified")
            result = 'SUCCEEDED'

    else:
        logger.info("Service not supported by this function")
        result = 'FAILED'

    return result


def CheckUpdate(rdsclient, event):

    dbservice = event['dbservice']
    dbinstance = event['dbinstance']

    if dbservice == 'rds':
        response = rdsclient.describe_db_instances(
            DBInstanceIdentifier=dbinstance
        )

        logger.info("Status of the instance verified")

        dbstatus = response['DBInstances'][0]['CACertificateIdentifier']

        if dbstatus == 'rds-ca-2019':
            result = 'SUCCEEDED'
        else:
            result = 'FAILED'

    elif dbservice == 'aurora':
        result = 'SUCCEEDED'

    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def CheckRename(rdsclient, event):

    dbservice = event['dbservice']
    dbinstance = event['dbinstance']

    if dbservice == 'rds' or dbservice == 'aurora':
        try:
            response = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )

            logger.info("Name of the instance verified")

            dbstatus = response['DBInstances'][0]['DBInstanceStatus']

            if dbstatus == 'available':
                response2 = rdsclient.describe_db_instances(
                    DBInstanceIdentifier=dbinstance
                )

                logger.info("Status of the instance verified")

                dbstatus2 = response2['DBInstances'][0]['DBInstanceStatus']

                if dbstatus2 == 'available':
                    result = 'SUCCEEDED'
                else:
                    result = 'FAILED'
            else:
                result = 'FAILED'

        except:
            logger.info("Instance not renamed yet")
            result = 'FAILED'
    else:
        logger.info("Service not supported by this function ")
        result = 'FAILED'

    return result


def CheckRenameCluster(rdsclient, event):

    logger.info("CheckRenameCluster started")

    dbservice = event['dbservice']
    cluster = event['cluster']

    if dbservice == 'aurora':
        try:
            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )

            logger.info("Name of the cluster verified")

            clusterstatus = response['DBClusters'][0]['Status']
            logger.info(clusterstatus)

            if clusterstatus == 'available':
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'

        except:
            logger.info("Cluster not renamed yet")
            result = 'FAILED'
    else:
        logger.info("Service not supported by this function")
        result = 'FAILED'

    return result


def CheckFixTags(rdsclient, event):

    dbservice = event['dbservice']
    dbinstance = event['dbinstance']
    dbarn = event['dbarn']

    if dbservice == 'rds':
        response = rdsclient.list_tags_for_resource(
            ResourceName=dbarn
        )

        logger.info("Tag verified")

        for x in response['TagList']:
            if x['Key'] == "refresh-instance":
                tagValue = x['Value']

        if tagValue == dbinstance:
            response2 = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )

            logger.info("Status of the instance verified")

            dbstatus = response2['DBInstances'][0]['DBInstanceStatus']

            if dbstatus == 'available':
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'
        else:
            result = 'FAILED'

    elif dbservice == 'aurora':
        cluster = event['cluster']
        cluarn = event['cluarn']

        response_clu = rdsclient.list_tags_for_resource(
            ResourceName=cluarn
        )

        response_db = rdsclient.list_tags_for_resource(
            ResourceName=dbarn
        )

        logger.info("Tag verified")

        for x in response_clu['TagList']:
            if x['Key'] == "refresh-cluster":
                tagValue_clu = x['Value']

        for x in response_db['TagList']:
            if x['Key'] == "refresh-instance":
                tagValue_db = x['Value']

        if tagValue_clu == cluster and tagValue_db == dbinstance:
            response_clu_status = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )

            response_db_status = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )

            logger.info("Status of the cluster and of the instance verified")

            clustatus = response_clu_status['DBClusters'][0]['Status']
            dbstatus = response_db_status['DBInstances'][0]['DBInstanceStatus']

            if clustatus == 'available' and dbstatus == 'available':
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'
        else:
            result = 'FAILED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def CheckReplicas(rdsclient, event):
    dbservice = event['dbservice']

    if dbservice == 'rds' or dbservice == 'aurora':
        replicas = event['replicas'].split(",")
        for replica in replicas:
            print(replica)

            try:
                response = rdsclient.describe_db_instances(
                    DBInstanceIdentifier=replica
                )

                logger.info("Status of the replica verified")

                dbstatus = response['DBInstances'][0]['DBInstanceStatus']

                if dbstatus == 'available':
                    result = 'SUCCEEDED'
                else:
                    result = 'FAILED'
            except:
                logger.info(
                    "Status of the replica not verified. Check the replica identifier you specified")
                result = 'FAILED'
    else:
        logger.info("Service not supported by this function")
        result = 'FAILED'

    return result


def CheckCreate(rdsclient, event):

    dbservice = event['dbservice']
    dbinstance = event['dbinstance']

    if dbservice == 'rds':
        result = 'SUCCEEDED'

    elif dbservice == 'aurora':
        try:
            response = rdsclient.describe_db_instances(
                DBInstanceIdentifier=dbinstance
            )

            logger.info("Status of the instance verified")
            dbstatus = response['DBInstances'][0]['DBInstanceStatus']
            logger.info(dbstatus)

            if dbstatus == 'available':
                result = 'SUCCEEDED'
            else:
                result = 'FAILED'
        except:
            result = 'FAILED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    logger.info(result)
    return result


def CheckPwd(rdsclient, event):

    dbservice = event['dbservice']

    if dbservice == 'rds':
        dbinstance = event['dbinstance']

        response = rdsclient.describe_db_instances(
            DBInstanceIdentifier=dbinstance
        )

        logger.info("Status of the instance verified")

        dbstatus = response['DBInstances'][0]['DBInstanceStatus']

        if dbstatus == 'available':
            result = 'SUCCEEDED'
        else:
            result = 'FAILED'
    elif dbservice == 'aurora':
        cluster = event['cluster']

        response = rdsclient.describe_db_clusters(
            DBClusterIdentifier=cluster
        )

        logger.info("Status of the cluster verified")

        clusterstatus = response['DBClusters'][0]['Status']

        if clusterstatus == 'available':
            result = 'SUCCEEDED'
        else:
            result = 'FAILED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def CheckRotatePwd(secclient, event):

    dbservice = event['dbservice']

    if dbservice == 'rds' or dbservice == 'aurora':
        secretname = event['secretname']
        temppwd = event['temppwd']

        response = secclient.get_secret_value(
            SecretId=secretname,
        )

        secretstring = str(response['SecretString'])
        obj = json.loads(secretstring)

        if obj['password'] != temppwd:
            result = 'SUCCEEDED'
        else:
            result = 'FAILED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def CheckRunScripts(s3client, event):

    dbservice = event['dbservice']

    if dbservice == 'rds' or dbservice == 'aurora':
        bucketname = event['bucketname']
        prefix = event['prefix']
        keytemp = prefix + '/script_in_progress.txt'

        try:
            response = s3client.get_object(
                Bucket=bucketname,
                Key=keytemp
            )

            logger.info("Temporary S3 object still exists")
            result = 'FAILED'
        except:
            logger.info("Temporary S3 object deleted")
            result = 'SUCCEEDED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def CheckCreateSecret(secclient, event):

    dbservice = event['dbservice']

    if dbservice == 'rds' or dbservice == 'aurora':
        secretname = event['secretname']

        try:
            response = secclient.describe_secret(
                SecretId=secretname,
            )

            logger.info("Existence of the secret verified")

            rotation = event['rotation']

            if rotation == "true":
                checkrotation = response['RotationEnabled']

                if rotation == checkrotation:
                    result = 'SUCCEEDED'
                else:
                    result = 'FAILED'

            result = 'SUCCEEDED'
        except:
            result = 'FAILED'
    else:
        logger.info("Database service unknown")
        result = 'FAILED'

    return result


def lambda_handler(event, context):

    torun = event['torun']

    if torun == 'true':
        awsregion = os.environ['AWS_REGION']

        rdsclient = boto3.client('rds', region_name=awsregion)
        secclient = boto3.client('secretsmanager', region_name=awsregion)
        s3client = boto3.client('s3', region_name=awsregion)

        checktodo = event['checktodo']

        if checktodo == "checkdeletereplicas":
            resultcheck = CheckDeleteReplicas(rdsclient, event)
        elif checktodo == "checkstopdb":
            resultcheck = CheckStopDb(rdsclient, event)
        elif checktodo == "checkstopcluster":
            resultcheck = CheckStopCluster(rdsclient, event)
        elif checktodo == "checkrestore":
            resultcheck = CheckRestore(rdsclient, event)
        elif checktodo == "checkdelete":
            resultcheck = CheckDelete(rdsclient, event)
        elif checktodo == "checkdeletecluster":
            resultcheck = CheckDeleteCluster(rdsclient, event)
        elif checktodo == "checkupdate":
            resultcheck = CheckUpdate(rdsclient, event)
        elif checktodo == "checkrename":
            resultcheck = CheckRename(rdsclient, event)
        elif checktodo == "checkrenamecluster":
            resultcheck = CheckRenameCluster(rdsclient, event)
        elif checktodo == "checkfixtags":
            resultcheck = CheckFixTags(rdsclient, event)
        elif checktodo == "checkreplicas":
            resultcheck = CheckReplicas(rdsclient, event)
        elif checktodo == "checkcreate":
            resultcheck = CheckCreate(rdsclient, event)
        elif checktodo == "checkpwd":
            resultcheck = CheckPwd(rdsclient, event)
        elif checktodo == "rotatepwd":
            resultcheck = CheckRotatePwd(secclient, event)
        elif checktodo == "runscripts":
            resultcheck = CheckRunScripts(s3client, event)
        elif checktodo == "checkcreatesecret":
            resultcheck = CheckCreateSecret(secclient, event)
        else:
            logger.info("Invalid check requested")
            resultcheck = 'FAILED'
    else:
        logger.info("Check skipped")
        resultcheck = 'SUCCEEDED'

    logger.info("the result is " + resultcheck)
    return {
        "statusCode": 200,
        "body": resultcheck
    }
