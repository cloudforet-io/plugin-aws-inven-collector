from plugin.connector.base import ResourceConnector


class TrailsConnector(ResourceConnector):
    service_name = "cloudtrail"
    cloud_service_group = "CloudTrail"
    cloud_service_type = "Trail"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "cloudtrail"
        self.cloud_service_type = "Trail"
        self.cloud_service_group = "CloudTrail"
        self.rest_service_name = "cloudtrail"

    def get_trails(self):
        return self.client.describe_trails()

    def get_event_selectors(self, trail_arn):
        return self.client.get_event_selectors(TrailName=trail_arn)

    def get_insight_selectors(self, trail_name):
        return self.client.get_insight_selectors(TrailName=trail_name)
