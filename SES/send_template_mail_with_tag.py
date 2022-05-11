import boto3

# use ses v2 api

def create_contact_list(ses_client, c_list_name):
    resp = ses_client.create_contact_list(
        ContactListName = c_list_name,
        Topics = [
            {
                'TopicName': 'Table',
                'DisplayName': 'Table',
                'Description': 'Tables, such as dinner table,coffee table etc.',
                'DefaultSubscriptionStatus': 'OPT_IN'
            },
            {
                'TopicName': 'Chairs',
                'DisplayName': 'Chairs',
                'Description': 'Chairs, such as dinner table,coffee table etc.',
                'DefaultSubscriptionStatus': 'OPT_IN'
            },
        ]
    )
    print(resp)

def create_teamplte(ses_client):

    response = ses_client.create_email_template(
        TemplateName='first_email_template_unsub4',
        TemplateContent={
            'Subject': 'Greetings, {{name}}!',
            'Text': 'Dear {{name}},\r\nYour favorite animal is {{favoriteanimal}}.\r\n{{amazonSESUnsubscribeUrl}}',
            'Html': '<h1>Hello {{name}},</h1><p>Your favorite animal is {{favoriteanimal}}.</p><br>Click <a href={{amazonSESUnsubscribeUrl}}>here</a> to unsub'
        }
    )
    print(response)


def send_mail_with_template(ses_client, template_name, template_data):
    response = ses_client.send_email(
        FromEmailAddress='no_reply@mail.ensean.space',
        Destination={
            'ToAddresses': [
                'jim@outlook.com',
            ]
        },
        ReplyToAddresses=[
            'support@mail.ensean.space',
        ],
        Content={
            'Template': {
                'TemplateName': template_name,
                'TemplateData': template_data
            }
        },
        # user define tags to report to email events
        EmailTags=[
            {
                'Name': 'Program_Id',
                'Value': 'Speical_Sale_For_Tables'
            },
            {
                'Name': 'Campaign_Id',
                'Value': '13490jkksajsjkjlksf',
            }
        ],
        ConfigurationSetName='cs',
        # for unsubscirption configuration
        ListManagementOptions={
            'ContactListName': 'cx_list_2022'
        }
    )
    print(response)


def main():
    ses_client = boto3.client('sesv2', region_name='us-west-2')
    # create_teamplte(ses_client)
    # create_contact_list(ses_client, 'cx_list_2022')
    template_data ="{ \"name\":\"Jim\", \"favoriteanimal\": \"alligator\" }"
    send_mail_with_template(ses_client, 'first_email_template_unsub4', template_data)


if __name__ == '__main__':
    main()
