# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import os
import json
import urllib.parse
import yaml

print('Loading function')

s3 = boto3.client('s3')
state_machine_arn = os.getenv('STATE_MACHINE')
step_functions = boto3.client("stepfunctions")


def lambda_handler(event, context):
    # Get event parameters
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # Get object config file
    try:
        config_file = s3.get_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(e)
        raise e

    # Parse yaml file
    try:
        configfile = yaml.safe_load(config_file["Body"])
    except yaml.YAMLError as exc:
        return exc

    for stackset in configfile["stacksets"]:
        stackset["account"] = configfile["account"]
        if "terminate" in configfile and configfile["terminate"]:
            stackset["terminate"] = configfile["terminate"]

    # Start step function
    print("Trigerring Step functions with these values: " + json.dumps(configfile, indent=2))
    response = step_functions.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(configfile))

    return response['executionArn']
