from plugin.connector.base import ResourceConnector


class LAGConnector(ResourceConnector):
    service_name = "directconnect"
    cloud_service_group = "DirectConnect"
    cloud_service_type = "LAG"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "directconnect"
        self.cloud_service_type = "LAG"
        self.cloud_service_group = "DirectConnect"
        self.rest_service_name = "directconnect"

    def get_lags(self):
        return self.client.describe_lags()
