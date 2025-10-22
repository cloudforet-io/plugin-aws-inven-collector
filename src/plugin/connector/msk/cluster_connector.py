from plugin.connector.base import ResourceConnector


class ClusterConnector(ResourceConnector):
    service_name = "kafka"
    cloud_service_group = "MSK"
    cloud_service_type = "Cluster"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "kafka"
        self.cloud_service_group = "MSK"
        self.cloud_service_type = "Cluster"
        self.rest_service_name = "kafka"

    def list_clusters(self):
        paginator = self.client.get_paginator("list_clusters")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_cluster(self, cluster_arn):
        response = self.client.describe_cluster(ClusterArn=cluster_arn)
        return response.get("ClusterInfo", {})

    def list_nodes(self, cluster_arn):
        response = self.client.list_nodes(ClusterArn=cluster_arn)
        return response.get("NodeInfoList", [])

    def list_configurations(self):
        response = self.client.list_configurations()
        return response.get("Configurations", [])
