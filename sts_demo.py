import boto3
import json
"""
功能说明：
    1)模拟sts服务端生成临时凭证，访问s3特定文件
    2)模拟客户端使用此临时凭证删除特定文件
配置说明：
    1）创建IAM角色，赋予S3FullAccess，作为临时凭证模板（需要配置服务端代码IAM能够assume改角色）

参考资料：
    1.STS服务端PHP样例代码：https://stackoverflow.com/questions/21956794/aws-assumerole-user-is-not-authorized-to-perform-stsassumerole-on-resource
    2.iOS SDK S3传输工具API文档：https://docs.aws.amazon.com/AWSiOSSDK/latest/Classes/AWSS3TransferUtility.html
    3.iOS SDK S3文件操作Demo：https://github.com/awslabs/aws-sdk-ios-samples/tree/main/S3TransferUtility-Sample/Objective-C
        备注：需要参考API文档将凭证从Cognito替换为STS临时凭证
"""

sts_client = boto3.client('sts')

def gen_single_obj_policy(bucket, obj_key):
    # 限制临时凭证只能操作
    single_obj_access_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": "arn:aws:s3:::%s/%s" % (bucket,obj_key)
            }
        ]
    }
    return json.dumps(single_obj_access_policy)

def gen_temp_credential(bucket, obj_key):
    # 以角色mobileUpload2S3Role为模板获取权限，但附加策略限制只能访问特定文件
    resp = sts_client.assume_role(RoleArn = 'arn:aws:iam::you_account_id:role/mobileUpload2S3Role',
                                RoleSessionName = "%s-%s" % (bucket,obj_key.replace('/','-')),
                                DurationSeconds=900,
                                Policy=gen_single_obj_policy(bucket, obj_key))
    return resp['Credentials']

def main():
    # 模拟服务端生成临时凭证
    credentials = gen_temp_credential('bucket_name', 'imgs/panda.png')

    # 模拟客户端对桶中的文件进行操作
    ## 获取s3客户端
    s3_client = boto3.client('s3',
                            aws_access_key_id=credentials['AccessKeyId'],
                            aws_secret_access_key=credentials['SecretAccessKey'],
                            aws_session_token=credentials['SessionToken'])
    ## 模拟客户端删除文件
    response = s3_client.delete_object(Bucket='bucket_name', Key='imgs/panda.png')
    print(json.dumps(response))


if __name__ == '__main__':
    main()