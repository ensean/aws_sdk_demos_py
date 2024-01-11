import boto3
import json
import asyncio

bedrock = boto3.client(service_name="bedrock-agent-runtime", region_name = 'us-west-2')

def inf():
    response = bedrock.retrieve(
        knowledgeBaseId='ICLSPW6BBY',
        retrievalQuery={
            'text': 'JDK 与 JRE 有什么差异'
        },
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults':  2
            }
        },
        nextToken='next'
    )
    print(response.get("retrievalResults"))

async def inf_as(lp):
    await lp.run_in_executor(None, inf)


def main():
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(inf_as(loop)) for _ in range(100000)]
    results = loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()