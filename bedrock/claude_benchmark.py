import boto3
import json
import asyncio

bedrock = boto3.client(service_name="bedrock-runtime", region_name = 'us-west-2')

def inf():
    body = json.dumps(
        {
            "prompt": "\n\nHuman:  送别友人的唐诗有哪些？\n\nAssistant:",
            "max_tokens_to_sample": 512,
        }
    )

    response = bedrock.invoke_model(body=body, modelId="anthropic.claude-v2")
    response_body = json.loads(response.get("body").read())
    print(response_body.get("completion"))

async def inf_as(lp):
    await lp.run_in_executor(None, inf)


def main():
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(inf_as(loop)) for _ in range(2000)]
    results = loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()