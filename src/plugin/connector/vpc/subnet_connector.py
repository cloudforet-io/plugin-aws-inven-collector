from plugin.connector.base import ResourceConnector


class SubnetConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "Subnet"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "Subnet"
        self.rest_service_name = "ec2"

    def describe_subnets(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_subnets(Filters=filters)
        return response.get("Subnets", [])

    def describe_subnet_attribute(self, subnet_id, attribute):
        response = self.client.describe_subnet_attribute(
            SubnetId=subnet_id, Attribute=attribute
        )
        return response
