import json
import boto3

def lambda_handler(event, context):
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )

    # Initialize S3 and Bedrock clients
    s3_client = boto3.client('s3')

    # Define S3 bucket and file details
    source_bucket = 'team-genai-innovators-common'
    source_key = 'external_data/products1.json'
    destination_bucket = 'team-genai-innovators-common'
    destination_key = 'generaged_data/output.json'

    # Read JSON file from S3
    response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
    input_data = json.loads(response['Body'].read().decode('utf-8'))
    
   

    # Define your prompt template
    prompt_template = """
        <prompt>
        \n\nHuman:Given the following data for a product, suggest an optimal price:

        Product Id: {product_id}
        Product Name: {product_name}
        Current Price: ${current_price}
        Competitor Price: ${competitor_price}

        Consider factors such as profit margin, Competitor price.
        Provide a suggested price by applying 2% discount on Competitor Price without any explanation.

        Return your response in the following plain JSON format:
            {{
                "product_id" : string,
                "suggested_price": float,
                "product_name" : string,

            }}
        \n\nAssistant:
        </prompt>
    """
    print(prompt_template.format(**input_data[0]))
    # Prepare the request payload for the model
    model_id = 'anthropic.claude-v2:1'
    payload = {
        'modelId': model_id,
        'body': json.dumps({
            'prompt': prompt_template.format(**input_data[0]),
            'max_tokens_to_sample': 300,
            'temperature': 1,
            'top_k': 250,
            'top_p': 1,
            'stop_sequences': ['\n\nHuman:'],
            'anthropic_version': 'bedrock-2023-05-31'
        }),
        'contentType': 'application/json'
    }

    response = bedrock.invoke_model(body=payload['body'], modelId=payload['modelId'], accept='*/*', contentType=payload['contentType'])
    response_body = json.loads(response['body'].read())
    
    print(response_body)

    # Write the response to the destination S3 bucket
    s3_client.put_object(Bucket=destination_bucket, Key=destination_key, Body=json.dumps(response_body))
