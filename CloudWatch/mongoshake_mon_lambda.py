import json
import boto3
import requests
import os

"""
使用Lambda采集mongoshake增量同步信息tps、延迟（秒）
注意事项：
    - Lambda部署于VPC中，通过VPC endpoint访问CloudWatch
    - Lambda角色需要附加CloudWatch权限以写入metric数据
    - boto3初始化CloudWatch客户端时需要指定VPC endpoint url
    - 需要添加requests layer，arn可从这里查询https://github.com/keithrozario/Klayers/tree/master/deployments/python3.9
    - mongoshake url（如 http://172.18.18.18:9100/repl）通过URLS环境变量传入，多个url通过英文逗号分隔
"""

def query_repl_result(url):
    resp = requests.get(url)
    result = json.loads(resp.content)
    return result


def parse_metrics(repl_result):
    tps = repl_result.get('tps', -1)
    who = repl_result.get('who')
    now_unix = repl_result.get('now').get('unix')
    lsn_ckpt_unix = repl_result.get('lsn_ckpt').get('unix')
    lag = now_unix - lsn_ckpt_unix  # lag in seconds

    metric_data = [
        {
            'MetricName': 'tps',
            'Dimensions': [
                {
                    'Name': 'mongoshake-instance',
                    'Value': who
                },
            ],
            'Timestamp': now_unix,
            'Value': tps,
            'StorageResolution': 60
        },
        {
            'MetricName': 'lag',
            'Dimensions': [
                {
                    'Name': 'mongoshake-instance',
                    'Value': who
                },
            ],
            'Timestamp': now_unix,
            'Value': lag,
            'Unit': 'Seconds',
            'StorageResolution': 60
        }
    ]
    return metric_data


def put_metrics_to_cloudwatch(repl_metrics):
    # lambda位于vpc内，访问cloudwatch需要走 vpc endpoint
    cw_client = boto3.client(
        'cloudwatch', endpoint_url='https://vpce-0c921xxxx-nhs3qefw.monitoring.ap-northeast-1.vpce.amazonaws.com')
    cw_client.put_metric_data(Namespace='mongoshake', MetricData=repl_metrics)


def fetch_and_put_data(url):
    # 从mongoshake接口获取数据
    result = query_repl_result(url)
    # 组装cloudwatch接收的payload
    metric_data = parse_metrics(result)
    # 推送payload
    put_metrics_to_cloudwatch(metric_data)


def lambda_handler(event, context):
    # url清单从 URLS 环境变量提供
    urls = os.getenv('URLS').split(',')
    for url in urls:
        fetch_and_put_data(url)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
