def lambda_handler(event, context):
    result = "Lambda function skipped"
        
    return {
        "statusCode": 200,
        "body": result
    }