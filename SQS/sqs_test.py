import boto3
import random
import json
import string
letters = string.ascii_lowercase

def send_msg(sqs_client, q_url, msg, msg_gid):
    sqs_client.send_message(
        QueueUrl = q_url,
        MessageBody = msg,
        MessageGroupId = msg_gid
    )


def main():
    client = boto3.client('sqs')
    for i in range(100):

        msg = {
            'aaa': ''.join(random.choice(letters) for i in range(10)),
            'xxxx': 'cccc'
        }
    
        msg_gid = 'msg%s' % random.randint(1,4)
        print("send msg %s" % i)
        send_msg(client, 'https://sqs.ap-northeast-1.amazonaws.com/123456789123/testq.fifo', json.dumps(msg), msg_gid)

if __name__ == '__main__':
    main()