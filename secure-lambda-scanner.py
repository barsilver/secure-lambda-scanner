import boto3
import requests
import zipfile
import logging
import io
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
                get_url = requests.get(code_url)
                zip_file = zipfile.ZipFile(io.BytesIO(get_url.content))
                zip_file.extractall(function['FunctionName'])
                #open(function['FunctionName'], "wb").write(url_response.content)
                #issues = manager.run_tests(code_url)





if __name__ == '__main__':
    main()