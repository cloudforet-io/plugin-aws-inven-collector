from plugin.connector.base import ResourceConnector


class VolumeConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "EC2"
    cloud_service_type = "Volume"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "Volume"
        self.rest_service_name = "ec2"

    def get_volumes(self):
        paginator = self.client.get_paginator("describe_volumes")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_volume_attribute(self, volume_id, attribute):
        return self.client.describe_volume_attribute(
            Attribute=attribute, VolumeId=volume_id
        )
