import json

def lambda_handler(event, context):
    data = {
        'hello': 'from lambda'
    }

    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }