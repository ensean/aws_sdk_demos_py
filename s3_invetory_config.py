import logging
import boto3

s3_client = boto3.client('s3')


def get_bucket_list(reg='us-east-1'):
    """
    get buckets in the specified region
    """
    resp = s3_client.list_buckets()
    reg_buckets = []
    # get all buckets' name
    bucket_names = [b['Name'] for b in resp['Buckets']]

    # filter by region
    for b in bucket_names:
        resp = s3_client.get_bucket_location(Bucket=b)
        if resp['LocationConstraint'] == reg:
            reg_buckets.append(b)
    return reg_buckets


def create_inv_config(src_bucket, dest_bucket):
    """
    create inventory configuration for src_bucket,
    export the result to the dest_bucket
    """
    try:
        s3_client.put_bucket_inventory_configuration(
                Bucket=src_bucket,
                Id='inventory-created-by-python-sdk',
                InventoryConfiguration={
                    'Destination': {
                        'S3BucketDestination': {
                            'Bucket': 'arn:aws:s3:::%s' % dest_bucket,
                            'Format': 'CSV',
                            'Prefix': 'inv-%s' % src_bucket,
                        }
                    },
                    'IsEnabled': True,
                    'Id': 'inventory-created-by-python-sdk',
                    'IncludedObjectVersions': 'Current',
                    'Schedule': {
                        'Frequency': 'Daily'
                    }
                },
            )
        print('set inventory for %s success' % src_bucket)
    except Exception as e:
        print('set inventory for %s failed' % src_bucket)
        print(e)
    

def has_inv_config(bucket):
    resp = s3_client.list_bucket_inventory_configurations(Bucket=bucket)
    if len(resp.get('InventoryConfigurationList', [])) == 0:
        return False
    else:
        return True


def main():
    # inventory bucket name
    inventory_dest_bucket = 'xxxx'
    b_list = get_bucket_list('ap-southeast-1')
    for bucket in b_list:
        if not has_inv_config(bucket):
            create_inv_config(bucket, inventory_dest_bucket)
    
if __name__ == '__main__':
    main()
