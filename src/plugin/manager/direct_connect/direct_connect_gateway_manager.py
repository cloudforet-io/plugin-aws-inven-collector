from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *


class DirectConnectGatewayManager(ResourceManager):
    cloud_service_group = "DirectConnect"
    cloud_service_type = "DirectConnectGateway"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DirectConnect"
        self.cloud_service_type = "DirectConnectGateway"
        self.metadata_path = "metadata/direct_connect/direct_connect_gateway.yaml"

    def create_cloud_service_type(self):
        return make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AWSDirectConnect",
            tags={"spaceone:icon": f"{ASSET_URL}/AWS-Direct-Connect.svg"},
            labels=["Networking"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        results = self.connector.get_direct_connect_gateways()
        account_id = self.connector.get_account_id()
        for raw in results.get("directConnectGateways", []):
            try:
                raw.update(
                    {
                        "cloudtrail": self.set_cloudtrail(
                            "us-east-1", None, raw["directConnectGatewayId"]
                        )
                    }
                )
                dc_gw_vo = raw
                gateway_id = dc_gw_vo.get("directConnectGatewayId", "")
                link = f"https://console.aws.amazon.com/directconnect/v2/home?region={region}#/dxgateways/{gateway_id}"
                reference = self.get_reference(gateway_id, link)

                cloud_service = make_cloud_service(
                    name=dc_gw_vo.get("directConnectGatewayName", ""),
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=dc_gw_vo,
                    account=account_id,
                    reference=reference,
                    region_code=region,
                )
                yield cloud_service
                # yield {
                #     "data": dc_gw_vo,
                #     "name": dc_gw_vo.direct_connect_gateway_name,
                #     "account": self.account_id,
                # }

            except Exception as e:
                # resource_id = raw.get('connectionId', '')
                yield make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=self.cloud_service_type,
                    region_name=region,
                )
