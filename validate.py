import boto3
import os

from botocore.exceptions import ClientError

divider = '===================================================================='

client = boto3.client('cloudformation')
path_mgmnt = '/Users/owainwilliams/Desktop/validation-code/cloudformation/mgmnt'
path_prod = '/Users/owainwilliams/Desktop/validation-code/cloudformation/prod'
path_staging = '/Users/owainwilliams/Desktop/validation-code/cloudformation/staging'

def checkValidity(path):
    json = open('{}/{}'.format(path, filename), 'r').read()
    try:
        response = client.validate_template(TemplateBody=json)
    except ClientError as e:
        print('\n{}\n{}\n{}\n'.format(divider, filename, divider))
        return('\n{}\n'.format(e))

for filename in os.listdir(path_mgmnt):
    response = checkValidity(path_mgmnt)
    if response != None:
        print(response)

for filename in os.listdir(path_prod):
    response = checkValidity(path_prod)
    if response != None:
        print(response)

for filename in os.listdir(path_staging):
    response = checkValidity(path_staging)
    if response != None:
        print(response)
