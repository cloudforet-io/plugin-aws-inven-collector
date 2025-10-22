from plugin.connector.base import ResourceConnector


class InstanceConnector(ResourceConnector):
    service_name = "rds"
    cloud_service_group = "RDS"
    cloud_service_type = "Instance"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "rds"
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "Instance"
        self.rest_service_name = "rds"

    def describe_db_instances(self):
        paginator = self.client.get_paginator("describe_db_instances")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_db_clusters(self):
        paginator = self.client.get_paginator("describe_db_clusters")
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
