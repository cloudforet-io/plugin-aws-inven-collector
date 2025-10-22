from plugin.connector.base import ResourceConnector


class UserConnector(ResourceConnector):
    service_name = "iam"
    cloud_service_group = "IAM"
    cloud_service_type = "User"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "iam"
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "User"
        self.rest_service_name = "iam"

    def list_users(self):
        paginator = self.client.get_paginator("list_users")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_user(self, user_name):
        response = self.client.get_user(UserName=user_name)
        return response.get("User", {})

    def list_mfa_devices(self, user_name):
        response = self.client.list_mfa_devices(UserName=user_name)
        return response.get("MFADevices", [])

    def list_groups_for_user(self, user_name):
        paginator = self.client.get_paginator("list_groups_for_user")
        response_iterator = paginator.paginate(
            UserName=user_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_attached_user_policies(self, user_name):
        response = self.client.list_attached_user_policies(UserName=user_name)
        return response.get("AttachedPolicies", [])

    def list_user_policies(self, user_name):
        response = self.client.list_user_policies(UserName=user_name)
        return response.get("PolicyNames", [])
