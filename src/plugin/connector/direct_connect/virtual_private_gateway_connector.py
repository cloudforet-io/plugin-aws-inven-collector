from plugin.connector.base import ResourceConnector


class VirtualPrivateGatewayConnector(ResourceConnector):
    service_name = "directconnect"
    cloud_service_group = "DirectConnect"
    cloud_service_type = "VirtualPrivateGateway"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "directconnect"
        self.cloud_service_type = "VirtualPrivateGateway"
        self.cloud_service_group = "DirectConnect"
        self.rest_service_name = "directconnect"

    def get_private_virtual_gateways(self):
        return self.client.describe_virtual_gateways()
