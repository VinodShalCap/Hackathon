import json
import boto3
import re

def lambda_handler(event, context):
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )

    # Initialize S3 and Bedrock clients
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    client_bedrock_knowledgebase = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    
    

    # Define S3 bucket and file details
    source_bucket = 'team-genai-innovators-common'
    source_key = 'external_data/products1.json'
    destination_bucket = 'team-genai-innovators-common'
    destination_key = 'generaged_data/output.json'

    # Read JSON file from S3
    response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
    input_data = json.loads(response['Body'].read().decode('utf-8'))
    
   

    # Define your prompt template
    # prompt_template = """
    #     <prompt>
    #     \n\nHuman:Given the following data for a product, suggest an optimal price:

    #     Product Id: {Prod_ID}
    #     Product Name: {ProductName}
    #     Current Price: ${BasePrice}
       

    #     Consider factors such as profit margin, Competitor price.
    #     Provide a suggested price by applying 2% discount on Competitor Price without any explanation.

    #     Return your response in the following plain JSON format without any additional information:
    #         {{
    #             "product_id" : string,
    #             "suggested_price": float,
    #             "product_name" : string,

    #         }}
    #     \n\nAssistant:
    #     </prompt>
    # """
    
    
    # loop through products from DynamoDB
    productTable = dynamodb.Table('team-genai-innovators-cca-products')
    response = productTable.scan(
        ProjectionExpression='BasePrice, ProductName, ImageURL, Strategy, Template, Prod_ID'
    )
    products = response['Items']
    
    for product in products:
        
        prompt_template = product.pop('Template')
        print(prompt_template)
  
        # Prepare the request payload for the model
        model_id = 'anthropic.claude-v2:1'
        payload = {
            'modelId': model_id,
            'body': json.dumps({
                'prompt': f"\n\nHuman:{prompt_template.format(**product)}\n\nAssistant:",
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
        
        print(response_body,'************************')
        
       
        
        pattern = r'<prompt>(.*?)</prompt>'
        match = re.search(pattern, response_body.get("completion"), re.DOTALL)
        # print(match,'matching***********')
        
        if match:
            prompt_text = match.group(1)
            # print(prompt_text,'product')
        else:
            print("No match found.")
    
        
        # Define a regular expression pattern to match the JSON data
        pattern = r'{[\s\S]*?}'
        
        # Use re.search to find the first match
        matchJson = re.search(pattern, prompt_text)
        
        if matchJson:
            json_data = matchJson.group()
            # print(json_data,"Json Data")
        else:
            print("No JSON data found.")
        
        
        # Write the response to the destination S3 bucket
        s3_client.put_object(Bucket=destination_bucket, Key=destination_key, Body=(json_data))




