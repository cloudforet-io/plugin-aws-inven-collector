from plugin.connector.base import ResourceConnector


class EIPConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "EC2"
    cloud_service_type = "EIP"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "EIP"
        self.rest_service_name = "ec2"

    def describe_addresses(self):
        response = self.client.describe_addresses()
        return response.get("Addresses", [])

    def describe_nat_gateways(self):
        paginator = self.client.get_paginator("describe_nat_gateways")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_network_interfaces(self, network_interface_ids):
        if network_interface_ids:
            response = self.client.describe_network_interfaces(
                NetworkInterfaceIds=network_interface_ids
            )
            return response.get("NetworkInterfaces", [])
        return []
