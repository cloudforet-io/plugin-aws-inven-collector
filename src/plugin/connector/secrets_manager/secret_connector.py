from plugin.connector.base import ResourceConnector


class SecretConnector(ResourceConnector):
    service_name = "secretsmanager"
    cloud_service_group = "SecretsManager"
    cloud_service_type = "Secret"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "secretsmanager"
        self.cloud_service_group = "SecretsManager"
        self.cloud_service_type = "Secret"
        self.rest_service_name = "secretsmanager"

    def list_secrets(self):
        paginator = self.client.get_paginator("list_secrets")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_secret(self, secret_id):
        response = self.client.describe_secret(SecretId=secret_id)
        return response

    def get_secret_value(self, secret_id):
        response = self.client.get_secret_value(SecretId=secret_id)
        return response
