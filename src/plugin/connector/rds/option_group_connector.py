from plugin.connector.base import ResourceConnector


class OptionGroupConnector(ResourceConnector):
    service_name = "rds"
    cloud_service_group = "RDS"
    cloud_service_type = "OptionGroup"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "rds"
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "OptionGroup"
        self.rest_service_name = "rds"

    def describe_option_groups(self):
        paginator = self.client.get_paginator("describe_option_groups")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_option_group_options(self, engine_name):
        paginator = self.client.get_paginator("describe_option_group_options")
        response_iterator = paginator.paginate(
            EngineName=engine_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_tags_for_resource(self, resource_arn):
        response = self.client.list_tags_for_resource(ResourceName=resource_arn)
        return response.get("TagList", [])
