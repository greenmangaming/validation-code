import boto3
import os
import click
import sys
from botocore.exceptions import ClientError

# /Users/owainwilliams/Desktop/validation-code/cloudformation

divider = '===================================================================='
client = boto3.client('cloudformation')

def checkValidity(folder, filename):
    json = open('{}/{}'.format(folder, filename), 'r').read()
    try:
        response = client.validate_template(TemplateBody=json)
    except ClientError as e:
        return('\n{}\n'.format(e))

def checkFiles(pathLocation):
    errors_ = {}
    for filename in os.listdir(pathLocation):
        response = checkValidity(pathLocation, filename)
        if response != None:
            errors_[filename] = response
    return(errors_)


@click.command()
@click.option('--path', prompt='path', help='The path of the CloudFormation folder.')


def main (path):
    path_mgmnt = '{}/{}'.format(path, 'mgmnt')
    path_prod = '{}/{}'.format(path, 'prod')
    path_staging = '{}/{}'.format(path, 'staging')
    errors = {}
    if checkFiles(path_staging) != None:
        errors.update(checkFiles(path_staging))
    if checkFiles(path_prod) != None:
        errors.update(checkFiles(path_prod))
    if checkFiles(path_mgmnt) != None:
        errors.update(checkFiles(path_mgmnt))
    keys = list(errors.keys())
    values = list(errors.values())
    for i in range(len(keys)):
        print(  divider + '\n' +
                keys[i] + '\n' +
                divider + '\n' +
                values[i])



if __name__ == '__main__':
    main()
