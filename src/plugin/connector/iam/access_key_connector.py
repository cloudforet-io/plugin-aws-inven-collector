from plugin.connector.base import ResourceConnector


class AccessKeyConnector(ResourceConnector):
    service_name = "iam"
    cloud_service_group = "IAM"
    cloud_service_type = "AccessKey"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "iam"
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "AccessKey"
        self.rest_service_name = "iam"

    def list_access_keys(self, user_name):
        paginator = self.client.get_paginator("list_access_keys")
        response_iterator = paginator.paginate(
            UserName=user_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def get_access_key_last_used(self, access_key_id):
        response = self.client.get_access_key_last_used(AccessKeyId=access_key_id)
        return response.get("AccessKeyLastUsed", {})
