from plugin.connector.base import ResourceConnector


class HostedZoneConnector(ResourceConnector):
    service_name = "route53"
    cloud_service_group = "Route53"
    cloud_service_type = "HostedZone"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "route53"
        self.cloud_service_group = "Route53"
        self.cloud_service_type = "HostedZone"
        self.rest_service_name = "route53"

    def list_hosted_zones(self):
        paginator = self.client.get_paginator("list_hosted_zones")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_hosted_zone(self, hosted_zone_id):
        response = self.client.get_hosted_zone(Id=hosted_zone_id)
        return response

    def list_resource_record_sets(self, hosted_zone_id):
        paginator = self.client.get_paginator("list_resource_record_sets")
        response_iterator = paginator.paginate(
            HostedZoneId=hosted_zone_id,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def list_tags_for_resource(self, resource_type, resource_id):
        response = self.client.list_tags_for_resource(
            ResourceType=resource_type, ResourceId=resource_id
        )
        return response.get("ResourceTagSet", {}).get("Tags", [])
