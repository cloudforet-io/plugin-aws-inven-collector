from spaceone.core.utils import *
from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *


class WebSocketManager(ResourceManager):
    cloud_service_group = "APIGateway"
    cloud_service_type = "API"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "APIGateway"
        self.cloud_service_type = "API"
        self.metadata_path = "metadata/api_gateway/websocket.yaml"

    # def create_cloud_service_type(self):
    #     return make_cloud_service_type(
    #         name=self.cloud_service_type,
    #         group=self.cloud_service_group,
    #         provider=self.provider,
    #         metadata_path=self.metadata_path,
    #         is_primary=True,
    #         is_major=True,
    #         service_code="AmazonApiGateway",
    #         tags={"spaceone:icon": f"{ASSET_URL}/Amazon-API-Gateway.svg"},
    #         labels=["Networking"],
    #     )

    def create_cloud_service(self, region, options, secret_data, schema):
        self.cloud_service_type = "API"
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
                    # yield {
                    #     "data": http_websocket_vo,
                    #     "name": http_websocket_vo.name,
                    #     "instance_type": http_websocket_vo.protocol,
                    #     "account": self.account_id,
                    #     "tags": raw.get("Tags", {}),
                    #     "launched_at": self.datetime_to_iso8601(
                    #         http_websocket_vo.created_date
                    #     ),
                    # }

                except Exception as e:
                    # resource_id = raw.get("ApiId", "")
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
