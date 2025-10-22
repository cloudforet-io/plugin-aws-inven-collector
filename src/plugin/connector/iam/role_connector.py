from plugin.connector.base import ResourceConnector


class RoleConnector(ResourceConnector):
    service_name = "iam"
    cloud_service_group = "IAM"
    cloud_service_type = "Role"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "iam"
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "Role"
        self.rest_service_name = "iam"

    def list_roles(self):
        paginator = self.client.get_paginator("list_roles")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_role(self, role_name):
        response = self.client.get_role(RoleName=role_name)
        return response.get("Role", {})

    def list_attached_role_policies(self, role_name):
        paginator = self.client.get_paginator("list_attached_role_policies")
        response_iterator = paginator.paginate(
            RoleName=role_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_role_policies(self, role_name):
        response = self.client.list_role_policies(RoleName=role_name)
        return response.get("PolicyNames", [])

    def get_role_policy(self, role_name, policy_name):
        response = self.client.get_role_policy(
            RoleName=role_name, PolicyName=policy_name
        )
        return response.get("PolicyDocument", {})
