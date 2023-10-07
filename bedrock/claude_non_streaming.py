import boto3
import json

bedrock = boto3.client(service_name="bedrock-runtime", region_name = 'us-west-2')

body = json.dumps(
    {
        "prompt": "\n\nHuman:  送别友人的唐诗有哪些？\n\nAssistant:",
        "max_tokens_to_sample": 500,
    }
)

response = bedrock.invoke_model(body=body, modelId="anthropic.claude-v2")

response_body = json.loads(response.get("body").read())
print(response_body.get("completion"))