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
    destination_key = 'generaged_data/generatedData.json'

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
    
    # Dictionary to store all product data
    all_product_data = {}
    
    
    for product in products:
        
        prompt_template = product.pop('Template')
        
        dynamic_input = f"""
        
        Product ID: {product['Prod_ID']}
        Product Name: {product['ProductName']}
        Current Price: ${product['BasePrice']}

        Use only pricing strategy {product['Strategy']}
        Return your response should be strictly in the following JSON format:

        {{
            "Prod_ID": "<String>",
            "SellPrice" : <float>,
            "FinalPrice" : <float>,
            "Discount" : <float>
        }}
        """
        print(dynamic_input)
        
        # Use the retrieve_and_generate method
        response_knowledgebase = client_bedrock_knowledgebase.retrieve_and_generate(
            input={
                'text': dynamic_input
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': '44KL7OSYLT',
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2:1'
                }
            }
        )
        
        
        
        generated_text = response_knowledgebase['output']['text']
        print(f"Generated text for product {generated_text}")

        json_data = generated_text
        
        
        parsed_response = json.loads(generated_text)
        
        print(parsed_response,'&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            
        # Store the response in the all_product_data dictionary
        all_product_data[product['Prod_ID']] = {
            "discount": parsed_response['Discount'],
            "proposed_price": round(parsed_response['FinalPrice'], 2),
            "competator_price": 0,
        }
        
        print(all_product_data,"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        # Write the response to the destination S3 bucket
    s3_client.put_object(Bucket=destination_bucket, Key=destination_key, Body=json.dumps(all_product_data))
