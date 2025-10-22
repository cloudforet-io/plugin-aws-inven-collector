from plugin.connector.base import ResourceConnector


class NodeGroupConnector(ResourceConnector):
    service_name = "eks"
    cloud_service_group = "EKS"
    cloud_service_type = "NodeGroup"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "eks"
        self.cloud_service_group = "EKS"
        self.cloud_service_type = "NodeGroup"
        self.rest_service_name = "eks"

    def list_nodegroups(self, cluster_name):
        paginator = self.client.get_paginator("list_nodegroups")
        response_iterator = paginator.paginate(
            clusterName=cluster_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def describe_nodegroup(self, cluster_name, nodegroup_name):
        response = self.client.describe_nodegroup(
            clusterName=cluster_name, nodegroupName=nodegroup_name
        )
        return response.get("nodegroup", {})
