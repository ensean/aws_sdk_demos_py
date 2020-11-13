import logging
import boto3
import requests
import json

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response



def main():
    # 生成上传presigned url
    response = create_presigned_post('liyx-media','upload/presigned/test.jpg')
    if response is None:
        exit(1)
    logging.info(json.dumps(response))
    # 将本地文件使用request post通过presigned url上传至s3
    object_name='/tmp/663466.jpg'
    logging.info("Starts to upload...")
    with open(object_name, 'rb') as f:
        files = {'file': (object_name, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    # 查看上传结果
    logging.info(f'File upload HTTP status code: {http_response.status_code}')
    
    # 获取访问pre-signed访问地址
    resp = create_presigned_url('liyx-media', 'upload/presigned/test.jpg')
    logging.info(json.dumps(resp))
    


if __name__ == "__main__":
    main()