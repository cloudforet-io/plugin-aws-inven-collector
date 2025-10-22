from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import VPNGateway


class VPNGatewayManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "VPNGateway"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "VPNGateway"
        self.metadata_path = "metadata/vpc/vpn_gateway.yaml"

    def create_cloud_service_type(self):
        result = []
        vpn_gateway_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonVPC",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-vpc.svg"
            },
            labels=["Networking"],
        )
        result.append(vpn_gateway_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_vpn_gateways(options, region)

    def _collect_vpn_gateways(self, options, region):
        region_name = region

        try:
            vpn_gateways, account_id = self.connector.list_vpc_vpn_gateways()

            for vpn_gateway in vpn_gateways:
                try:
                    vpn_gateway_id = vpn_gateway.get("VpnGatewayId")

                    # Get VPN gateway tags
                    tags = self._get_vpn_gateway_tags(vpn_gateway_id)

                    vpn_gateway_data = {
                        "vpn_gateway_id": vpn_gateway_id,
                        "state": vpn_gateway.get("State", ""),
                        "type": vpn_gateway.get("Type", ""),
                        "availability_zone": vpn_gateway.get("AvailabilityZone", ""),
                        "vpc_attachments": vpn_gateway.get("VpcAttachments", []),
                        "amazon_side_asn": vpn_gateway.get("AmazonSideAsn", 0),
                        "tags": vpn_gateway.get("Tags", []),
                    }

                    vpn_gateway_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                vpn_gateway_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                vpn_gateway_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#VPNGateways:search={vpn_gateway_id}"
                    resource_id = vpn_gateway_id
                    reference = self.get_reference(resource_id, link)

                    vpn_gateway_vo = VPNGateway(vpn_gateway_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=vpn_gateway_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=vpn_gateway_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=vpn_gateway_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_vpn_gateways] [{vpn_gateway.get("VpnGatewayId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_vpn_gateways] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_vpn_gateway_tags(self, vpn_gateway_id):
        """Get VPN gateway tags"""
        try:
            return self.connector.get_vpn_gateway_tags(vpn_gateway_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for VPN gateway {vpn_gateway_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
