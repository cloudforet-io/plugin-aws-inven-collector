from plugin.connector.base import ResourceConnector


class GroupConnector(ResourceConnector):
    service_name = "iam"
    cloud_service_group = "IAM"
    cloud_service_type = "Group"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "iam"
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "Group"
        self.rest_service_name = "iam"

    def list_groups(self):
        paginator = self.client.get_paginator("list_groups")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_group(self, group_name):
        response = self.client.get_group(GroupName=group_name)
        return response.get("Group", {})

    def list_users_in_group(self, group_name):
        paginator = self.client.get_paginator("get_group")
        response_iterator = paginator.paginate(
            GroupName=group_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_attached_group_policies(self, group_name):
        paginator = self.client.get_paginator("list_attached_group_policies")
        response_iterator = paginator.paginate(
            GroupName=group_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_group_policies(self, group_name):
        response = self.client.list_group_policies(GroupName=group_name)
        return response.get("PolicyNames", [])
