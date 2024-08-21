import boto3
import json


bedrock = boto3.client('bedrock-runtime')

# Function to get model response
def get_model_response(prompt):
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 500,
        "temperature": 0.5,
        "top_p": 0.9,
    })
    
    response = bedrock.invoke_model(
        body=body,
        modelId="anthropic.claude-v2",  # Using Claude v2 model
        contentType="application/json"
    )
    
    response_body = json.loads(response.get('body').read())
    return response_body.get('completion')


jacket_data = {
    "product_name": "CarryBag",
    "current_price": 129.99   
}


prompt = f"""
Given the following data for a Winter Parka jacket, suggest an optimal price:

Product Name: {jacket_data['product_name']}
Current Price: ${jacket_data['current_price']}

Consider factors such as profit margin, competitive pricing, demand, and seasonality. 
Provide a suggested price and a brief explanation for the recommendation.

Return your response in the following JSON format:
    {{
        "suggested_price": float       
    }}

"""


response = get_model_response(prompt)

print("Model Suggestion:")
print(response)

