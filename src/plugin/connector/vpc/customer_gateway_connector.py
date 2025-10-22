from plugin.connector.base import ResourceConnector


class CustomerGatewayConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "CustomerGateway"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "CustomerGateway"
        self.rest_service_name = "ec2"

    def describe_customer_gateways(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_customer_gateways(Filters=filters)
        return response.get("CustomerGateways", [])
