import os
import json
import boto3


AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
MODEL_ID = os.environ.get('MODEL_ID', 'anthropic.claude-v2:1')

bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)

def lambda_handler(event, context):
    product_data = {
        "product_name": "CarryBag",
        "current_price": 129.99
    }

    prompt = f"""
        Given the following data for a Winter Parka jacket, suggest an optimal price:
        
        Product Name: {product_data['product_name']}
        Current Price: ${product_data['current_price']}
        
        Consider factors such as profit margin, competitive pricing, demand, and seasonality. 
        Provide a suggested price and a brief explanation for the recommendation.
        
        Return your response in the following JSON format:
            {{
                "suggested_price": float       
            }}
    """

    response = invoke_model(prompt)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def invoke_model(prompt):
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 500,
        "temperature": 0.5,
        "top_p": 0.9,
    })

    try:
        response = bedrock.invoke_model(
            body=body,
            modelId="anthropic.claude-v2:1",
            contentType="application/json",
            accept="*/*",
        )
        response_body = json.loads(response['Body'].read())
        return response_body.get('completion')
    except Exception as e:
        print(f"Error invoking model: {e}")
        return {"error": str(e)}
