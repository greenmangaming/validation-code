import boto3
import os
import click
import sys
from botocore.exceptions import ClientError
import threading


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
        if filename.endswith('.json'):
            response = checkValidity(pathLocation, filename)
            if response != None:
                errors_[filename] = response
    return(errors_)

def upload(pathLocation, filename, s3Dir, s3Bucket):
    if not filename.endswith('.json'):
        return
    s3Bucket.put_object(Key='gmg-interns/owainwi/{}/{}'.format(s3Dir, filename),
                    Body=open('{}/{}'.format(pathLocation, filename), 'r').read())
    print('{} uploaded to s3!'.format(filename))

def uploadFiles(pathLocation, s3Dir):
    s3 = boto3.resource('s3')
    bucket = 'gmg-general-dev-test'
    s3Bucket = s3.Bucket(bucket)
    filenames = []
    for filename in os.listdir(pathLocation):
        filenames.append(filename)
    for fname in filenames:
        t = threading.Thread(target = upload, args = (pathLocation, fname, s3Dir, s3Bucket)).start()

@click.command()
@click.option('--path', prompt='Path', help='The Path of the CloudFormation folder.')

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
        uploadFiles(path_mgmnt, 'mgmnt')
        uploadFiles(path_prod, 'prod')
        uploadFiles(path_staging, 'staging')
        sys.exit()
    else:
        print('There were errors so the files could not be uploaded to s3.')
        sys.exit()

if __name__ == '__main__':
    main()
