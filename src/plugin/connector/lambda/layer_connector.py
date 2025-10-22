from plugin.connector.base import ResourceConnector


class LayerConnector(ResourceConnector):
    service_name = "lambda_model"
    cloud_service_group = "Lambda"
    cloud_service_type = "Layer"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lambda_model"
        self.cloud_service_group = "Lambda"
        self.cloud_service_type = "Layer"
        self.rest_service_name = "lambda_model"

    def list_layers(self):
        paginator = self.client.get_paginator("list_layers")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_layer(self, layer_name, version_number=None):
        if version_number:
            response = self.client.get_layer_version(
                LayerName=layer_name, VersionNumber=version_number
            )
        else:
            response = self.client.get_layer_version(LayerName=layer_name)
        return response

    def list_layer_versions(self, layer_name):
        paginator = self.client.get_paginator("list_layer_versions")
        response_iterator = paginator.paginate(
            LayerName=layer_name,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator
