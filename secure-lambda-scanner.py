import boto3
import requests
import zipfile
import logging
import io
import os
from bandit.core import config as bandit_config
from bandit.core import manager as bandit_manager
from botocore.exceptions import ClientError


def main():
    ec2_client = boto3.client('ec2')
    regions = ec2_client.describe_regions()

    config = bandit_config.BanditConfig()
    manager = bandit_manager.BanditManager(config, "Full")

    for region in regions['Regions']:
        lambda_client = boto3.client('lambda', region_name=region['RegionName'])
        functions = lambda_client.list_functions()
        for function in functions['Functions']:
            if 'python' in function['Runtime']:
                code_url = lambda_client.get_function(FunctionName=function['FunctionName'])['Code']['Location']
                print(function['FunctionName'], code_url, region['RegionName'], '', sep='\n')
                destination_folder = function['FunctionName']
                url_response = requests.get(code_url)
                if url_response.status_code == 200:
                    zip_file = zipfile.ZipFile(io.BytesIO(url_response.content))
                    zip_file.extractall(destination_folder)
                    print(f"Downloaded and extracted to {destination_folder}")
                else:
                    print(f"Failed to download. Status code: {url_response.status_code}")

                for filename in os.listdir(destination_folder):
                    f = os.path.join(destination_folder, filename)
                    if os.path.isfile(f):
                        issues = manager.run_tests(f)





if __name__ == '__main__':
    main()