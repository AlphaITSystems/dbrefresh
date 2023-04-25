import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def str2bool(value):
    return value.lower() in ("True",True,"False",False)


def lambda_handler(event, context):
    torun = event['torun']
        
    if torun == "true":
        awsregion = os.environ['AWS_REGION']
        
        dbservice = event['dbservice']
        cluster = event['cluster']
        dbinstance = event['dbinstance']
        application = event['application']
        environment = event['environment']
        dbclass = event['dbclass']
        engine = event['engine']
        subgrp = event['subgrp']
        dbparamgrp = event['dbparamgrp']
        autominor = str2bool(event['autominor'])
        copytagstosnap = str2bool(event['copytagstosnap'])
        enhancedmon = str2bool(event['enhancedmon'])
        perfinsights = str2bool(event['perfinsights'])
        
        cluster = event['cluster']
        
        tempdbinstance = dbinstance + "temp"
        
        rdsclient = boto3.client('rds', region_name=awsregion)
        
        if dbservice == 'aurora':
            if enhancedmon == "True" and perfinsights == "False":
                enhancedmoninterval = event['enhancedmoninterval']
                enhancedmonrolearn = event['enhancedmonrolearn']
                
                response = rdsclient.create_db_instance(
                    DBInstanceIdentifier=tempdbinstance,
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
                    MonitoringInterval=enhancedmoninterval,
                    MonitoringRoleArn=enhancedmonrolearn,
                    CopyTagsToSnapshot=copytagstosnap
                )
            elif enhancedmon == "True" and perfinsights == "True":
                enhancedmoninterval = event['enhancedmoninterval']
                enhancedmonrolearn = event['enhancedmonrolearn']
                
                perfinsightsretention = event['perfinsightsretention']
                perfinsightskmskeyid = event['perfinsightskmskeyid']
                
                response = rdsclient.create_db_instance(
                    DBInstanceIdentifier=tempdbinstance,
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
                    MonitoringInterval=enhancedmoninterval,
                    MonitoringRoleArn=enhancedmonrolearn,
                    EnablePerformanceInsights=perfinsights,
                    PerformanceInsightsRetentionPeriod=perfinsightsretention,
                    PerformanceInsightsKMSKeyId=perfinsightskmskeyid,
                    CopyTagsToSnapshot=copytagstosnap
                )                
            elif enhancedmon == "False" and perfinsights == "True":
                perfinsightsretention = event['perfinsightsretention']
                perfinsightskmskeyid = event['perfinsightskmskeyid']

                response = rdsclient.create_db_instance(
                    DBInstanceIdentifier=tempdbinstance,
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
                    EnablePerformanceInsights=perfinsights,
                    PerformanceInsightsRetentionPeriod=perfinsightsretention,
                    PerformanceInsightsKMSKeyId=perfinsightskmskeyid,
                    CopyTagsToSnapshot=copytagstosnap
                )
            else:
                response = rdsclient.create_db_instance(
                    DBInstanceIdentifier=tempdbinstance,
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
            
            result = "Instance creation initiated"
        else:
            raise ValueError("Database service specified unknown or not supported by this function")

        return {
            "statusCode": 200,
            "body": result
        }
        
    else:
        result = "Instance creation skipped"
        
        return {
            "statusCode": 200,
            "body": result
        }