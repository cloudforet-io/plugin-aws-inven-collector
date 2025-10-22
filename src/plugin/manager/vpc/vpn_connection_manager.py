from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import VPNConnection


class VPNConnectionManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "VPNConnection"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "VPNConnection"
        self.metadata_path = "metadata/vpc/vpn_connection.yaml"

    def create_cloud_service_type(self):
        result = []
        vpn_connection_cst_result = make_cloud_service_type(
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
        result.append(vpn_connection_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_vpn_connections(options, region)

    def _collect_vpn_connections(self, options, region):
        region_name = region

        try:
            vpn_connections, account_id = self.connector.list_vpc_vpn_connections()

            for vpn_connection in vpn_connections:
                try:
                    vpn_connection_id = vpn_connection.get("VpnConnectionId")

                    # Get VPN connection tags
                    tags = self._get_vpn_connection_tags(vpn_connection_id)

                    vpn_connection_data = {
                        "vpn_connection_id": vpn_connection_id,
                        "state": vpn_connection.get("State", ""),
                        "customer_gateway_id": vpn_connection.get(
                            "CustomerGatewayId", ""
                        ),
                        "customer_gateway_configuration": vpn_connection.get(
                            "CustomerGatewayConfiguration", ""
                        ),
                        "type": vpn_connection.get("Type", ""),
                        "vpn_gateway_id": vpn_connection.get("VpnGatewayId", ""),
                        "transit_gateway_id": vpn_connection.get(
                            "TransitGatewayId", ""
                        ),
                        "options": vpn_connection.get("Options", {}),
                        "routes": vpn_connection.get("Routes", []),
                        "tags": vpn_connection.get("Tags", []),
                    }

                    vpn_connection_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                vpn_connection_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                vpn_connection_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#VPNConnections:search={vpn_connection_id}"
                    resource_id = vpn_connection_id
                    reference = self.get_reference(resource_id, link)

                    vpn_connection_vo = VPNConnection(vpn_connection_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=vpn_connection_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=vpn_connection_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=vpn_connection_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_vpn_connections] [{vpn_connection.get("VpnConnectionId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_vpn_connections] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_vpn_connection_tags(self, vpn_connection_id):
        """Get VPN connection tags"""
        try:
            return self.connector.get_vpn_connection_tags(vpn_connection_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for VPN connection {vpn_connection_id}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
