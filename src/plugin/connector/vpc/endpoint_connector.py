from plugin.connector.base import ResourceConnector


class EndpointConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "Endpoint"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "Endpoint"
        self.rest_service_name = "ec2"

    def describe_vpc_endpoints(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_vpc_endpoints(Filters=filters)
        return response.get("VpcEndpoints", [])

    def describe_vpc_endpoint_services(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_vpc_endpoint_services(Filters=filters)
        return response.get("ServiceDetails", [])
