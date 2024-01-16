import boto3
import json
import asyncio
import random
import os
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from concurrent.futures import ProcessPoolExecutor

bedrock = boto3.client(service_name="bedrock-agent-runtime", region_name = 'us-west-2')
bedrock_rt = boto3.client(service_name="bedrock-runtime", region_name = 'us-west-2')


host = 'xxxxxx.us-west-2.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.aoss.amazonaws.com
region = 'us-west-2'
service = 'aoss'
# 确保当前 credential principal 能够访问 opensearch serverless collection
# 具体配置路径为: collection -> data access -> edit ->  添加 principals
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
)

# url = 'https://xxxxxx.us-west-2.aoss.amazonaws.com/bedrock-knowledge-base-default-index/_search'

qs = [
    "JDK 与 JRE 有什么差异",
    "JRE 与 JDK 有什么差异",
    "JDK 与 JVM 有什么差异",
    "Java 有那些特点",
    "序列话是什么",
    "今天天气如何",
    "你喜欢的食物是什么",
    " Java 是最好的语言吗？",
    "Map 跟 HashMap 有什么区别",
    " Array 跟 List 有什么区别",
    "JDK 与 JRE 有什么差异",
    "Integer 跟 int 有什么区别",
    " StringBuffer 有什么优势",
    "什么是继承",
    "什么是多态",
    "什么是泛化",
]
def get_emb(txt):
    body = json.dumps({"inputText": txt})
    modelId = "amazon.titan-embed-text-v1"  # (Change this to try different embedding models)
    accept = "application/json"
    contentType = "application/json"
    response = bedrock_rt.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    embedding = response_body.get("embedding")
    return embedding

qs_emb =[get_emb(x) for x in qs]


# https://docs.aws.amazon.com/opensearch-service/latest/developerguide/search-example.html
def inf():
    query = {
        "size": 5,
        "query": {
            "knn": {
                "bedrock-knowledge-base-default-vector": {
                    "vector": random.choice(qs_emb),
                    "k": 5
                }
            }
        }
    }
    response = client.search(
        body = query,
        index = 'bedrock-knowledge-base-default-index'
    )
    print(response)

async def inf_as(lp, executor):
    await lp.run_in_executor(executor, inf)


def main():
    MAX_CLIENTS = None
    if MAX_CLIENTS is None:
        MAX_CLIENTS = os.cpu_count()
    process_executor = ProcessPoolExecutor(max_workers = MAX_CLIENTS)
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(inf_as(loop, process_executor)) for _ in range(1)]
    results = loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()