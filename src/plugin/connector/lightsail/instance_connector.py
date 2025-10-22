from plugin.connector.base import ResourceConnector


class InstanceConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "Instance"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Instance"
        self.rest_service_name = "lightsail"

    def get_instances(self):
        paginator = self.client.get_paginator("get_instances")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_instance(self, instance_name):
        response = self.client.get_instance(instanceName=instance_name)
        return response.get("instance", {})

    def get_instance_access_details(self, instance_name, protocol):
        response = self.client.get_instance_access_details(
            instanceName=instance_name, protocol=protocol
        )
        return response
