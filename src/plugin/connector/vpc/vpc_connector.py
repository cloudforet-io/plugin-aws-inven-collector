from plugin.connector.base import ResourceConnector


class VPCConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "VPC"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "VPC"
        self.rest_service_name = "ec2"

    def list_vpcs(self, include_default=False):
        _filter_value = ["false"]
        if include_default:
            _filter_value.append("true")

        paginator = self.client.get_paginator("describe_vpcs")
        response_iterator = paginator.paginate(
            Filters=[{"Name": "isDefault", "Values": _filter_value}],
            PaginationConfig={"MaxItems": 10000},
        )
        return response_iterator

    def describe_vpc_attribute(self, vpc_id, attribute):
        response = self.client.describe_vpc_attribute(VpcId=vpc_id, Attribute=attribute)
        return response
