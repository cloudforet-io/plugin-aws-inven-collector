from plugin.connector.base import ResourceConnector


class ContainerConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "Container"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Container"
        self.rest_service_name = "lightsail"

    def get_container_services(self):
        response = self.client.get_container_services()
        return response.get("containerServices", [])

    def get_container_service(self, service_name):
        response = self.client.get_container_service(serviceName=service_name)
        return response.get("containerService", {})

    def get_container_service_deployments(self, service_name):
        response = self.client.get_container_service_deployments(
            serviceName=service_name
        )
        return response.get("deployments", [])
