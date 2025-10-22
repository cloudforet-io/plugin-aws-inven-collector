from plugin.connector.base import ResourceConnector


class StaticIPConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "StaticIP"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "StaticIP"
        self.rest_service_name = "lightsail"

    def get_static_ips(self):
        paginator = self.client.get_paginator("get_static_ips")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_static_ip(self, static_ip_name):
        response = self.client.get_static_ip(staticIpName=static_ip_name)
        return response.get("staticIp", {})
