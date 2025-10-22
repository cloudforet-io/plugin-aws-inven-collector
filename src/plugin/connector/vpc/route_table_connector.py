from plugin.connector.base import ResourceConnector


class RouteTableConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "RouteTable"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "RouteTable"
        self.rest_service_name = "ec2"

    def describe_route_tables(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_route_tables(Filters=filters)
        return response.get("RouteTables", [])

    def describe_route_table_attribute(self, route_table_id, attribute):
        response = self.client.describe_route_table_attribute(
            RouteTableId=route_table_id, Attribute=attribute
        )
        return response
