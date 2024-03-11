from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *


class VirtualPrivateGatewayManager(ResourceManager):
    cloud_service_group = "DirectConnect"
    cloud_service_type = "VirtualPrivateGateway"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DirectConnect"
        self.cloud_service_type = "VirtualPrivateGateway"
        self.metadata_path = "metadata/direct_connect/virtual_private_gateway.yaml"

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
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
        results = self.connector.get_private_virtual_gateways()
        account_id = self.connector.get_account_id()
        for raw in results.get("virtualGateways", []):
            try:
                raw.update(
                    {
                        "cloudtrail": self.set_cloudtrail(
                            region, None, raw["virtualGatewayId"]
                        )
                    }
                )
                virtual_private_gw_vo = raw
                gateway_id = virtual_private_gw_vo.get("virtualGatewayId", "")
                owner_account = virtual_private_gw_vo.get("ownerAccount", "")
                link = f"https://console.aws.amazon.com/directconnect/v2/home?region={region}#/virtual-gateways/arn:aws:ec2:{region}:{owner_account}:{gateway_id}"
                reference = self.get_reference(gateway_id, link)

                # yield {"data": virtual_private_gw_vo, "account": self.account_id}
                cloud_service = make_cloud_service(
                    name="VirtualPrivateGateway",
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=virtual_private_gw_vo,
                    account=account_id,
                    reference=reference,
                    region_code=region,
                )
                yield cloud_service

            except Exception as e:
                # resource_id = raw.get('connectionId', '')
                yield make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=self.cloud_service_type,
                    region_name=region,
                )
