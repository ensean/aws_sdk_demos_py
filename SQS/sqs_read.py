import boto3
import time
import json

def rev_msg(client, q_url):
    resp = client.receive_message(
        QueueUrl=q_url,
        AttributeNames = ['MessageGroupId', 'SentTimestamp'],
        WaitTimeSeconds = 2,
    )
    return resp.get('Messages', [])

def del_msg(client, q_url, msg_reciept):
    response = client.delete_message(
        QueueUrl=q_url,
        ReceiptHandle=msg_reciept
    )

def main():
    sqs_client = boto3.client('sqs')
    q_url = 'https://sqs.ap-northeast-1.amazonaws.com/123456789123/testq.fifo'
    while True:
        msg_list = rev_msg(sqs_client, q_url)
        if len(msg_list) == 0:
            print('no msg got from sqs')
        for msg in msg_list:
            msg_gid = msg['Attributes']['MessageGroupId']
            ts = msg['Attributes']['SentTimestamp']
            if msg_gid == 'msg3':
                print('proccessing msg3 %s...' % ts)
                msg_reciept = msg['ReceiptHandle']
                del_msg(sqs_client, q_url, msg_reciept )
                time.sleep(3)
            else:
                print('check for msg for message group id msg3')
if __name__ == '__main__':
    main()