#!/usr/bin/env python3

import boto3
import requests
import zipfile
import logging
import io
from botocore.exceptions import ClientError
import click
import shutil
import subprocess  # nosec B404

@click.command()
@click.option('--destination-directory', '-d', '--dest', required=True, type=str, help="Set destination path to store the bandit results files.")
@click.option('--format', '-f', '--fmt', default='txt', show_default=True, type=click.Choice(['txt', 'json', 'yaml', 'xml', 'html', 'csv']), help="Specify the output format. Default is set to txt")


def main(destination_directory, format):
    
    # Set the timeout value (in seconds)
    timeout_seconds = 10

    ec2_client = boto3.client('ec2')
    regions = ec2_client.describe_regions()

    # Find the location of the bandit executable
    bandit_path = shutil.which('bandit')

    # Loop over all regions to find all lambda functions in the AWS account
    for region in regions['Regions']:
        lambda_client = boto3.client('lambda', region_name=region['RegionName'])
        functions = lambda_client.list_functions()
        # Loop over all python lambda functions in the region
        for function in functions['Functions']:
            if 'python' in function['Runtime']:
                # Download code from URL and extract all files
                code_url = lambda_client.get_function(FunctionName=function['FunctionName'])['Code']['Location']
                destination_folder = function['FunctionName']
                url_response = requests.get(code_url, timeout=timeout_seconds)
                if url_response.status_code == 200:
                    zip_file = zipfile.ZipFile(io.BytesIO(url_response.content))
                    zip_file.extractall(destination_folder)
                    print(f"Downloaded and extracted to {destination_folder}")

                    if bandit_path is not None:
                        # Run bandit as a subprocess
                        bandit_cmd = f"{bandit_path} -r {destination_folder} -f {format} -o /{destination_directory}/{destination_folder}.{format}"
                        result = subprocess.run(bandit_cmd, shell=False)  # nosec B603

                    else:
                        print("Error: bandit executable not found. Make sure it is installed and in your system's PATH.")
                    shutil.rmtree(destination_folder)

                else:
                    print(f"Failed to download. Status code: {url_response.status_code}")





if __name__ == '__main__':
    main()