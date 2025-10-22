from plugin.connector.base import ResourceConnector


class TargetGroupConnector(ResourceConnector):
    service_name = "elbv2"
    cloud_service_group = "ELB"
    cloud_service_type = "TargetGroup"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "elbv2"
        self.cloud_service_group = "ELB"
        self.cloud_service_type = "TargetGroup"
        self.rest_service_name = "elbv2"

    def describe_target_groups(self):
        paginator = self.client.get_paginator("describe_target_groups")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_target_group_attributes(self, target_group_arn):
        response = self.client.describe_target_group_attributes(
            TargetGroupArn=target_group_arn
        )
        return response.get("Attributes", [])

    def describe_target_health(self, target_group_arn):
        response = self.client.describe_target_health(TargetGroupArn=target_group_arn)
        return response.get("TargetHealthDescriptions", [])
