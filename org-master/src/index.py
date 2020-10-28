import json
import boto3


SUPPORTED_REGIONS = ["eu-west-1", "eu-west-2", "us-east-1"]


def assume_role(aws_account_number, role_name):
    # Beginning the assume role process for account
    sts_client = boto3.client('sts')
    response = sts_client.assume_role(
        RoleArn='arn:aws:iam::{}:role/{}'.format(
            aws_account_number,
            role_name
        ),
        RoleSessionName='EnableSecurityHub'
    ) 
    # Storing STS credentials
    session = boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )
    print("Assumed session for {}.".format(
        aws_account_number
    ))
    return session


def get_master_members(sh_client, aws_region):
    """
    Returns a list of current members of the SecurityHub master account
    :param aws_region: AWS Region of the SecurityHub master account
    :param detector_id: DetectorId of the SecurityHub master account in the AWS Region
    :return: dict of AwsAccountId:RelationshipStatus
    """
    member_dict = dict()
    results = sh_client.list_members(
        OnlyAssociated=False
    )
    for member in results['Members']:
        member_dict.update({member['AccountId']: member['MemberStatus']})
    while results.get("NextToken"):
        results = sh_client.list_members(
            OnlyAssociated=False,
            NextToken=results['NextToken']
        )
        for member in results['Members']:
            member_dict.update({member['AccountId']: member['MemberStatus']})
    return member_dict


def get_all_accounts(org_client):
    iterator = org_client.get_paginator("list_accounts").paginate()
    accounts = []
    for page in iterator:
        for account in page["Accounts"]:
            accounts.append(account["Id"])
    return accounts


def lambda_handler(event, context):
    org_client = boto3.client("organizations")
    all_org_accounts = get_all_accounts(org_client)
    print(all_org_accounts)

    # Get the current Security Hub Members
    securityhub_client = boto3.client("securityhub")
    for region in SUPPORTED_REGIONS:
        member_accounts = get_master_members(securityhub_client, region)
        print(f"Security Hub Member accounts in region {region}")
        print(member_accounts)
