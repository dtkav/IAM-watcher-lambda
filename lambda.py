from __future__ import print_function

import json
import urllib2
import boto3
from io import BytesIO
from gzip import GzipFile

print('Loading function')

s3 = boto3.client('s3')

# NOTE change these to configure slack integration
SLACK_HOOK = "https://hooks.slack.com/services/<asdf>/<asdf>/<asdf>"  # change me
SLACK_CHANNEL = "general"  # change me
SLACK_USER = "trails"  # change me
SLACK_ICON = ":shield:"

ACCEPT = ["iam.amazonaws.com"]
WATCHLIST_OK = [
    "DeactivateMFADevice",
    "DeleteAccessKey",
    "DeleteAccountAlias",
    "DeleteAccountPasswordPolicy",
    "DeleteGroup",
    "DeleteGroupPolicy",
    "DeleteInstanceProfile",
    "DeleteLoginProfile",
    "DeleteOpenIDConnectProvider",
    "DeletePolicy",
    "DeletePolicyVersion",
    "DeleteRole",
    "DeleteRolePolicy",
    "DeleteSAMLProvider",
    "DeleteServerCertificate",
    "DeleteServiceSpecificCredential",
    "DeleteSigningCertificate",
    "DeleteSSHPublicKey",
    "DeleteUser",
    "DeleteUserPolicy",
    "DeleteVirtualMFADevice",
    "DetachGroupPolicy",
    "DetachRolePolicy",
    "DetachUserPolicy",
    "RemoveClientIDFromOpenIDConnectProvider",
    "RemoveRoleFromInstanceProfile",
    "RemoveUserFromGroup"
]
WATCHLIST_WARN = [
    "AddUserToGroup",
    "AttachGroupPolicy",
    "AttachRolePolicy",
    "AttachUserPolicy",
    "ChangePassword",
    "CreateAccessKey",
    "CreateAccountAlias",
    "CreateGroup",
    "CreateInstanceProfile",
    "CreateLoginProfile",
    "CreateOpenIDConnectProvider",
    "CreatePolicy",
    "CreatePolicyVersion",
    "CreateRole",
    "CreateSAMLProvider",
    "CreateServiceLinkedRole",
    "CreateServiceSpecificCredential",
    "CreateUser",
    "CreateVirtualMFADevice",
    "PutGroupPolicy",
    "PutRolePolicy",
    "PutUserPolicy",
    "UpdateAccessKey",
    "UpdateAccountPasswordPolicy",
    "UpdateAssumeRolePolicy",
    "UpdateGroup",
    "UpdateLoginProfile",
    "UpdateOpenIDConnectProviderThumbprint",
    "UpdateRoleDescription",
    "UpdateSAMLProvider",
    "UpdateServerCertificate",
    "UpdateServiceSpecificCredential",
    "UpdateSigningCertificate",
    "UpdateSSHPublicKey",
    "UpdateUser",
    "UploadServerCertificate",
    "UploadSigningCertificate",
    "UploadSSHPublicKey"
]
WATCHLIST_IGNORE = [
    "AddClientIDToOpenIDConnectProvider",
    "AddRoleToInstanceProfile",
    "EnableMFADevice",
    "GenerateCredentialReport",
    "GetAccessKeyLastUsed",
    "GetAccountAuthorizationDetails",
    "GetAccountPasswordPolicy",
    "GetAccountSummary",
    "GetContextKeysForCustomPolicy",
    "GetContextKeysForPrincipalPolicy",
    "GetCredentialReport",
    "GetGroup",
    "GetGroupPolicy",
    "GetInstanceProfile",
    "GetLoginProfile",
    "GetOpenIDConnectProvider",
    "GetPolicy",
    "GetPolicyVersion",
    "GetRole",
    "GetRolePolicy",
    "GetSAMLProvider",
    "GetServerCertificate",
    "GetSSHPublicKey",
    "GetUser",
    "GetUserPolicy",
    "ListAccessKeys",
    "ListAccountAliases",
    "ListAttachedGroupPolicies",
    "ListAttachedRolePolicies",
    "ListAttachedUserPolicies",
    "ListEntitiesForPolicy",
    "ListGroupPolicies",
    "ListGroups",
    "ListGroupsForUser",
    "ListInstanceProfiles",
    "ListInstanceProfilesForRole",
    "ListMFADevices",
    "ListOpenIDConnectProviders",
    "ListPolicies",
    "ListPolicyVersions",
    "ListRolePolicies",
    "ListRoles",
    "ListSAMLProviders",
    "ListServerCertificates",
    "ListServiceSpecificCredentials",
    "ListSigningCertificates",
    "ListSSHPublicKeys",
    "ListUserPolicies",
    "ListUsers",
    "ListVirtualMFADevices",
    "ResetServiceSpecificCredential",
    "ResyncMFADevice",
    "SetDefaultPolicyVersion",
    "SimulateCustomPolicy",
    "SimulatePrincipalPolicy"
]

WATCHLIST = WATCHLIST_OK + WATCHLIST_WARN


def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    print(message)
    ev = json.loads(message)
    bucket = ev["s3Bucket"]
    for key in ev["s3ObjectKey"]:
        print("getting " + key)
        response = s3.get_object(Bucket=bucket, Key=key)
        bytestream = BytesIO(response['Body'].read())
        body = GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')
        j = json.loads(body)
        attachments = []
        for record in j["Records"]:
            if record["eventSource"] in ACCEPT:
                if record["eventName"] not in WATCHLIST:
                    continue
                print("found IAM change in log " + key)

                attachment = {
                    "author_name": record["userIdentity"]["arn"],
                    "title": record["eventName"],
                    "fields": [
                        {"title": k, "value": v, "short": True}
                        for k, v
                        in record["requestParameters"].iteritems()
                    ],
                    "color": "ok" if record["eventName"] in WATCHLIST_OK else "warning"
                }
                attachments.append(attachment)
        if attachments:
            if len(attachments) > 20:
                print("warning! too many attachments")
            data = {
                "channel": SLACK_CHANNEL,
                "username": SLACK_USER,
                "icon_emoji": SLACK_ICON,
                "attachments": attachments
            }
            print(json.dumps(data, indent=2))
            headers = {"Content-Type": "application/json"}
            payload = json.dumps(data)
            req = urllib2.Request(SLACK_HOOK, payload, headers)
            try:
                urllib2.urlopen(req)
            except urllib2.HTTPError as e:
                print(e)
                print(e.read())
    return message
