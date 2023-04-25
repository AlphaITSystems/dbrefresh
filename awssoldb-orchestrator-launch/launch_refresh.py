import boto3
import sys
import json
from botocore.exceptions import ClientError
import logging

if len(sys.argv) != 5:
    print('Usage: python3 launch_refresh.py <target_instance_name> <application_name> <state_machine_arn> <region>')
    print('  Example:')
    print('  python3 launch_refresh.py dbinstance1 alpha arn:aws:states:us-east-1:123456789012:stateMachine:state-machine-awssol us-east-1')
    print('')
    sys.exit('[Error] Missing or invalid parameters')
else:
    target_instance_name = sys.argv[1]
    application_name = sys.argv[2]
    state_machine_arn = sys.argv[3]
    region = sys.argv[4]

    dbjsondir = "./db-json/" + region
    dbjsonfile = dbjsondir + "/db-" + application_name + \
        "-" + target_instance_name + ".json"
    stepfunctions_client = boto3.client('stepfunctions', region_name=region)

    try:
        with open(dbjsonfile) as json_file:
            sm_input = json.load(json_file)

            response = stepfunctions_client.start_execution(
                stateMachineArn=state_machine_arn,
                input=json.dumps(sm_input)
            )

        print('[OK] Restore initiated')
    except ClientError as e:
        logging.error(e)
        sys.exit('[Error] start_execution API failed')
