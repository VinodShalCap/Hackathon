import json
import boto3
import re

def lambda_handler(event, context):
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )

    # Initialize S3, DynamoDB, and Bedrock clients
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')

    # Define S3 bucket and file details
    destination_bucket = 'team-genai-innovators-common'
    destination_key = 'generaged_data/output.json'

    # Scan the DynamoDB table for product records
    table = dynamodb.Table('team-genai-innovators-cca-products')
    response = table.scan(
        ProjectionExpression='product_id, product_name, current_price, competitor_price, prompt_template'
    )
    products = response['Items']

    # Loop through each product record
    for product in products:
        prompt_template = product.pop('prompt_template')

        # Prepare the request payload for the model
        model_id = 'anthropic.claude-v2:1'
        payload = {
            'modelId': model_id,
            'body': json.dumps({
                'prompt': prompt_template.format(**product),
                'max_tokens_to_sample': 200,
                'temperature': 0,
                'top_k': 250,
                'top_p': 1,
                'stop_sequences': ['\n\nHuman:'],
                'anthropic_version': 'bedrock-2023-05-31'
            }),
            'contentType': 'application/json'
        }

        response1 = bedrock.invoke_model(body=payload['body'], modelId=payload['modelId'], accept='application/json', contentType=payload['contentType'])
        response_body = json.loads(response1['body'].read().decode('utf-8'))

        pattern = r'<prompt>(.*?)</prompt>'
        match = re.search(pattern, response_body.get("completion"), re.DOTALL)

        if match:
            prompt_text = match.group(1)
        else:
            print("No match found.")

        pattern = r'{[\s\S]*?}'
        matchJson = re.search(pattern, prompt_text)

        if matchJson:
            json_data = matchJson.group()
        else:
            print("No JSON data found.")

        # Write the response to the destination S3 bucket
        s3_client.put_object(Bucket=destination_bucket, Key=f"{destination_key}/{product['product_id']}.json", Body=json_data)
