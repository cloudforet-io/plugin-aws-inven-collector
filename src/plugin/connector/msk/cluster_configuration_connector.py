from plugin.connector.base import ResourceConnector


class ClusterConfigurationConnector(ResourceConnector):
    service_name = "kafka"
    cloud_service_group = "MSK"
    cloud_service_type = "ClusterConfiguration"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "kafka"
        self.cloud_service_group = "MSK"
        self.cloud_service_type = "ClusterConfiguration"
        self.rest_service_name = "kafka"

    def list_configurations(self):
        paginator = self.client.get_paginator("list_configurations")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_configuration(self, arn):
        response = self.client.describe_configuration(Arn=arn)
        return response.get("LatestRevision", {})

    def list_configuration_revisions(self, arn):
        response = self.client.list_configuration_revisions(Arn=arn)
        return response.get("Revisions", [])

    def describe_configuration_revision(self, arn, revision):
        response = self.client.describe_configuration_revision(
            Arn=arn, Revision=revision
        )
        return response
