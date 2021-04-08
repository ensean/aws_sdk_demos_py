import boto3

s3_client = boto3.client('s3')


resp = s3_client.upload_file('/tmp/panda.png',
    'load-runner-tokyo-containerbucket-1ogw46y9hzs28',
    'upload_by_boto3.png')

print(resp)

