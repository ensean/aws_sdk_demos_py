import boto3
import json
from botocore.config import Config

# 设置读取超时时间 https://guide.aws.dev/articles/AR4TEI8aAsT0qtqrbfnD5NPg
config = Config(read_timeout=1000)


# claude is provided via bedrock in us-west-2, us-east-1 currently
bedrock = boto3.client(service_name="bedrock-runtime",
                       region_name='us-west-2',
                       config=config)
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
