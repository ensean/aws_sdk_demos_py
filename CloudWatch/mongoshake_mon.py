"""
采集mongoshake增量复制信息，主要包含如下指标
    tps,
    延迟
"""
import boto3
import sys
import json
import requests
import datetime
import random
import time


def query_repl_result(url):
    resp = requests.get(url)
    result = json.loads(resp.content)
    return result


def parse_metrics(repl_result):
    tps = repl_result.get('tps', -1)
    who = repl_result.get('who')
    now_unix = repl_result.get('now').get('unix')
    lsn_unix = repl_result.get('lsn').get('unix')
    lsn_ack_unix = repl_result.get('lsn_ack').get('unix')
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
            'StorageResolution': 60
        }
    ]
    return metric_data


def put_metrics_to_cloudwatch(repl_metrics):
    cw_client = boto3.client('cloudwatch')
    cw_client.put_metric_data(Namespace='mongoshake', MetricData=repl_metrics)


def main():
    if len(sys.argv) != 2:
        print("python mongoshake_mon.py url")
    else:
        for i in range(1, 100):
            # repl_result = query_repl_result(sys.argv[1])
            ts = int(datetime.datetime.now().timestamp())
            repl_result = {
                "logs_get": 2,
                "logs_repl": 0,
                "logs_success": 0,
                "lsn": {
                    "time": "1970-01-01 08:00:00",
                    "ts": "0",
                    "unix": ts - 120
                },
                "lsn_ack": {
                    "time": "1970-01-01 08:00:00",
                    "ts": "0",
                    "unix": ts - 130
                },
                "lsn_ckpt": {
                    "time": "1970-01-01 08:00:00",
                    "ts": "0",
                    "unix": ts - 140
                },
                "now": {
                    "time": "2020-04-03 18:32:28",
                    "unix": ts
                },
                "replset": "zz-186-replica-3177x",
                "tag": "improve-2.4.1,6badf6dfa00ebc0fc1a34e4864814733c5849daf,release,go1.10.8,2020-04-03_18:19:37",
                "tps": random.randint(3000,6000),
                "who": "mongoshake-inst1"
            }
            metrics = parse_metrics(repl_result)
            put_metrics_to_cloudwatch(metrics)
            time.sleep(61)


if __name__ == '__main__':
    main()
