import boto3
import logging
import bandit
from botocore.exceptions import ClientError


def main():
    ec2_client = boto3.client('ec2')
    regions = ec2_client.describe_regions()

    for region in regions['Regions']:
        lambda_client = boto3.client('lambda', region_name=region['RegionName'])
        functions = lambda_client.list_functions()
        for function in functions['Functions']:
            if 'python' in function['Runtime']:
                code_url = lambda_client.get_function(FunctionName=function['FunctionName'])['Code']['Location']
                print(function['FunctionName'], code_url, region['RegionName'], '', sep='\n')



if __name__ == '__main__':
    main()