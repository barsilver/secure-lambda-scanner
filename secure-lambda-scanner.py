#!/usr/bin/env python3

import boto3
import requests
import zipfile
import logging
import io
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
import shutil
import subprocess  # nosec B404
import os
from datetime import datetime


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def scan_lambda_function(event, context):

    # Initialize AWS EC2 client
    ec2_client = boto3.client('ec2')

    # Find the location of the bandit executable
    bandit_path = shutil.which('bandit')

    lambda_function_name = event['detail']['requestParameters']['functionName']
    # Test - print function name from event
    print(f"{lambda_function_name}")
    python_code = get_lambda_function_code(lambda_function_name)

    format = os.environ['BANDIT_RESULTS_FORMAT']

    if bandit_path is not None:
        results_file = f"{lambda_function_name}.{format}"
        # Run bandit as a subprocess
        bandit_cmd = f"{bandit_path} -r {lambda_function_name} -f {format} -o {results_file}"
        result = subprocess.run(bandit_cmd, shell=False)  # nosec B603

        # Generate a timestamp string for creating a unique S3 key
        timestr = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        s3_key = f"{lambda_function_name}_{timestr}.{format}"
        # Upload the scan results file to S3 with the constructed key
        upload_results_to_s3(results_file, s3_key)

    else:
        logger.error("Bandit executable not found. Make sure it is installed and in your system's PATH.")
    
    shutil.rmtree(destination_folder)


def upload_results_to_s3(local_file, s3_file):
    # Initialize AWS S3 client
    s3_client = boto3.client('s3')

    try:
        # Upload the local file to the specified S3 bucket with the given key
        s3_client.upload_file(local_file, os.environ['BUCKET_NAME'], s3_file)
         # Generate a pre-signed URL for the uploaded object with a specified expiration time
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': os.environ['BUCKET_NAME'],
                'Key': s3_file
            },
            # Expiration time of the pre-signed URL in seconds (24 hours in this case)
            ExpiresIn=24 * 3600
        )

        # Log a success message along with the generated pre-signed URL
        logger.info("Upload Successful. URL: %s", url)
        return url
    except NoCredentialsError:
        # Log an error message when AWS credentials are not available
        logger.error("Credentials not available")
        return None

def get_lambda_function_code(lambda_function_name):

    # Set this value to 10
    timeout_seconds = os.environ['TIMEOUT_SECONDS']

    lambda_client = boto3.client('lambda')
    response = lambda_client.get_function(FunctionName=lambda_function_name['FunctionName'])
    
    # Download code from URL
    code_url = response['Code']['Location']

    url_response = requests.get(code_url, timeout=timeout_seconds)
    if url_response.status_code == 200:
        # Extract all files to a temporary folder named as the lambda function name
        zip_file = zipfile.ZipFile(io.BytesIO(url_response.content))
        zip_file.extractall(lambda_function_name)
    else:
        logger.error("Failed to download. Status code: {url_response.status_code}")
