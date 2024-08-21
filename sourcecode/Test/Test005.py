import boto3
import json


bedrock = boto3.client('bedrock-runtime',region_name='us-east-1')


prompt = """
Human: What is the capital of France?
Assistant: The capital of France is Paris.
"""

kwargs = {
  "modelId": "anthropic.claude-v2:1",
  "contentType": "application/json",
  "accept": "*/*",
  "body": json.dumps("{\"prompt\":\"\\n\\nHuman: Hello world\\n\\nAssistant:\",\"max_tokens_to_sample\":300,\"temperature\":0.5,\"top_k\":250,\"top_p\":1,\"stop_sequences\":[\"\\n\\nHuman:\"],\"anthropic_version\":\"bedrock-2023-05-31\"}")
}

response = bedrock.invoke_model(**kwargs)

body = json.loads(response.get('body').read())

print(body)