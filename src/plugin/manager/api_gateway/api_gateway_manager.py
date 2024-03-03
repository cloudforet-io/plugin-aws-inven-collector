from ..base import ResourceManager
from ...conf.cloud_service_conf import *
from spaceone.core.utils import *
from spaceone.inventory.plugin.collector.lib import *


class ApiGatewayManager(ResourceManager):
    cloud_service_group = "APIGateway"
    cloud_service_type = "API"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "APIGateway"
        self.cloud_service_type = "API"
        self.metadata_path = "metadata/api_gateway/api_gateway.yaml"

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonApiGateway",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-API-Gateway.svg"},
            labels=["Networking"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        collect_list = [
            self._collect_rest_apis,
            self._collect_websockets,
        ]
        self.connector.set_account_id()
        for pre_collect in collect_list:
            yield from pre_collect(region)

    def _collect_rest_apis(self, region):
        cloudwatch_namespace = "AWS/ApiGateway"
        cloudwatch_dimension_name = "ApiName"
        cloudtrail_resource_type = "AWS::ApiGateway::RestApi"

        results = self.connector.get_rest_apis()
        account_id = self.connector.get_account_id()
        for data in results:
            for raw in data.get("items", []):
                try:
                    _res = self.connector.get_rest_resources(raw.get("id"))
                    # for avoid to API Rate limitation.
                    time.sleep(0.5)

                    raw.update(
                        {
                            "protocol": "REST",
                            "endpoint_type": self.get_endpoint_type(
                                raw.get("endpointConfiguration", {}).get("types")
                            ),
                            "resources": list(
                                map(
                                    lambda _resource_raw: self.set_rest_api_resource(
                                        _resource_raw
                                    ),
                                    _res.get("items", []),
                                )
                            ),
                            "arn": self.generate_arn(
                                service=self.connector.rest_service_name,
                                region=region,
                                account_id="",
                                resource_type="restapis",
                                resource_id=f"{raw.get('id')}/*",
                            ),
                            "cloudwatch": self.set_cloudwatch(
                                cloudwatch_namespace,
                                cloudwatch_dimension_name,
                                raw.get("id"),
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region, cloudtrail_resource_type, raw["id"]
                            ),
                            "launched_at": self.datetime_to_iso8601(
                                raw.get("createdDate")
                            ),
                        }
                    )
                    link = f"https://console.aws.amazon.com/apigateway/home?region={region}#/apis/{raw.get('id')}/resources/"
                    reference = self.get_reference(raw.get("arn"), link)

                    # Converting datetime type attributes to ISO8601 format needed to meet protobuf format
                    self._update_times(raw)

                    rest_api_vo = raw
                    cloud_service = make_cloud_service(
                        name=rest_api_vo.get("name", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=rest_api_vo,
                        instance_type=rest_api_vo.get("protocol"),
                        account=account_id,
                        reference=reference,
                        tags=raw.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    def _collect_websockets(self, region):
        cloudtrail_resource_type = "AWS::ApiGateway::RestApi"
        results = self.connector.get_apis()
        account_id = self.connector.get_account_id()
        for data in results:
            for raw in data.get("Items", []):
                try:
                    raw.update(
                        {
                            "protocol": raw.get("ProtocolType"),
                            "endpoint_type": "Regional",
                            "arn": self.generate_arn(
                                service=self.connector.rest_service_name,
                                region=region,
                                account_id="",
                                resource_type="interface",
                                resource_id=raw.get("ApiId"),
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region, cloudtrail_resource_type, raw["ApiId"]
                            ),
                            "launched_at": self.datetime_to_iso8601(
                                raw.get("CreatedDate")
                            ),
                        }
                    )
                    link = f"https://console.aws.amazon.com/apigateway/home?region={region}#/apis/{raw.get('id')}/routes"
                    reference = self.get_reference(raw.get("arn"), link)

                    # Converting datetime type attributes to ISO8601 format needed to meet protobuf format
                    self._update_times(raw)

                    http_websocket_vo = raw
                    cloud_service = make_cloud_service(
                        name=http_websocket_vo.get("Name", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=http_websocket_vo,
                        instance_type=http_websocket_vo.get("protocol"),
                        account=account_id,
                        reference=reference,
                        tags=raw.get("Tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    def _update_times(self, raw):
        raw.update(
            {
                "CreatedDate": self.datetime_to_iso8601(raw.get("CreatedDate")),
            }
        )

    def set_rest_api_resource(self, resource):
        resource.update(
            {
                "display_methods": self.get_methods_in_resources(
                    resource.get("resourceMethods", {})
                )
            }
        )
        return resource

    @staticmethod
    def get_methods_in_resources(resource_methods):
        return list(map(lambda method: method, resource_methods))

    @staticmethod
    def get_endpoint_type(endpoint_types):
        if endpoint_types:
            return endpoint_types[0]
        else:
            return ""
