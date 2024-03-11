from plugin.connector.base import ResourceConnector


class EIPConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "EC2"
    cloud_service_type = "EIP"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_type = "EIP"
        self.rest_service_name = "ec2"

    def get_addresses(self):
        return self.client.describe_addresses()

    def describe_nat_gateways(self):
        return self.client.describe_nat_gateways()

    def describe_network_interfaces(self, network_interface_ids):
        return self.client.describe_network_interfaces(
            NetworkInterfaceIds=network_interface_ids
        )
