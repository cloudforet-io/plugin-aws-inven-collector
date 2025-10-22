from plugin.connector.base import ResourceConnector


class KeyConnector(ResourceConnector):
    service_name = "kms"
    cloud_service_group = "KMS"
    cloud_service_type = "Key"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "kms"
        self.cloud_service_group = "KMS"
        self.cloud_service_type = "Key"
        self.rest_service_name = "kms"

    def list_keys(self):
        paginator = self.client.get_paginator("list_keys")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_key(self, key_id):
        response = self.client.describe_key(KeyId=key_id)
        return response.get("KeyMetadata", {})

    def list_aliases(self):
        paginator = self.client.get_paginator("list_aliases")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def list_resource_tags(self, key_id):
        response = self.client.list_resource_tags(KeyId=key_id)
        return response.get("Tags", [])
