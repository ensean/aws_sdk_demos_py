import boto3
import json

# claude is provided via bedrock in us-west-2, us-east-1 currently
bedrock = boto3.client(service_name="bedrock-runtime", region_name='us-west-2')
body = json.dumps(
    {
        "prompt": "\n\nHuman: Write a very short essay about space travel to Mars\n\nAssistant:",
        "max_tokens_to_sample": 200,
    }
)

response = bedrock.invoke_model_with_response_stream(
    modelId="anthropic.claude-v2", body=body
)

stream = response.get("body")

if stream:
    for event in stream:
        chunk = event.get("chunk")
        if chunk:
            print(json.loads(chunk.get("bytes").decode()))
