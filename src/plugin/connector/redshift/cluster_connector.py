from plugin.connector.base import ResourceConnector


class ClusterConnector(ResourceConnector):
    service_name = "redshift"
    cloud_service_group = "Redshift"
    cloud_service_type = "Cluster"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "redshift"
        self.cloud_service_group = "Redshift"
        self.cloud_service_type = "Cluster"
        self.rest_service_name = "redshift"

    def describe_clusters(self):
        paginator = self.client.get_paginator("describe_clusters")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_cluster(self, cluster_identifier):
        response = self.client.describe_clusters(ClusterIdentifier=cluster_identifier)
        return response.get("Clusters", [{}])[0]

    def list_tags_for_resource(self, resource_name):
        response = self.client.list_tags_for_resource(ResourceName=resource_name)
        return response.get("TagList", [])
