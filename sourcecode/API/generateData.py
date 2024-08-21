
import json
import boto3
 
def lambda_handler(event,context):
 
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )
    
    # Initialize S3 and Bedrock clients
    s3_client = boto3.client('s3')
    # bedrock_client = boto3.client('bedrock')
    
    # Define S3 bucket and file details
    source_bucket = 'team-genai-innovators-common'
    source_key = 'external_data/products.json'
    destination_bucket = 'team-genai-innovators-common'
    destination_key = 'generaged_data/output.json'
    
    # Read JSON file from S3
    response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
    input_data = json.loads(response['Body'].read().decode('utf-8'))
    
    # Prepare the request payload for the model
    model_id = 'anthropic.claude-2'
    payload = {
        'modelId': model_id,
        'body': json.dumps(input_data),
        'contentType': 'application/json'
    }
    
    # for key, value in input_data.items():
    #     print(f"{key}: {value}")
        
    specific_key = 'name'
    
    for specific_key, value in input_data.items():
       print(f"Content of {specific_key}: {input_data[specific_key]}")
        
    
    
    product_data = {
        "product_id": "Prod001",
        "product_name": "CarryBag",
        "current_price": 10.00,
        "competitor_price" : 11.50
    }
    
    
    
    
    
    prompt = f"""
        Given the following data for a Winter Parka jacket, suggest an optimal price:
        
        Product Id: {product_data['product_id']}
        Product Name: {product_data['product_name']}
        Current Price: ${product_data['current_price']}
        Competitor Price: ${product_data['competitor_price']}
        
        Consider factors such as profit margin, Competitor price,. 
        Provide a suggested price by applying 2% discount on Competitor Price without any explanation.
        
        Return your response in the following JSON format:
            {{
                "product_id" : string,
                "suggested_price": float,
                "product_name" : string,
                
            }}
    """

    print (prompt)
    input = {
        "modelId": "anthropic.claude-v2:1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": json.dumps({
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 1,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"],
            "anthropic_version": "bedrock-2023-05-31"
        })
    }

    response =bedrock.invoke_model(body=input["body"],modelId=input["modelId"],accept=input["accept"],contentType=input["contentType"])

    response_body = json.loads(response['body'].read())
    
    # ----
    client_bedrock_knowledgebase = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    client_knowledgebase = client_bedrock_knowledgebase.retrieve_and_generate(
    input={
        'text': "provide 2% discount on competitor_price for proudct CarryBag001, return in json format "
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': '44KL7OSYLT',
            'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2:1'
                }
            })
            
    print("ttesttinig")
    print(client_knowledgebase)
    # -----
    
    
    
    # Write the response to the destination S3 bucket
    s3_client.put_object(Bucket=destination_bucket, Key=destination_key, Body=json.dumps(response_body))

    # print(json.dumps(input_data))
    # print("#################################")
    # print(json.dumps(input["body"]))
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print(response_body)


