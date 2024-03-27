import boto3
import requests
import json
import urllib

BASE_URL = 'https://signin.aws.amazon.com/federation'
TARGET_URL = 'https://console.aws.amazon.com/'
def get_fedration_token():
    client = boto3.client('sts')
    fid = client.get_federation_token(
        Name = 'dynamic_user',
        PolicyArns = [
            {'arn':'arn:aws:iam::aws:policy/AdministratorAccess'}
        ],
        DurationSeconds=900,
    )
    return fid

def get_signin_token(fid):
    # not impl by boto3 since 2018 https://github.com/boto/boto3/issues/1695
    fid = get_fedration_token()
    session = {
        "sessionId": fid.get("Credentials").get("AccessKeyId"),
        "sessionKey": fid.get("Credentials").get("SecretAccessKey"),
        "sessionToken": fid.get("Credentials").get("SessionToken"),
    }
    json_string_with_temp_credentials = json.dumps(session)
    print(json_string_with_temp_credentials)
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&SessionDuration=43200"
    request_parameters += "&Session=" + urllib.parse.quote_plus(json_string_with_temp_credentials)
    request_url =  BASE_URL + request_parameters
    print("request_url: "+request_url)
    r = requests.get(request_url)
    signin_token = json.loads(r.text)
    return signin_token

def get_signin_url(signin_token):
    # contruct console login url
    request_parameters = "?Action=login" 
    # request_parameters += "&Issuer=Example.org" 
    request_parameters += "&Destination=" + urllib.parse.quote_plus(TARGET_URL)
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    login_url = BASE_URL + request_parameters

    # Send final URL to stdout
    print(login_url)

def main():
    fid = get_fedration_token()
    signin_token = get_signin_token(fid)
    get_signin_url(signin_token)

if __name__ == "__main__":
    main()