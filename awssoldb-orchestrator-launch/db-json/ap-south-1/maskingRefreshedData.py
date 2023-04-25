import csv
import pandas as pd
import pymysql
import json
import sys
import logging
from botocore.exceptions import ClientError
from sshtunnel import SSHTunnelForwarder
import boto3
Phone = 0
countGlobal = 0
Tables = ""
tableId = 0
email = ""
result = ""


TableName = ""
tunnel = SSHTunnelForwarder(
    ('ec2-13-232-158-29.ap-south-1.compute.amazonaws.com'),
    ssh_username="ec2-user",
    ssh_pkey="C:\\Users\\hp\\Desktop\\Production-ec2-key.pem",
    remote_bind_address=(
        'productiondb.czogckszbkfu.ap-south-1.rds.amazonaws.com', 3306)
)
tunnel.start()
print("****SSH Tunnel Established****")
print(tunnel.local_bind_port)
conn = pymysql.connect(
    host='127.0.0.1', user='production', password='production12345', port=tunnel.local_bind_port, local_infile=True)
cursor = conn.cursor()
cursor.execute('use Production;')
# FileNameForMapping = "TableMapping"
# dbjsondir = "./awssoldb-orchestrator-pkg-cloudformation/TableMapping/"
# dbjsonfile = dbjsondir + FileNameForMapping + ".json"
# try:
#     with open(dbjsonfile) as json_file:
#         tableId = json.load(json_file)
#         Keyset = tableId.keys()
#         print(Keyset)
#         for r in Keyset:
#             print(tableId[r])

# except ClientError as e:
#     logging.error(e)
#     sys.exit('[Error] start_execution API failed')

# FileNameForRelation = "TableRelations"
# dbjsondir = "./awssoldb-orchestrator-pkg-cloudformation/TableMapping/"
# dbjsonfileRelations = dbjsondir + FileNameForRelation + ".json"
# try:
#     with open(dbjsonfileRelations) as json_file:
#         sm_input = json.load(json_file)
#         Keyset = sm_input.keys()
#         print("************", Keyset)
#         for r in Keyset:
#             globals()['countGlobal'] = 0
#             print(sm_input[r])
#             TablesRelation = sm_input[r]["TablesRelated"]
#             globals()['Tables'] = TablesRelation.split(",")

#             for h in globals()['Tables']:
#                 cursor.execute("use "+r)
#                 cursor.execute("Select "+"Count(*)"+" from "+h)
#                 count = cursor.fetchall()
#                 if globals()['countGlobal'] == 0:
#                     globals()['countGlobal'] = count
#                 if (count > globals()['countGlobal']):
#                     globals()['countGlobal'] = count
#                 globals()['TableName'] = h
#             print("***************************", countGlobal)
#             tableforFindingId = tableId[r][globals()['TableName']]
#             cursor.execute("Select "+tableforFindingId +
#                            " from "+globals()['TableName'])
#             globals()['result'] = cursor.fetchall()
#             data = open(
#                 'D:\\database-refresh-orchestrator-for-amazon-rds-and-amazon-aurora-main\\data1.csv', 'a', newline='')
#             writer = csv.writer(data)
#             for x in range(len(result)):
#                 globals()['Phone'] = 5000000000+x
#                 globals()['email'] = "testemail"+str(x)+"@gmail.com"
#                 q = str(Phone)
#                 writer.writerow([str(result[x]).replace(
#                     "(", '').replace(")", '').replace(',', ''), q, email])

#         csvfile = open(
#             'D:\\database-refresh-orchestrator-for-amazon-rds-and-amazon-aurora-main\\data1.csv', 'r').readlines()
#         filename = 1
#         for i in range(len(csvfile)):
#                 if i % 1000 == 0:
#                     open('./awssoldb-orchestrator-pkg-cloudformation/functions/Data/'+str(filename) + '.csv',
#                         'w').writelines(csvfile[i:i+1000])
#                     filename += 1
#        data.close()
#         cursor.execute("use Customers")
#         cursor.execute(
#             'CREATE TEMPORARY TABLE temp_update_table(CustomerId bigint,Phone bigint)')
#         cursor.execute('LOAD DATA LOCAL INFILE "D:/database-refresh-orchestrator-for-amazon-rds-and-amazon-aurora-main/data1.csv" INTO TABLE temp_update_table FIELDS TERMINATED BY "," LINES TERMINATED BY "\r\n" (@col1,@col2) set CustomerId=@col1,Phone=@col2')
#         for Table in globals()['Tables']:
#             cursor.execute("UPDATE " + Table + " INNER JOIN temp_update_table ON temp_update_table.CustomerId = " +
#                            Table+"." + tableId['Customers'][globals()['TableName']]+" SET "+Table + "."+"Phone = temp_update_table.Phone;")
cursor.execute(
    'LOAD DATA LOCAL INFILE "C:/Users/hp/Desktop/customer10000.csv" INTO TABLE Customer4 FIELDS TERMINATED BY "," LINES TERMINATED BY "\r\n" IGNORE 1 LINES;')
conn.commit()
# except ClientError as e:
#     logging.error(e)
#     sys.exit('[Error] start_execution API failed')
