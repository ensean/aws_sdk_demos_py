import boto3
from datetime import datetime

lightsail_client = boto3.client('lightsail',region_name='us-west-2')


def query_network_in(instance_name):
    resp = lightsail_client.get_instance_metric_data(
        instanceName=instance_name,
        metricName="NetworkIn",
        period=2678400,
        startTime=datetime(2020,12,1),
        endTime=datetime(2020,12,31),
        unit='Bytes',   # 汇总单位只能是字节
        statistics=['Sum']
    )
    return resp

def query_network_out(instance_name):
    resp = lightsail_client.get_instance_metric_data(
        instanceName=instance_name,
        metricName="NetworkOut",
        period=2678400,
        startTime=datetime(2020,12,22),
        endTime=datetime(2020,12,31),
        unit='Bytes',   # 汇总单位只能是字节
        statistics=['Sum']
    )
    return resp


def main():
    resp = query_network_out('Ubuntu-1')
    print(resp)

if __name__ == "__main__":
    main()