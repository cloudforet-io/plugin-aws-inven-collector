from plugin.connector.base import ResourceConnector


class DistributionConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "Distribution"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Distribution"
        self.rest_service_name = "lightsail"

    def get_distributions(self):
        response = self.client.get_distributions()
        return response.get("distributions", [])

    def get_distribution(self, distribution_name):
        response = self.client.get_distribution(distributionName=distribution_name)
        return response.get("distribution", {})

    def get_distribution_latest_cache_reset(self, distribution_name):
        response = self.client.get_distribution_latest_cache_reset(
            distributionName=distribution_name
        )
        return response.get("createTime", {})
