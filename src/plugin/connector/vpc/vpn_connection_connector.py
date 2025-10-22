from plugin.connector.base import ResourceConnector


class VPNConnectionConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "VPNConnection"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "VPNConnection"
        self.rest_service_name = "ec2"

    def describe_vpn_connections(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_vpn_connections(Filters=filters)
        return response.get("VpnConnections", [])

    def describe_vpn_connection_attribute(self, vpn_connection_id, attribute):
        response = self.client.describe_vpn_connection_attribute(
            VpnConnectionId=vpn_connection_id, Attribute=attribute
        )
        return response
