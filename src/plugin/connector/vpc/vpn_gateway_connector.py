from plugin.connector.base import ResourceConnector


class VPNGatewayConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "VPNGateway"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "VPNGateway"
        self.rest_service_name = "ec2"

    def describe_vpn_gateways(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_vpn_gateways(Filters=filters)
        return response.get("VpnGateways", [])

    def describe_vpn_gateway_attribute(self, vpn_gateway_id, attribute):
        response = self.client.describe_vpn_gateway_attribute(
            VpnGatewayId=vpn_gateway_id, Attribute=attribute
        )
        return response
