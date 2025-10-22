from plugin.connector.base import ResourceConnector


class ClusterConnector(ResourceConnector):
    service_name = "ecs"
    cloud_service_group = "ECS"
    cloud_service_type = "Cluster"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ecs"
        self.cloud_service_group = "ECS"
        self.cloud_service_type = "Cluster"
        self.rest_service_name = "ecs"

    def list_clusters(self):
        paginator = self.client.get_paginator("list_clusters")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_clusters(self, cluster_arns):
        response = self.client.describe_clusters(clusters=cluster_arns)
        return response.get("clusters", [])

    def list_services(self, cluster_arn):
        paginator = self.client.get_paginator("list_services")
        response_iterator = paginator.paginate(
            cluster=cluster_arn,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_tasks(self, cluster_arn):
        paginator = self.client.get_paginator("list_tasks")
        response_iterator = paginator.paginate(
            cluster=cluster_arn,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_container_instances(self, cluster_arn):
        paginator = self.client.get_paginator("list_container_instances")
        response_iterator = paginator.paginate(
            cluster=cluster_arn,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator
