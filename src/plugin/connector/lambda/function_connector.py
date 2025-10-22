from plugin.connector.base import ResourceConnector


class FunctionConnector(ResourceConnector):
    service_name = "lambda_model"
    cloud_service_group = "Lambda"
    cloud_service_type = "Function"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lambda_model"
        self.cloud_service_group = "Lambda"
        self.cloud_service_type = "Function"
        self.rest_service_name = "lambda_model"

    def list_functions(self):
        paginator = self.client.get_paginator("list_functions")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_function(self, function_name):
        response = self.client.get_function(FunctionName=function_name)
        return response

    def get_function_tags(self, function_name):
        response = self.client.list_tags(Resource=function_name)
        return response.get("Tags", {})

    def get_function_policy(self, function_name):
        response = self.client.get_policy(FunctionName=function_name)
        return response.get("Policy", "")

    def list_function_versions(self, function_name):
        paginator = self.client.get_paginator("list_versions_by_function")
        response_iterator = paginator.paginate(
            FunctionName=function_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator
