import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def str2bool(value):
    return value.lower() in ("True", True, "False", False)


def lambda_handler(event, context):
    torun = event['torun']

    if torun == "true":
        awsregion = os.environ['AWS_REGION']

        dbservice = event['dbservice']
        restoretype = event['restoretype']
        application = event['application']
        environment = event['environment']
        port = event['port']
        # dbname = event['dbname']
        subgrp = event['subgrp']
        iamdbauth = str2bool(event['iamdbauth'])
        cwalogs = event['cwalogs']
        copytagstosnap = str2bool(event['copytagstosnap'])
        deletionprotection = str2bool(event['deletionprotection'])
        secgrpids = event['secgrpids']

        cwalogslist = cwalogs.split(",")

        rdsclient = boto3.client('rds', region_name=awsregion)

        if dbservice == 'rds':
            source = event['source']
            target = event['target']
            multiaz = str2bool(event['multiaz'])
            storagetype = event['storagetype']
            dbclass = event['dbclass']
            autominor = str2bool(event['autominor'])
            dbparamgrp = event['dbparamgrp']

            tempdbinstance = target

            if storagetype == "io1":
                iops = event['iops']
            else:
                iops = 0

            if restoretype == 'latestpoint':
                dbdesc = rdsclient.describe_db_instances(
                    DBInstanceIdentifier=source
                )

                latestrestorablepoint = str(
                    dbdesc['DBInstances'][0]['LatestRestorableTime'])

                if iops == 0:
                    response = rdsclient.restore_db_instance_to_point_in_time(
                        SourceDBInstanceIdentifier=source,
                        TargetDBInstanceIdentifier=tempdbinstance,
                        UseLatestRestorableTime=True,
                        DBInstanceClass=dbclass,
                        Port=int(port),
                        DBSubnetGroupName=subgrp,
                        MultiAZ=multiaz,
                        PubliclyAccessible=False,
                        AutoMinorVersionUpgrade=autominor,
                        CopyTagsToSnapshot=copytagstosnap,
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
                        StorageType=storagetype,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBParameterGroupName=dbparamgrp,
                        DeletionProtection=deletionprotection
                    )
                else:
                    response = rdsclient.restore_db_instance_to_point_in_time(
                        SourceDBInstanceIdentifier=source,
                        TargetDBInstanceIdentifier=tempdbinstance,
                        UseLatestRestorableTime=True,
                        DBInstanceClass=dbclass,
                        Port=int(port),
                        DBSubnetGroupName=subgrp,
                        MultiAZ=multiaz,
                        PubliclyAccessible=False,
                        AutoMinorVersionUpgrade=autominor,
                        CopyTagsToSnapshot=copytagstosnap,
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
                        StorageType=storagetype,
                        Iops=iops,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBParameterGroupName=dbparamgrp,
                        DeletionProtection=deletionprotection
                    )

                # logger.info("Restore to the latest restorable time initiated")
                result = "Restore to the latest restorable time initiated"

            elif restoretype == 'restorepoint':
                restoretime = event['restoretime']
                latestrestorablepoint = "null"

                if iops == 0:
                    response = rdsclient.restore_db_instance_to_point_in_time(
                        SourceDBInstanceIdentifier=source,
                        TargetDBInstanceIdentifier=tempdbinstance,
                        RestoreTime=restoretime,
                        DBInstanceClass=dbclass,
                        Port=int(port),
                        DBSubnetGroupName=subgrp,
                        MultiAZ=multiaz,
                        PubliclyAccessible=False,
                        AutoMinorVersionUpgrade=autominor,
                        CopyTagsToSnapshot=copytagstosnap,
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
                        StorageType=storagetype,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBParameterGroupName=dbparamgrp,
                        DeletionProtection=deletionprotection
                    )
                else:
                    response = rdsclient.restore_db_instance_to_point_in_time(
                        SourceDBInstanceIdentifier=source,
                        TargetDBInstanceIdentifier=tempdbinstance,
                        RestoreTime=restoretime,
                        DBInstanceClass=dbclass,
                        Port=int(port),
                        DBSubnetGroupName=subgrp,
                        MultiAZ=multiaz,
                        PubliclyAccessible=False,
                        AutoMinorVersionUpgrade=autominor,
                        CopyTagsToSnapshot=copytagstosnap,
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
                        StorageType=storagetype,
                        Iops=iops,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBParameterGroupName=dbparamgrp,
                        DeletionProtection=deletionprotection
                    )

                # logger.info("Restore to the latest restorable time initiated")
                result = "Restore to the point specified initiated"
            elif restoretype == 'fromsnapshot':
                snapshot = event['snapshot']
                latestrestorablepoint = "null"

                if iops == 0:
                    response = rdsclient.restore_db_instance_from_db_snapshot(
                        DBInstanceIdentifier=tempdbinstance,
                        DBSnapshotIdentifier=snapshot,
                        DBInstanceClass=dbclass,
                        Port=int(port),
                        DBSubnetGroupName=subgrp,
                        MultiAZ=multiaz,
                        PubliclyAccessible=False,
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
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        StorageType=storagetype,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
                        CopyTagsToSnapshot=copytagstosnap,
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBParameterGroupName=dbparamgrp,
                        DeletionProtection=False
                    )
                else:
                    response = rdsclient.restore_db_instance_from_db_snapshot(
                        DBInstanceIdentifier=tempdbinstance,
                        DBSnapshotIdentifier=snapshot,
                        DBInstanceClass=dbclass,
                        Port=int(port),
                        DBSubnetGroupName=subgrp,
                        MultiAZ=multiaz,
                        PubliclyAccessible=False,
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
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        StorageType=storagetype,
                        Iops=iops,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
                        CopyTagsToSnapshot=copytagstosnap,
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBParameterGroupName=dbparamgrp,
                        DeletionProtection=False
                    )

                # logger.info("Restore from snapshot initiated")
                result = "Restore from snapshot initiated"
            else:
                # result = "Unknown restore type"
                raise ValueError(
                    "Restore type unknown or not supported by this function")

        elif dbservice == 'aurora':
            sourcecluster = event['sourcecluster']
            targetcluster = event['targetcluster']
            cluparamgrp = event['cluparamgrp']
            engine = event['engine']

            temptargetcluster = targetcluster + "temp"

            if restoretype == 'latestpoint' or restoretype == 'fastcloning':

                if restoretype == 'latestpoint':
                    type = 'full-copy'
                else:
                    type = 'copy-on-write'

                cludesc = rdsclient.describe_db_clusters(
                    DBClusterIdentifier=sourcecluster
                )

                latestrestorablepoint = str(
                    cludesc['DBClusters'][0]['LatestRestorableTime'])

                if engine == "aurora" or engine == "aurora-mysql":
                    backtrack = event['backtrack']

                    response = rdsclient.restore_db_cluster_to_point_in_time(
                        DBClusterIdentifier=temptargetcluster,
                        RestoreType=type,
                        SourceDBClusterIdentifier=sourcecluster,
                        UseLatestRestorableTime=True,
                        Port=port,
                        DBSubnetGroupName=subgrp,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
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
                                'Key': 'refresh-cluster',
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        BacktrackWindow=backtrack,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBClusterParameterGroupName=cluparamgrp,
                        DeletionProtection=deletionprotection,
                        CopyTagsToSnapshot=copytagstosnap
                    )
                elif engine == "aurora-postgresql":

                    logger.info(type)

                    response = rdsclient.restore_db_cluster_to_point_in_time(
                        DBClusterIdentifier=temptargetcluster,
                        RestoreType=type,
                        SourceDBClusterIdentifier=sourcecluster,
                        UseLatestRestorableTime=True,
                        Port=port,
                        DBSubnetGroupName=subgrp,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
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
                                'Key': 'refresh-cluster',
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBClusterParameterGroupName=cluparamgrp,
                        DeletionProtection=deletionprotection,
                        CopyTagsToSnapshot=copytagstosnap
                    )

                result = "Cluster restore to the latest restorable time initiated"
            elif restoretype == 'restorepoint':
                restoretime = event['restoretime']
                latestrestorablepoint = "null"

                if engine == "aurora" or engine == "aurora-mysql":
                    backtrack = event['backtrack']

                    response = rdsclient.restore_db_cluster_to_point_in_time(
                        DBClusterIdentifier=temptargetcluster,
                        RestoreType='full-copy',
                        RestoreToTime=restoretime,
                        SourceDBClusterIdentifier=sourcecluster,
                        Port=port,
                        DBSubnetGroupName=subgrp,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
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
                                'Key': 'refresh-cluster',
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        BacktrackWindow=backtrack,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBClusterParameterGroupName=cluparamgrp,
                        DeletionProtection=deletionprotection,
                        CopyTagsToSnapshot=copytagstosnap
                    )
                elif engine == "aurora-postgresql":
                    response = rdsclient.restore_db_cluster_to_point_in_time(
                        DBClusterIdentifier=temptargetcluster,
                        RestoreType='full-copy',
                        RestoreToTime=restoretime,
                        SourceDBClusterIdentifier=sourcecluster,
                        Port=port,
                        DBSubnetGroupName=subgrp,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
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
                                'Key': 'refresh-cluster',
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBClusterParameterGroupName=cluparamgrp,
                        DeletionProtection=deletionprotection,
                        CopyTagsToSnapshot=copytagstosnap
                    )

                result = "Cluster restore to the point specified initiated"
            elif restoretype == 'fromsnapshot':
                snapshot = event['snapshot']
                engineversion = event['engineversion']
                latestrestorablepoint = "null"

                if engine == "aurora" or engine == "aurora-mysql":
                    backtrack = event['backtrack']

                    response = rdsclient.restore_db_cluster_from_snapshot(
                        DBClusterIdentifier=temptargetcluster,
                        SnapshotIdentifier=snapshot,
                        Engine=engine,
                        EngineVersion=engineversion,
                        Port=port,
                        DBSubnetGroupName=subgrp,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
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
                                'Key': 'refresh-cluster',
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        BacktrackWindow=backtrack,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBClusterParameterGroupName=cluparamgrp,
                        DeletionProtection=deletionprotection,
                        CopyTagsToSnapshot=copytagstosnap
                    )
                elif engine == "aurora-postgresql":
                    response = rdsclient.restore_db_cluster_from_snapshot(
                        DBClusterIdentifier=temptargetcluster,
                        SnapshotIdentifier=snapshot,
                        Engine=engine,
                        EngineVersion=engineversion,
                        Port=port,
                        DBSubnetGroupName=subgrp,
                        VpcSecurityGroupIds=[
                            secgrpids,
                        ],
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
                                'Key': 'refresh-cluster',
                                'Value': 'to_modify_after_rename'
                            },
                            {
                                'Key': 'refresh',
                                'Value': 'true'
                            }
                        ],
                        EnableIAMDatabaseAuthentication=iamdbauth,
                        EnableCloudwatchLogsExports=cwalogslist,
                        DBClusterParameterGroupName=cluparamgrp,
                        DeletionProtection=deletionprotection,
                        CopyTagsToSnapshot=copytagstosnap
                    )

                result = "Cluster restore from snapshot initiated"
            else:
                # result = "Unknown restore type"
                raise ValueError(
                    "Restore type unknown or not supported by this function")

        else:
            # latestrestorablepoint = "null"
            raise ValueError(
                "Database service specified unknown or not supported by this function")

        return {
            "statusCode": 200,
            "body": result,
            "latestrestorablepoint": latestrestorablepoint
        }

    else:
        result = "Instance restore skipped"
        latestrestorablepoint = "null"

        return {
            "statusCode": 200,
            "body": result,
            "latestrestorablepoint": latestrestorablepoint
        }
