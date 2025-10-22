from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *

from ...model.direct_connect import VirtualPrivateGateway


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
        yield from self._collect_virtual_private_gateways(options, region)

    def _collect_virtual_private_gateways(self, options, region):
        results = self.connector.get_private_virtual_gateways()
        for raw in results.get("virtualGateways", []):
            try:
                raw.update(
                    {
                        "cloudtrail": self.set_cloudtrail(
                            self.cloud_service_group, raw["virtualGatewayId"], region
                        )
                    }
                )
                virtual_private_gw_vo = VirtualPrivateGateway(raw, strict=False)
                gateway_id = virtual_private_gw_vo.get("virtualGatewayId", "")
                owner_account = virtual_private_gw_vo.get("ownerAccount", "")
                link = f"https://console.aws.amazon.com/directconnect/v2/home?region={region}#/virtual-gateways/arn:aws:ec2:{region}:{owner_account}:{gateway_id}"
                reference = self.get_reference(gateway_id, link)

                cloud_service = make_cloud_service(
                    name="VirtualPrivateGateway",
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=virtual_private_gw_vo.to_primitive(),
                    account=options.get("account_id"),
                    reference=reference,
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
