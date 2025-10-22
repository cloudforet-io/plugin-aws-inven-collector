from plugin.connector.base import ResourceConnector


class PeeringConnectionConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "PeeringConnection"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "PeeringConnection"
        self.rest_service_name = "ec2"

    def describe_vpc_peering_connections(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_vpc_peering_connections(Filters=filters)
        return response.get("VpcPeeringConnections", [])

    def describe_vpc_peering_connection_attribute(
        self, vpc_peering_connection_id, attribute
    ):
        response = self.client.describe_vpc_peering_connection_attribute(
            VpcPeeringConnectionId=vpc_peering_connection_id, Attribute=attribute
        )
        return response
