import boto3
import os
import click
import sys
from botocore.exceptions import ClientError

# /Users/owainwilliams/Desktop/validation-code/cloudformation

divider = '===================================================================='
client = boto3.client('cloudformation')

def confirm(path):
    print('Looking for files in path: {}'.format(path))

def checkValidity(folder, filename):
    json = open('{}/{}'.format(folder, filename), 'r').read()
    try:
        response = client.validate_template(TemplateBody=json)
    except ClientError as e:
        return('\n{}\n'.format(e))

@click.command()
@click.option('--path', prompt='path', help='The path of the CloudFormation folder.')


def main (path):
    num = 0
    errors = {}
    confirm(path)
    path_mgmnt = '{}/{}'.format(path, 'mgmnt')
    for filename in os.listdir(path_mgmnt):
        num += 1
        response = checkValidity(path_mgmnt, filename)
        if response != None:
            key = '{}_{}'.format(filename, num)
            errors[key] = response

    path_prod = '{}/{}'.format(path, 'prod')
    for filename in os.listdir(path_prod):
        num += 1
        response = checkValidity(path_prod, filename)
        if response != None:
            key = '{}_{}'.format(filename, num)
            errors[key] = response

    path_staging = '{}/{}'.format(path, 'staging')
    for filename in os.listdir(path_staging):
        num += 1
        response = checkValidity(path_staging, filename)
        if response != None:
            key = '{}_{}'.format(filename, num)
            errors[key] = response

    if len(errors.keys()) != 0:
        # I would use 'for key, value in errors:' but there are too
        # many values to unpack
        for i in range(len(errors.keys())):
            keys = list(errors.keys())
            print('{}\n{}\n{}\n\n\n{}\n\n\n'.format(
                            divider, keys[i], divider, errors[keys[i]]))
        print('\n\n{}\n{}\nIn total there were {} errors.\n{}\n{}'.format(
                        divider, divider, len(errors.keys()), divider, divider))
    else:
        sys.exit()

if __name__ == '__main__':
    main()
