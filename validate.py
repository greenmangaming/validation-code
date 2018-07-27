import boto3
import os
import click
import sys
from botocore.exceptions import ClientError
import threading
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# /Users/owainwilliams/Desktop/validation-code/cloudformation/
# gmg-general-dev-test/gmg-interns/owainwi

divider = '=' * 70
client = boto3.client('cloudformation')

def checkValidity(bucket, val):
    url = 'https://s3.amazonaws.com/' + bucket + '/' + val
    try:
        response = client.validate_template(TemplateURL=url)
    except ClientError as e:
        print('error - ' + url)
        return(e)

def checkFiles(bucket, keys):
    errors = []
    for val in keys:
        response = checkValidity(bucket, val)
        if response == None:
            continue
        errors.append({
            'file': val,
            'error': response
        })
    return(errors)

def upload(body, key, s3Bucket):
    s3Bucket.put_object(Key = key, Body = body)
    return(key + ' has been uploaded to s3')

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

    keys = []
    fs = []
    paths = []
    s3 = boto3.resource('s3')
    bucket = 'gmg-general-dev-test'
    s3Bucket = s3.Bucket(bucket)
    if not dir.endswith('/'):
        dir = dir + '/'
    if dir.startswith('/'):
        dir = dir[1:]

    for root, dirs, files in os.walk(path):
        paths.append(root)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for val in paths:
            sub = val[len(paths[0]):]
            for filename in os.listdir(val):
                if not filename.endswith('.json'):
                    continue
                key = dir + sub + '/' + filename
                body = open(val + '/' + filename, 'r').read()
                keys.append(key)
                future = pool.submit(upload, body, key, s3Bucket)
                fs.append(future)
        for future in concurrent.futures.as_completed(fs):
            print(future.result())

    s3Location = bucket + '/' + dir
    errors = checkFiles(bucket, keys)

    if len(errors) > 0:
        for i in range(len(errors)):
            print(
                divider + '\n' +
                errors[i]['file'] + '\n' +
                divider + '\n'
            )
            print(errors[i]['error'])
    else:
        print('There were no errors!')

if __name__ == '__main__':
    main()
