import boto3
import time
client = boto3.client('rekognition', region_name = 'ap-northeast-2')

"""
演示 rek 分析存储在 S3 中的视频文件，权限配置：
1. 创建 rek 使用的角色
2. SNS topic 访问策略中添加规则允许 rek 角色发布消息
{
  "Sid": "rek",
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::123456789012:role/stored_video_analysis"
  },
  "Action": [
    "SNS:Publish"
  ],
  "Resource": "arn:aws:sns:ap-northeast-2:123456789012:rek-video"
}
"""
def main():
    resp = client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': 'rekognition-video-console-demo-icn-123456789012-1708566611',
                'Name': '2edd1c948fb9dffc45aba98636960ef0.mp4',
            }
        },
        MinConfidence = 70,
        NotificationChannel={
            'SNSTopicArn': 'arn:aws:sns:ap-northeast-2:123456789012:rek-video',
            'RoleArn': 'arn:aws:iam::123456789012:role/stored_video_analysis'
        },
        Settings={
        'GeneralLabels': {
            'LabelInclusionFilters': [
                'Box',
                'Package',
                'Package Delivery',
            ],
        }
    }
    )
    job_id = resp.get('JobId')
    # 推荐通过监听 sns 来判断检测任务是否完成，检测任务完成且成功情况下再获取检测结果
    while True:
        resp = client.get_label_detection(JobId = job_id)
        job_status = resp.get('JobStatus')
        if job_status == 'IN_PROGRESS':
            time.sleep(5)
            print("detect job in progress")
        elif job_status == 'SUCCEEDED':
            print(resp.get('Labels'))
            break
        else:
            print("detect job failed")
            break


if __name__ == "__main__":
    main()