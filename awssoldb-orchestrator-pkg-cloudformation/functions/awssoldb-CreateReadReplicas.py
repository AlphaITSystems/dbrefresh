import boto3
import logging
import time
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def str2bool(value):
    return value.lower() in ("True",True,"False",False)
    
    
def createRep(rdsclient, application, environment, dbinstance, multiaz, iamdbauth, autominor, secgrpids, storagetype, copytagstosnap, replicaname, dbclass, port, iops, awsregion):
    #This function works only for RDS
    
    if iops == 0:
        response = rdsclient.create_db_instance_read_replica(
            DBInstanceIdentifier=replicaname,
            SourceDBInstanceIdentifier=dbinstance,
            DBInstanceClass=dbclass,
            Port=port,
            MultiAZ=multiaz,
            EnableIAMDatabaseAuthentication=iamdbauth,
            AutoMinorVersionUpgrade=autominor,
            Tags=[
                {
                    'Key': 'refresh-application',
                    'Value': application
                },
                {
                    'Key': 'refresh-environment',
                    'Value': environment
                },
                {
                    'Key': 'refresh-instance',
                    'Value': replicaname
                },
                {
                    'Key': 'refresh',
                    'Value': 'true'
                }
            ],
            VpcSecurityGroupIds=[
                secgrpids,
            ],
            StorageType=storagetype,
            CopyTagsToSnapshot=copytagstosnap,
            SourceRegion=awsregion
        )
    else:
        response = rdsclient.create_db_instance_read_replica(
            DBInstanceIdentifier=replicaname,
            SourceDBInstanceIdentifier=dbinstance,
            DBInstanceClass=dbclass,
            Port=port,
            MultiAZ=multiaz,
            EnableIAMDatabaseAuthentication=iamdbauth,
            AutoMinorVersionUpgrade=autominor,
            Tags=[
                {
                    'Key': 'refresh-application',
                    'Value': application
                },
                {
                    'Key': 'refresh-environment',
                    'Value': environment
                },
                {
                    'Key': 'refresh-instance',
                    'Value': replicaname
                },
                {
                    'Key': 'refresh',
                    'Value': 'true'
                }
            ],
            VpcSecurityGroupIds=[
                secgrpids,
            ],
            StorageType=storagetype,
            Iops=iops,
            CopyTagsToSnapshot=copytagstosnap,
            SourceRegion=awsregion
        )        
    
    result = "Creation of the read replica initiated"
    
    return result
    


def createAuroraRep(rdsclient, application, environment, cluster, subgrp, dbparamgrp, engine, autominor, copytagstosnap, replicaname, dbclass):
    #This function works only for Aurora
    response = rdsclient.create_db_instance(
        DBInstanceIdentifier=replicaname,
        DBInstanceClass=dbclass,
        Engine=engine,
        DBSubnetGroupName=subgrp,
        DBParameterGroupName=dbparamgrp,
        AutoMinorVersionUpgrade=autominor,
        PubliclyAccessible=False,
        Tags=[
            {
                'Key': 'refresh-application',
                'Value': application
            },
            {
                'Key': 'refresh-environment',
                'Value': environment
            },
            {
                'Key': 'refresh-instance',
                'Value': 'to_modify_after_rename'
            },
            {
                'Key': 'refresh',
                'Value': 'true'
            }
        ],
        DBClusterIdentifier=cluster,
        CopyTagsToSnapshot=copytagstosnap
    )
    
    result = "Creation of the read replica initiated"
    
    return result
    
    
def lambda_handler(event, context):
    
    torun = event['torun']

    if torun == "true":
        awsregion = os.environ['AWS_REGION']
        
        dbservice = event['dbservice']

        rdsclient = boto3.client('rds', region_name=awsregion)
        
        if dbservice == 'rds':
            application = event['application']
            environment = event['environment']
            dbinstance = event['dbinstance']
            multiaz = str2bool(event['multiaz'])
            iamdbauth = str2bool(event['iamdbauth'])
            autominor = str2bool(event['autominor'])
            secgrpids = event['secgrpids']
            copytagstosnap = str2bool(event['copytagstosnap'])
            storagetype = event['storagetype']

            if storagetype == "io1":
                iops = event['iops']
            else:
                iops = 0
            
            replicas  = event['replicas'].split(",")
            for replica in replicas:
                temp = replica.split("_")
                replicaname = temp[0]
                dbclass = temp[1]
                port = int(temp[2])
            
                print(replicaname)
                print(dbclass)
                print(port)
            
                createRep(rdsclient, application, environment, dbinstance, multiaz, iamdbauth, autominor, secgrpids, storagetype, copytagstosnap, replicaname, dbclass, port, iops, awsregion)
                
                result = "Creation of the replicas initiated"
                
        elif dbservice == 'aurora':
            application = event['application']
            environment = event['environment']
            cluster = event['cluster']
            subgrp = event['subgrp']
            dbparamgrp = event['dbparamgrp']
            engine = event['engine']
            autominor = str2bool(event['autominor'])
            copytagstosnap = str2bool(event['copytagstosnap'])
            dbinstance = event['dbinstance']
            
            replicas  = event['replicas'].split(",")
            for replica in replicas:
                temp = replica.split("_")
                replicaname = temp[0]
                dbclass = temp[1]
            
                print(replicaname)
                print(dbclass)
                
                createAuroraRep(rdsclient, application, environment, cluster, subgrp, dbparamgrp, engine, autominor, copytagstosnap, replicaname, dbclass)
                
                result = "Creation of the replica initiated"
        else:
            raise ValueError("Database service specified unknown or not supported by this function")

        return {
            "statusCode": 200,
            "body": result
        }
        
    else:
        result = "Instance restore skipped"
        
        return {
            "statusCode": 200,
            "body": result
        }