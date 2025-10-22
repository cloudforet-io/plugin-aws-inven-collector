from plugin.connector.base import ResourceConnector


class SnapshotConnector(ResourceConnector):
    service_name = "rds"
    cloud_service_group = "RDS"
    cloud_service_type = "Snapshot"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "rds"
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "Snapshot"
        self.rest_service_name = "rds"

    def describe_db_snapshots(self):
        paginator = self.client.get_paginator("describe_db_snapshots")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_db_cluster_snapshots(self):
        paginator = self.client.get_paginator("describe_db_cluster_snapshots")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def list_tags_for_resource(self, resource_arn):
        response = self.client.list_tags_for_resource(ResourceName=resource_arn)
        return response.get("TagList", [])
