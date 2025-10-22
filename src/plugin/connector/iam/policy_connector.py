from plugin.connector.base import ResourceConnector


class PolicyConnector(ResourceConnector):
    service_name = "iam"
    cloud_service_group = "IAM"
    cloud_service_type = "Policy"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "iam"
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "Policy"
        self.rest_service_name = "iam"

    def list_policies(self):
        paginator = self.client.get_paginator("list_policies")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_policy(self, policy_arn):
        response = self.client.get_policy(PolicyArn=policy_arn)
        return response.get("Policy", {})

    def list_policy_versions(self, policy_arn):
        paginator = self.client.get_paginator("list_policy_versions")
        response_iterator = paginator.paginate(
            PolicyArn=policy_arn,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def get_policy_version(self, policy_arn, version_id):
        response = self.client.get_policy_version(
            PolicyArn=policy_arn, VersionId=version_id
        )
        return response.get("PolicyVersion", {})

    def list_entities_for_policy(self, policy_arn):
        paginator = self.client.get_paginator("list_entities_for_policy")
        response_iterator = paginator.paginate(
            PolicyArn=policy_arn,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator
