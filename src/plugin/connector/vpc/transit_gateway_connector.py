from plugin.connector.base import ResourceConnector


class TransitGatewayConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "TransitGateway"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "TransitGateway"
        self.rest_service_name = "ec2"

    def describe_transit_gateways(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_transit_gateways(Filters=filters)
        return response.get("TransitGateways", [])

    def describe_transit_gateway_attachments(self, filters=None):
        if filters is None:
            filters = []
        paginator = self.client.get_paginator("describe_transit_gateway_attachments")
        response_iterator = paginator.paginate(
            Filters=filters,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def describe_transit_gateway_route_tables(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_transit_gateway_route_tables(Filters=filters)
        return response.get("TransitGatewayRouteTables", [])
