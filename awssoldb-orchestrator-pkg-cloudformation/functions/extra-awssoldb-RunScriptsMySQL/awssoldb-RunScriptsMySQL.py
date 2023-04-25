import boto3
import json
import logging
import pymysql
from pymysql.err import ProgrammingError
from pymysql.err import DataError
from pymysql.err import IntegrityError
from pymysql.err import NotSupportedError
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def VerifyTags(rdsclient, arn):
    response = rdsclient.list_tags_for_resource(
        ResourceName=arn
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
    
    
def GetConnection(access, data, temppwd, method, engine):
    if access == "pwd":
        try:
            if engine == "mysql" or engine == "mariadb":
                host = data['DBInstances'][0]['Endpoint']['Address']
                username = data['DBInstances'][0]['MasterUsername']
                password = temppwd
                port = data['DBInstances'][0]['Endpoint']['Port']
                dbname = data['DBInstances'][0]['DBName']
            elif engine == "aurora-mysql":
                host = data['DBClusters'][0]['Endpoint']
                username = data['DBClusters'][0]['MasterUsername']
                password = temppwd
                port = data['DBClusters'][0]['Port']
                dbname = data['DBClusters'][0]['DatabaseName']

            if method == "lambda":
                conn = pymysql.connect(host, user=username, passwd=password, port=port, db=dbname, connect_timeout=5)
            elif method == "ec2":
                conn = "/bin/mysql -h " + host + " -P " + str(port) + " -u " + username + " -Db " + dbname + " -p$MYTMP"
            else:
                return None
            
            return conn
        except pymysql.OperationalError:
            return None
    elif access == "secret":
        try:
            host = data['host']
            username = data['username']
            password = data['password']
            port = int(data['port'])
            dbname = data['dbname']
            
            if method == "lambda":
                conn = pymysql.connect(host, user=username, passwd=password, port=port, db=dbname, connect_timeout=5)
            elif method == "ec2":
                conn = "/bin/mysql -h " + host + " -P " + str(port) + " -u " + username + " -Db " + dbname + " -p$MYTMP"
            else:
                return None
            return conn
        except pymysql.OperationalError:
            return None
    else:
        return None


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
            
            if VerifyTags(rdsclient, dbarn):
                engine = event['engine']
        
                if engine == "mysql" or engine == "mariadb":
                    method = event["method"]
                    access = event['access']
                    
                    if method == "lambda":
                        if access == "pwd":
                            data = response
                            temppwd = event['temppwd']
                        elif access == "secret":
                            temppwd = ""
                            secretname = event['secretname']
                            secclient = boto3.client('secretsmanager', region_name=awsregion)
                            
                            response = secclient.get_secret_value(
                                SecretId=secretname,
                            )
                            
                            secretstring = str(response['SecretString'])
                            obj = json.loads(secretstring)
                            data = obj
                        
                        conn = GetConnection(access, data, temppwd, method, engine)
                        
                        if conn:
                            logger.info("Connection opened")
                            
                            s3client = boto3.client('s3', region_name=awsregion)
                            bucketname = event['bucketname']
                            prefix = event['prefix']
                            keytemp = prefix + "/script_in_progress.txt"
                            
                            response = s3client.put_object(
                                Body=b'Lambda function RunScripts in progress',
                                Key=keytemp,
                                Bucket=bucketname
                            )
                            
                            logger.info("Temp S3 object created")
                            
                            try:
                                keys = event['keys'].split(",")

                                for key in keys:
                                    keycomplete = prefix + "/" + key
                                    logger.info(keycomplete)
                                    
                                    response = s3client.get_object(
                                        Bucket=bucketname,
                                        Key=keycomplete
                                    )
                                    
                                    logger.info("File opened")
                                    content = response['Body'].read().decode('utf-8')
    
                                    with conn.cursor() as cur:
                                        for cmd in content.splitlines():
                                            if (cmd != "") and (cmd[:1] != "#"):
                                                cur.execute(cmd)
                                                logger.info(cmd)
                                        conn.commit()
                                        logger.info("Commit")
                                    logger.info("File closed")
                            except ProgrammingError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a ProgrammingError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a ProgrammingError")
                            except DataError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a DataError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a DataError")
                            except IntegrityError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a IntegrityError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a IntegrityError")
                            except NotSupportedError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a NotSupportedError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a NotSupportedError")
                            except:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with errors. Unknow error")
                                raise ValueError("Scripts run with errors. Unknow error")
                            finally:
                                logger.info("Connection closed")
                                conn.close()
                                
                            response = s3client.delete_object(
                                Bucket=bucketname,
                                Key=keytemp
                            )
                            
                            logger.info("Temp S3 object removed")
                                
                            result = "Scripts run"
                        else:
                            logger.info("Unable to log into the MySQL database, scripts not run")
                            raise ValueError("Unable to log into the MySQL database, scripts not run")
                    elif method == "ec2":
                        if access == "pwd":
                            data = response
                            temppwd = event['temppwd']
                        elif access == "secret":
                            temppwd = ""
                            secretname = event['secretname']
                            secclient = boto3.client('secretsmanager', region_name=awsregion)
                            
                            response = secclient.get_secret_value(
                                SecretId=secretname,
                            )
                            
                            secretstring = str(response['SecretString'])
                            obj = json.loads(secretstring)
                            data = obj
                        
                        conn = GetConnection(access, data, temppwd, method, engine)

                        ec2client = boto3.client('ec2', region_name=awsregion)
                        ec2response = ec2client.describe_instances(
                                Filters=[
                                    {
                                        'Name': 'tag:Name',
                                        'Values': [
                                            'DbRestore'
                                        ]
                                    },
                                ]
                            )
        
                        ec2InstanceId = ec2response['Reservations'][0]['Instances'][0]['InstanceId']
                        
                        s3client = boto3.client('s3', region_name=awsregion)
                        bucketname = event['bucketname']
                        prefix = event['prefix']
                        keytemp = prefix + "/script_in_progress.txt"
                        
                        response = s3client.put_object(
                            Body=b'Lambda function RunScripts in progress',
                            Key=keytemp,
                            Bucket=bucketname
                        )
                        
                        logger.info("Temp S3 object created")
                        
                        ssmclient = boto3.client('ssm', region_name=awsregion)
                        
                        keys = event['keys'].split(",")
                        for key in keys:
                            command = "/bin/aws s3 cp s3://" + bucketname + "/" + prefix + "/" + key + " ."
                            logger.info(command)
                            response = ssmclient.send_command(
                                InstanceIds=[ ec2InstanceId ],
                                DocumentName='AWS-RunShellScript',
                                TimeoutSeconds=60,
                                Parameters={
                                    "commands": [
                                        command
                                    ]
                                }
                            )
                            
                            cmdId = response['Command']['CommandId']
                            final_status = "Not Started"
                            
                            while final_status not in ('Success','Delivery Timed Out','Execution Timed Out','Failed','Canceled','Undeliverable','Terminated'):
                                try:
                                    temp_status = ssmclient.get_command_invocation(
                                        CommandId=cmdId,
                                        InstanceId=ec2InstanceId
                                    )
                                    final_status = temp_status['Status']
                                except:
                                    #CmdId not available yet
                                    None

                            if final_status == "Success":
                                logger.info("Command executed successfully")
                            else:
                                logger.info("Command NOT executed successfully")

                        if access == "pwd":
                            precommand = "export MYTMP='" + temppwd + "'"
                        elif access == "secret":
                            precommand = "export MYTMP='" + data['password'] + "'"

                        for key in keys:
                            command = conn + " < " + key
                            postcommand = "rm " + key
                            
                            logger.info(command)
                            response = ssmclient.send_command(
                                InstanceIds=[ ec2InstanceId ],
                                DocumentName='AWS-RunShellScript',
                                TimeoutSeconds=60,
                                Parameters={
                                    "commands": [
                                        precommand,
                                        command,
                                        postcommand
                                    ]
                                }
                            )
                            
                            cmdId = response['Command']['CommandId']
                            logger.info(cmdId)
                            final_status = "Not Started"
                            
                            while final_status not in ('Success','Delivery Timed Out','Execution Timed Out','Failed','Canceled','Undeliverable','Terminated'):
                                try:
                                    temp_status = ssmclient.get_command_invocation(
                                        CommandId=cmdId,
                                        InstanceId=ec2InstanceId
                                    )
                                    final_status = temp_status['Status']
                                except:
                                    #CmdId not available yet
                                    None

                            if final_status == "Success":
                                logger.info("Command executed successfully")
                            else:
                                logger.info("Command NOT executed successfully")
                        
                        response = s3client.delete_object(
                            Bucket=bucketname,
                            Key=keytemp
                        )
                        
                        logger.info("Temp S3 object removed")
                        logger.info("Scripts run through Lambda")

                        result = "Scripts run through Lambda"
                    else:
                        result = "Method not supported. Valid values are 'lambda' or 'ec2'"
                elif engine == "postgresql":
                    result = "Action not supported yet by the engine specified [postgresql]"
                elif engine == "oracle":
                    result = "Action not supported yet by the engine specified [oracle]"
                elif engine == "sqlserver":
                    result = "Action not supported yet by the engine specified [sqlserver]"
            else:
                raise ValueError("Action not permitted. Tag 'refresh' missing or invalid")
        elif dbservice == 'aurora':
            cluster = event['cluster']

            response = rdsclient.describe_db_clusters(
                DBClusterIdentifier=cluster
            )
            
            cluarn = response['DBClusters'][0]['DBClusterArn']
            
            if VerifyTags(rdsclient, cluarn):
                engine = event['engine']
        
                if engine == "aurora-mysql":
                    method = event["method"]
                    access = event['access']
                    
                    if method == "lambda":
                        if access == "pwd":
                            data = response
                            temppwd = event['temppwd']
                        elif access == "secret":
                            temppwd = ""
                            secretname = event['secretname']
                            secclient = boto3.client('secretsmanager', region_name=awsregion)
                            
                            response = secclient.get_secret_value(
                                SecretId=secretname,
                            )
                            
                            secretstring = str(response['SecretString'])
                            obj = json.loads(secretstring)
                            data = obj
                        
                        conn = GetConnection(access, data, temppwd, method, engine)
                        
                        if conn:
                            logger.info("Connection opened")
                            
                            s3client = boto3.client('s3', region_name=awsregion)
                            bucketname = event['bucketname']
                            prefix = event['prefix']
                            keytemp = prefix + "/script_in_progress.txt"
                            
                            response = s3client.put_object(
                                Body=b'Lambda function RunScripts in progress',
                                Key=keytemp,
                                Bucket=bucketname
                            )
                            
                            logger.info("Temp S3 object created")
                            
                            try:
                                keys = event['keys'].split(",")

                                for key in keys:
                                    keycomplete = prefix + "/" + key
                                    logger.info(keycomplete)
                                    
                                    response = s3client.get_object(
                                        Bucket=bucketname,
                                        Key=keycomplete
                                    )
                                    
                                    logger.info("File opened")
                                    content = response['Body'].read().decode('utf-8')
    
                                    with conn.cursor() as cur:
                                        for cmd in content.splitlines():
                                            if (cmd != "") and (cmd[:1] != "#"):
                                                cur.execute(cmd)
                                                logger.info(cmd)
                                        conn.commit()
                                        logger.info("Commit")
                                    logger.info("File closed")
                            except ProgrammingError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a ProgrammingError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a ProgrammingError")
                            except DataError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a DataError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a DataError")
                            except IntegrityError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a IntegrityError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a IntegrityError")
                            except NotSupportedError as err:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with a NotSupportedError")
                                logger.info(err.args[0])
                                logger.info(err.args[1])
                                raise ValueError("Scripts run with a NotSupportedError")
                            except:
                                response = s3client.delete_object(
                                    Bucket=bucketname,
                                    Key=keytemp
                                )
                                logger.info("Scripts run with errors. Unknow error")
                                raise ValueError("Scripts run with errors. Unknow error")
                            finally:
                                logger.info("Connection closed")
                                conn.close()
                                
                            response = s3client.delete_object(
                                Bucket=bucketname,
                                Key=keytemp
                            )
                            
                            logger.info("Temp S3 object removed")
                                
                            result = "Scripts run"
                        else:
                            logger.info("Unable to log into the Aurora MySQL database, scripts not run")
                            raise ValueError("Unable to log into the Aurora MySQL database, scripts not run")
                    elif method == "ec2":
                        if access == "pwd":
                            data = response
                            temppwd = event['temppwd']
                        elif access == "secret":
                            temppwd = ""
                            secretname = event['secretname']
                            secclient = boto3.client('secretsmanager', region_name=awsregion)
                            
                            response = secclient.get_secret_value(
                                SecretId=secretname,
                            )
                            
                            secretstring = str(response['SecretString'])
                            obj = json.loads(secretstring)
                            data = obj
                        
                        conn = GetConnection(access, data, temppwd, method, engine)

                        ec2client = boto3.client('ec2', region_name=awsregion)
                        ec2response = ec2client.describe_instances(
                                Filters=[
                                    {
                                        'Name': 'tag:Name',
                                        'Values': [
                                            'DbRestore'
                                        ]
                                    },
                                ]
                            )
        
                        ec2InstanceId = ec2response['Reservations'][0]['Instances'][0]['InstanceId']
                        
                        s3client = boto3.client('s3', region_name=awsregion)
                        bucketname = event['bucketname']
                        prefix = event['prefix']
                        keytemp = prefix + "/script_in_progress.txt"
                        
                        response = s3client.put_object(
                            Body=b'Lambda function RunScripts in progress',
                            Key=keytemp,
                            Bucket=bucketname
                        )
                        
                        logger.info("Temp S3 object created")
                        
                        ssmclient = boto3.client('ssm', region_name=awsregion)
                        
                        keys = event['keys'].split(",")
                        for key in keys:
                            command = "/bin/aws s3 cp s3://" + bucketname + "/" + prefix + "/" + key + " ."
                            logger.info(command)
                            response = ssmclient.send_command(
                                InstanceIds=[ ec2InstanceId ],
                                DocumentName='AWS-RunShellScript',
                                TimeoutSeconds=60,
                                Parameters={
                                    "commands": [
                                        command
                                    ]
                                }
                            )
                            
                            cmdId = response['Command']['CommandId']
                            final_status = "Not Started"
                            
                            while final_status not in ('Success','Delivery Timed Out','Execution Timed Out','Failed','Canceled','Undeliverable','Terminated'):
                                try:
                                    temp_status = ssmclient.get_command_invocation(
                                        CommandId=cmdId,
                                        InstanceId=ec2InstanceId
                                    )
                                    final_status = temp_status['Status']
                                except:
                                    #CmdId not available yet
                                    None

                            if final_status == "Success":
                                logger.info("Command executed successfully")
                            else:
                                logger.info("Command NOT executed successfully")

                        if access == "pwd":
                            precommand = "export MYTMP='" + temppwd + "'"
                        elif access == "secret":
                            precommand = "export MYTMP='" + data['password'] + "'"

                        for key in keys:
                            command = conn + " < " + key
                            postcommand = "rm " + key
                            
                            logger.info(command)
                            response = ssmclient.send_command(
                                InstanceIds=[ ec2InstanceId ],
                                DocumentName='AWS-RunShellScript',
                                TimeoutSeconds=60,
                                Parameters={
                                    "commands": [
                                        precommand,
                                        command,
                                        postcommand
                                    ]
                                }
                            )
                            
                            cmdId = response['Command']['CommandId']
                            logger.info(cmdId)
                            final_status = "Not Started"
                            
                            while final_status not in ('Success','Delivery Timed Out','Execution Timed Out','Failed','Canceled','Undeliverable','Terminated'):
                                try:
                                    temp_status = ssmclient.get_command_invocation(
                                        CommandId=cmdId,
                                        InstanceId=ec2InstanceId
                                    )
                                    final_status = temp_status['Status']
                                except:
                                    #CmdId not available yet
                                    None

                            if final_status == "Success":
                                logger.info("Command executed successfully")
                            else:
                                logger.info("Command NOT executed successfully")
                        
                        response = s3client.delete_object(
                            Bucket=bucketname,
                            Key=keytemp
                        )
                        
                        logger.info("Temp S3 object removed")
                        logger.info("Scripts run through Ec2")

                        result = "Scripts run through Ec2"
                    else:
                        result = "Method not supported. Valid values are 'lambda' or 'ec2'"
                elif engine == "aurora-postgresql":
                    result = "Action not supported yet by the engine specified [aurora-postgresql]"
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