from plugin.connector.base import ResourceConnector


class SubnetGroupConnector(ResourceConnector):
    service_name = "rds"
    cloud_service_group = "RDS"
    cloud_service_type = "SubnetGroup"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "rds"
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "SubnetGroup"
        self.rest_service_name = "rds"

    def describe_db_subnet_groups(self):
        paginator = self.client.get_paginator("describe_db_subnet_groups")
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
