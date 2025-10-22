from plugin.connector.base import ResourceConnector


class ClusterConnector(ResourceConnector):
    service_name = "eks"
    cloud_service_group = "EKS"
    cloud_service_type = "Cluster"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "eks"
        self.cloud_service_group = "EKS"
        self.cloud_service_type = "Cluster"
        self.rest_service_name = "eks"

    def list_clusters(self):
        paginator = self.client.get_paginator("list_clusters")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_cluster(self, cluster_name):
        response = self.client.describe_cluster(name=cluster_name)
        return response.get("cluster", {})
