from plugin.connector.base import ResourceConnector


class ConnectConnector(ResourceConnector):
    service_name = "directconnect"
    cloud_service_group = "DirectConnect"
    cloud_service_type = "Connection"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "directconnect"
        self.cloud_service_type = "Connection"
        self.cloud_service_group = "DirectConnect"
        self.rest_service_name = "directconnect"

    def get_connections(self):
        return self.client.describe_connections()
