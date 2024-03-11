from plugin.conf.cloud_service_conf import BOTO3_HTTPS_VERIFIED
from plugin.connector.base import ResourceConnector


class APIGatewayConnector(ResourceConnector):
    service_name = "apigateway"
    cloud_service_group = "APIGateway"
    cloud_service_type = "API"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "apigateway"
        self.cloud_service_type = "API"
        self.cloud_service_group = "APIGateway"
        self.rest_service_name = "apigateway"

    def get_rest_apis(self):
        paginator = self.client.get_paginator("get_rest_apis")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_apis(self):
        self.rest_service_name = "apigatewayv2"
        temp_client = self.session.client(
            self.rest_service_name, verify=BOTO3_HTTPS_VERIFIED
        )
        paginator = temp_client.get_paginator("get_apis")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_rest_resources(self, rest_api_id):
        self.rest_service_name = "apigateway"
        return self.client.get_resources(restApiId=rest_api_id, limit=500)
