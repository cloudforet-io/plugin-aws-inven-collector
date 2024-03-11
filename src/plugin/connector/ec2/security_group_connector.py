from plugin.connector.base import ResourceConnector


class SecurityGroupConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "EC2"
    cloud_service_type = "SecurityGroup"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_type = "SecurityGroup"
        self.rest_service_name = "ec2"

    def get_security_groups(self):
        paginator = self.client.get_paginator("describe_security_groups")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_filtered_instances(self, filters):
        paginator = self.client.get_paginator("describe_instances")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
            Filters=filters,
        )
        return response_iterator

    def describe_vpcs(self):
        return self.client.describe_vpcs()
