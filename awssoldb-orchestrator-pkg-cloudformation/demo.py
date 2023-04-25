import boto3
import json
import logging
import os
import time
import csv
import pandas as pd
import pymysql
import sys
from botocore.exceptions import ClientError
from sshtunnel import SSHTunnelForwarder
logger = logging.getLogger()
logger.setLevel(logging.INFO)
cursor = pymysql.connect.cursor
conn = pymysql.connect
Phone = 0
countGlobal = 0
Tables = ""
tableId = 0
email = ""
result = ""


def CreateDatabaseConnection(rdsclient, event):
    try:
        dbservice = event['dbservice']
        dbinstance = event['dbinstance'],
        dbendpoint = event['dbendpoint'],
        ec2endpoint = event['ec2endpoint'],
        ec2name = event['ec2name'],
        keyfilepath = event['keyfilepath'],
        dbusername = event['dbusername'],
        dbpassword = event['dbpassword'],
        localinfile = event['true'],
        tunnel = SSHTunnelForwarder(
            'ec2-3-109-55-255.ap-south-1.compute.amazonaws.com',
            ssh_username='ec2-user',
            ssh_pkey='C:\\Users\\hp\\Desktop\\Test-ec2-key.pem',
            remote_bind_address=(
                'testdbrefreshed.czogckszbkfu.ap-south-1.rds.amazonaws.com', 3306))
        tunnel.start()
        print("****SSH Tunnel Established****")
        print(tunnel.local_bind_port)
        conn = pymysql.connect(
            host='127', user=dbusername, password=str(dbpassword), port=3306, local_infile=localinfile)
        cursor = conn.cursor()
        return True
    except:
        print("database connection cannot be made")
        return False


def PerformMasking(rdsclient, event):
    FileNameForMapping = "TableMapping"
    performmasking = event['performmasking']
    if performmasking == True:
        dbjsonfile = ""
        dbinstance = event['dbinstance']
        dbjsondir = "./awssoldb-orchestrator-pkg-cloudformation/TableMapping/"
        dbjsonfile = dbjsondir + FileNameForMapping + ".json"
        try:
            with open(dbjsonfile) as json_file:
                tableId = json.load(json_file)
                Keyset = tableId.keys()
                print(Keyset)
                for r in Keyset:
                    print(tableId[r])
        except ClientError as e:
            logging.error(e)
            sys.exit('[Error] start_execution API failed')

        FileNameForRelation = "TableRelations"
        dbjsondir = "./awssoldb-orchestrator-pkg-cloudformation/TableMapping/"
        dbjsonfileRelations = dbjsondir + FileNameForRelation + ".json"
        try:
            with open(dbjsonfileRelations) as json_file:
                sm_input = json.load(json_file)
                Keyset = sm_input.keys()
                print("************", Keyset)
                for r in Keyset:
                    globals()['countGlobal'] = 0
                    print(sm_input[r])
                    TablesRelation = sm_input[r]["TablesRelated"]
                    globals()['Tables'] = TablesRelation.split(",")

                    for h in globals()['Tables']:
                        cursor.execute("use "+r)
                        cursor.execute("Select "+"Count(*)"+" from "+h)
                        count = cursor.fetchall()
                        if globals()['countGlobal'] == 0:
                            globals()['countGlobal'] = count
                        if (count > globals()['countGlobal']):
                            globals()['countGlobal'] = count
                        globals()['TableName'] = h
                    print("***************************", countGlobal)
                    tableforFindingId = tableId[r][globals()['TableName']]
                    cursor.execute("Select "+tableforFindingId +
                                   " from "+globals()['TableName'])
                    globals()['result'] = cursor.fetchall()
                    data = open(
                        'data1.csv', 'a', newline='')
                    writer = csv.writer(data)
                    for x in range(len(result)):
                        globals()['Phone'] = 5000000000+x
                        globals()['email'] = "testemail" + \
                            str(x)+"@rediffmail.com"
                        q = str(Phone)
                        writer.writerow([str(result[x]).replace(
                            "(", '').replace(")", '').replace(',', ''), q, email])
                    data.close()

                    csvfile = open(
                        'data1.csv', 'r').readlines()
                    filename = 1
                    for i in range(len(csvfile)):
                        if i % 10000 == 0:
                            open('./awssoldb-orchestrator-pkg-cloudformation/functions/Data/'+str(filename) + '.csv',
                                 'w').writelines(csvfile[i:i+10000])
                            filename += 1
                    cursor.execute("use Customers")
                    lst = os.listdir(
                        './awssoldb-orchestrator-pkg-cloudformation/functions/Data')
                    number_files = len(lst)
                    cursor.execute(
                        'CREATE TEMPORARY TABLE temp_update_table(CustomerId bigint,Phone bigint,email varchar)')
                    for x in range(number_files):
                        cursor.execute('LOAD DATA LOCAL INFILE "./awssoldb-orchestrator-pkg-cloudformation/functions/Data'+str(x)+'.csv"' +
                                       ' INTO TABLE temp_update_table FIELDS TERMINATED BY "," LINES TERMINATED BY "\r\n" (@col1,@col2,@col3) set CustomerId=@col1,Phone=@col2,email=@col3 ')

                    for Table in globals()['Tables']:
                        for x in range(number_files):
                            cursor.execute("UPDATE " + Table + " INNER JOIN temp_update_table ON temp_update_table.CustomerId = " +
                                           Table+"." + tableId['Customers'][globals()['TableName']]+" SET "+Table + "."+"Phone = temp_update_table.Phone;")
                        cursor.execute(
                            "DROP TABLE IF EXISTS temp_update_table;")
                        conn.commit
                    removeCsvFiles(True)
                    File = open('data1.csv',
                                'w')
                    File.truncate()
                    File.close()
        except ClientError as e:
            logging.error(e)
            sys.exit('[Error] start_execution API failed')

    else:
        print("Perform masking flag is set to false")

# def CheckRestore(rdsclient, event):
#     dbservice = event['dbservice']
#     if dbservice == 'rds':
#         dbinstance = event['dbinstance']
#         response = rdsclient.describe_db_instances(
#             DBInstanceIdentifier=dbinstance
#         )
#         logger.info("Status of the instance verified")
#         dbstatus = response['DBInstances'][0]['DBInstanceStatus']
#         if dbstatus == 'available':
#             result = 'SUCCEEDED'
#         else:
#             result = 'FAILED'
#     elif dbservice == 'aurora':
#         cluster = event['cluster']
#         response = rdsclient.describe_db_clusters(
#             DBClusterIdentifier=cluster
#         )
#         logger.info("Status of the cluster verified")
#         clusterstatus = response['DBClusters'][0]['Status']
#         if clusterstatus == 'available':
#             result = 'SUCCEEDED'
#         else:
#             result = 'FAILED'
#     else:
#         logger.info("Database service unknown")
#         result = 'FAILED'
#     return result


def lambda_handler(event, context):
    resultPerformMasking = False
    torun = event['torun']
    resultcheck = ""
    if torun == 'true':
        awsregion = os.environ['AWS_REGION']
        rdsclient = boto3.client('rds', region_name=awsregion)
        resultcheckflag = CreateDatabaseConnection(rdsclient, event)
        if resultcheckflag:
            try:
                PerformMasking(rdsclient, event)
                resultcheck = 'SUCCEEDED'
            except:
                print("masking not completed")
                resultcheck = 'FAILED'
        else:
            print("databaseconnection not made")
            resultcheck = 'FAILED'
    else:
        logger.info("Check skipped")
        resultcheck = 'SUCCEEDED'
    return {
        "statusCode": 200,
        "body": resultcheck
    }


def removeCsvFiles(csvFiles):
    if (csvFiles):
        lst = os.listdir(
            './awssoldb-orchestrator-pkg-cloudformation/functions/Data')
        number_files = len(lst)
        for x in range(number_files):
            os.remove(
                './awssoldb-orchestrator-pkg-cloudformation/functions/Data/'+str(x)+".csv")


def replacingNullValues():
    File = open('data1.csv', 'w')
    File.truncate()
    File.close()
    tableId = json
    FileNameForMapping = "TableMapping.json"
    dbjsonfile = ""
    dbjsondir = "./awssoldb-orchestrator-pkg-cloudformation/TableMapping/"
    dbjsonfile = dbjsondir + FileNameForMapping + ".json"
    try:
        with open(dbjsonfile) as json_file:
            tableId = json.load(json_file)
            Keyset = tableId.keys()
            print(Keyset)
            for r in Keyset:
                print(tableId[r])
    except ClientError as e:
        logging.error(e)
        sys.exit('[Error] start_execution API failed')

    FileNameForRelation = "TableRelations"
    dbjsondir = "./awssoldb-orchestrator-pkg-cloudformation/TableMapping/"
    dbjsonfileRelations = dbjsondir + FileNameForRelation + ".json"
    # cursor.execute('select int_col from table where int_col > 5000000000')
    for r in Keyset:
        globals()['countGlobal'] = 0
        with open(dbjsonfileRelations) as json_file:
            sm_input = json.load(json_file)
            print(sm_input[r])
            TablesRelation = sm_input[r]["TablesRelated"]
            globals()['Tables'] = TablesRelation.split(",")

            for h in globals()['Tables']:
                cursor.execute("use "+r)
                cursor.execute(
                    'select ' + tableId[r][h]+' from ' + h + ' where email NOT like "%rediffmail.com%"')
                datatobereplaced = cursor.fetchall()
                cursor.execute('select Phone from ' + h +
                               ' Order By Phone Desc Limit 1')
                mobile = cursor.fetchall()
                cursor.execute('select Count(Email) from ' + h)
                emailnumber = cursor.fetchall()
                data = open(
                    'data1.csv', 'a', newline='')
                writer = csv.writer(data)
                for x in range(len(datatobereplaced)):
                    globals()['Phone'] = mobile+x
                    globals()['email'] = "testemail"+emailnumber+x+"@gmail.com"
                    q = str(Phone)
                    writer.writerow([datatobereplaced[x], q, email])
                data.close()

                csvfile = open(
                    'data1.csv', 'r').readlines()
                filename = 1
                for i in range(len(csvfile)):
                    if i % 10000 == 0:
                        open('./awssoldb-orchestrator-pkg-cloudformation/functions/Data/'+str(filename) + '.csv',
                             'w').writelines(csvfile[i:i+10000])
                        filename += 1
                cursor.execute("use "+r)
                lst = os.listdir(
                    './awssoldb-orchestrator-pkg-cloudformation/functions/Data')
                number_files = len(lst)
                cursor.execute(
                    'CREATE TEMPORARY TABLE temp_update_table(CustomerId bigint,Phone bigint,email varchar)')
                for x in range(number_files):
                    cursor.execute('LOAD DATA LOCAL INFILE "./awssoldb-orchestrator-pkg-cloudformation/functions/Data'+str(x)+'.csv"' +
                                   ' INTO TABLE temp_update_table FIELDS TERMINATED BY "," LINES TERMINATED BY "\r\n" (@col1,@col2,@col3) set CustomerId=@col1,Phone=@col2,email=@col3 ')

                for Table in globals()['Tables']:
                    for x in range(number_files):
                        cursor.execute("UPDATE " + Table + " INNER JOIN temp_update_table ON temp_update_table.CustomerId = " +
                                       Table+"." + tableId['Customers'][globals()['TableName']]+" SET "+Table + "."+"Phone = temp_update_table.Phone,Email=temp_update_table.email;")
                cursor.execute(
                    "DROP TABLE IF EXISTS temp_update_table;")
                conn.commit
                removeCsvFiles(True)
                File = open('data1.csv',
                            'w')
                File.truncate()
                File.close()
