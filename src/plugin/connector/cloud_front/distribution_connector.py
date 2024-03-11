from plugin.connector.base import ResourceConnector


class DistributionConnector(ResourceConnector):
    service_name = "cloudfront"
    cloud_service_group = "CloudFront"
    cloud_service_type = "Distribution"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "cloudfront"
        self.cloud_service_type = "Distribution"
        self.cloud_service_group = "CloudFront"
        self.rest_service_name = "cloudfront"

    def get_distributions(self):
        paginator = self.client.get_paginator("list_distributions")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def list_tags_for_resource(self, distribution_arn):
        return self.client.list_tags_for_resource(Resource=distribution_arn)
