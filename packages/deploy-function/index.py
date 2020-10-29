import time
import os
import json
import boto3


MASTER_ACCOUNT = os.environ["MASTER_ACCOUNT"]
SUPPORTED_REGIONS = ["eu-west-1", "eu-west-2", "us-east-1"]
TARGET_ROLE = os.environ["TARGET_ROLE"]


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


def lambda_handler(event, context):

    master_securityhub_client = {}
    member_accounts = {}

    # Get the current Security Hub Members
    for region in SUPPORTED_REGIONS:
        master_securityhub_client[region] = boto3.client("securityhub", region)
        member_accounts[region] = get_master_members(master_securityhub_client[region], region)
        print(f"Security Hub Member accounts in region {region}")
        print(member_accounts)

    print(event)
    account_id = event["Id"]
    for region in SUPPORTED_REGIONS:
        print(region)
        master_securityhub_client[region].create_members(
            AccountDetails=[
                {
                    "AccountId": account_id,
                    "Email": event["Email"]
                }
            ]
        )

        start_time = int(time.time())
        while account_id not in member_accounts[region]:
            if (int(time.time()) - start_time) > 300:
                print("Membership did not show up for account {}, skipping".format(event))
                break
            time.sleep(5)
            member_accounts[region] = get_master_members(
                master_securityhub_client[region],
                region
            )

        start_time = int(time.time())
        while member_accounts[region][account_id] != "Associated":
            if (int(time.time()) - start_time) > 300:
                print("Invitation did not show up for account {}, skipping".format(account))
                break

            if member_accounts[region][account_id] == "Created":
                master_securityhub_client[region].invite_members(
                    AccountIds=[account_id]
                )
                print(f"Invited account {account_id} in region {region}")

            if member_accounts[region][account_id] == "Invited":
                target_session = assume_role(account_id, TARGET_ROLE)
                sh_client = target_session.client("securityhub", region)
                response = sh_client.list_invitations()
                invitation_id = None
                for invitation in response['Invitations']:
                    invitation_id = invitation['InvitationId']

                if invitation_id is not None:
                    sh_client.accept_invitation(
                        InvitationId=invitation_id,
                        MasterId=str(MASTER_ACCOUNT)
                    )
                    print(f"Accepting Account {account_id} to SecurityHub master in region {region}")

            member_accounts[region] = get_master_members(
                master_securityhub_client[region],
                region
            )
