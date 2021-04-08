import boto3
import datetime
cloudwatch = boto3.client('cloudwatch',
                          aws_access_key_id='xxx',
                          aws_secret_access_key='xxx',
                          region_name='eu-entral-1')

resp = cloudwatch.get_metric_data(
    MetricDataQueries=[
        {
            'Id': 'string',
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/EC2',
                    'MetricName': 'CPUUtilization',
                    'Dimensions': [
                        {
                            'Name': 'InstanceId',
                            'Value': 'i-xxxxx'
                        },
                    ]
                },
                'Period': 300,
                'Stat': 'Average',
            },
        },
    ],
    StartTime=datetime.datetime(2021, 3, 29),
    EndTime=datetime.datetime(2021, 3, 31),
    MaxDatapoints=123,

)
print(resp)
