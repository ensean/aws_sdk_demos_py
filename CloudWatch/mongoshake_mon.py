"""
采集mongoshake增量复制信息，主要包含如下指标
    tps,
    延迟
"""
import boto3
import sys
import json
import requests


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
    cw_client = boto3.client('cloudwatch')
    cw_client.put_metric_data(Namespace='mongoshake', MetricData=repl_metrics)


def main():
    if len(sys.argv) != 2:
        print("python mongoshake_mon.py url or python mongoshake_mon.py url1,url2,url3")
    else:
        urls = sys.argv[1].split(',')
        for url in urls:
            repl_result = query_repl_result(url)
            metrics = parse_metrics(repl_result)
            put_metrics_to_cloudwatch(metrics)

if __name__ == '__main__':
    main()
