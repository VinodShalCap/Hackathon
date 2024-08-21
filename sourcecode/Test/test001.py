import boto3
import json

bedrock = boto3.client('bedrock-runtime',region_name='us-east-1')

prompt ="what is the capital city of India"

kwargs = {
  "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
  "contentType": "application/json",
  "accept": "application/json",
  "body": json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
      {
        "role": "user",
        "content": [          
          {
            "type": "text",
            "text": prompt
          }
        ]
      }
    ]
  })
}


response = bedrock.invoke_model(**kwargs)
response_body = json.loads(response.get("body").read())
message = response_body.get("content")[0].get("text")
print(message)



