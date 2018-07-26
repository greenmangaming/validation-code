import boto3
import os
import click
import sys
from botocore.exceptions import ClientError

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
        elif response != None:
            errors_[filename] = response
        elif (os.stat('.gitignore').st_size > 51200):
            sys.exit('File size too large (>51200 B)')
    return(errors_)

def uploadFiles(pathLocation):
    for filename in os.listdir(pathLocation):
        s3 = boto3.resource('s3')
        s3Bucket = s3.Bucket('s3://gmg-general-dev-test/gmg-interns/owainwi/')
        s3Bucket = .put_object(Key=filename,
                    Body=open('{}/{}'.format(folder, filename), 'r').read())
        print('{} uploaded to s3!'.format(filename))

@click.command()
@click.option('--Path', prompt='Path', help='The Path of the CloudFormation folder.')

def main(path):
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
    if len(keys) == 0:
        uploadFiles(path_mgmnt)
        uploadFiles(path_prod)
        uploadFiles(path_staging)
        sys.exit()
    else:
        print('There were errors so the files could not be uploaded to s3.')
        sys.exit()

if __name__ == '__main__':
    main()
