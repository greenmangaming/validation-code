import boto3
import os
import click
import sys
from botocore.exceptions import ClientError
import threading


divider = '=' * 70
client = boto3.client('cloudformation')

def checkValidity(root, filename):
    json = open('{}/{}'.format(root, filename), 'r').read()
    try:
        response = client.validate_template(TemplateBody=json)
    except ClientError as e:
        return('\n{}\n'.format(e))

def checkFiles(path):
    errors_ = {}
    paths = []
    for root, dirs, files in os.walk(path):
        paths.append(root)
        for filename in os.listdir(root):
            if not filename.endswith('.json'):
                continue
            response = checkValidity(root, filename)
            if response != None:
                errors_[filename] = response
    return(errors_, paths)

def upload(path, filename, s3Dir, s3Bucket, subDir):
    if not filename.endswith('.json'):
        return
    s3Bucket.put_object(
        Key='{}{}/{}'.format(s3Dir, subDir, filename),
        Body=open('{}/{}'.format(path, filename), 'r'
    ).read())
    print('{} uploaded to s3!'.format(filename))

def uploadFiles(path, s3Dir, orDir):
    s3 = boto3.resource('s3')
    bucket = 'gmg-general-dev-test'
    s3Bucket = s3.Bucket(bucket)
    filenames = []
    subDir = path[len(orDir):]
    for filename in os.listdir(path):
        filenames.append(filename)
    for fname in filenames:
        t = threading.Thread(
            target = upload,
            args = (path, fname, s3Dir, s3Bucket, subDir)
        ).start()

@click.command()
@click.option(
    '--path',
    prompt='Path',
    help='The Path of the CloudFormation folder.'
)
@click.option(
    '--dir',
    prompt='Directory',
    help='The Directory of the s3 folder.'
)

def main(path, dir):
    errors = {}
    checkFilesRes = checkFiles(path)

    if dir.endswith('/'):
        dir = dir[:-1]
    if dir.startswith('/'):
        dir = dir[1:]
    errors.update(checkFilesRes[0])

    keys = list(errors.keys())
    values = list(errors.values())

    for i in range(len(keys)):
        print(  divider + '\n' +
                keys[i] + '\n' +
                divider + '\n' +
                values[i])

    if len(keys) == 0:

        paths = checkFilesRes[1]

        for val in paths:
            uploadFiles(val, dir, paths[0])
        sys.exit()
    else:
        print('There were errors so the files could not be uploaded to s3.')
        sys.exit()

if __name__ == '__main__':
    main()
