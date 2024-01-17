#!/usr/bin/env python3

import boto3
import requests
import zipfile
import logging
import io
from botocore.exceptions import ClientError
import click
import shutil
import subprocess

@click.command()
# Set destination path to store the bandit results files
@click.option('--destination-directory', '-d', '--dest', required=True, type=str)

def main(destination_directory):
    ec2_client = boto3.client('ec2')
    regions = ec2_client.describe_regions()

    # Find the location of the bandit executable
    bandit_path = shutil.which('bandit')

    for region in regions['Regions']:
        lambda_client = boto3.client('lambda', region_name=region['RegionName'])
        functions = lambda_client.list_functions()
        for function in functions['Functions']:
            if 'python' in function['Runtime']:
                code_url = lambda_client.get_function(FunctionName=function['FunctionName'])['Code']['Location']
                destination_folder = function['FunctionName']
                url_response = requests.get(code_url)
                if url_response.status_code == 200:
                    zip_file = zipfile.ZipFile(io.BytesIO(url_response.content))
                    zip_file.extractall(destination_folder)
                    print(f"Downloaded and extracted to {destination_folder}")

                    if bandit_path is not None:
                        # Run bandit as a subprocess
                        bandit_cmd = f'{bandit_path} -r {destination_folder} -f json -o /{destination_directory}/{destination_folder}.json'
                        result = subprocess.run(bandit_cmd, shell=True)

                    else:
                        print("Error: bandit executable not found. Make sure it is installed and in your system's PATH.")
                    shutil.rmtree(destination_folder)

                else:
                    print(f"Failed to download. Status code: {url_response.status_code}")





if __name__ == '__main__':
    main()