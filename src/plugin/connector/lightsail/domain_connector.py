from plugin.connector.base import ResourceConnector


class DomainConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "Domain"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Domain"
        self.rest_service_name = "lightsail"

    def get_domains(self):
        paginator = self.client.get_paginator("get_domains")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_domain(self, domain_name):
        response = self.client.get_domain(domainName=domain_name)
        return response.get("domain", {})
