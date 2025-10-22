from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import NATGateway


class NATGatewayManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "NATGateway"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "NATGateway"
        self.metadata_path = "metadata/vpc/nat_gateway.yaml"

    def create_cloud_service_type(self):
        result = []
        nat_gateway_cst_result = make_cloud_service_type(
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
        result.append(nat_gateway_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_nat_gateways(options, region)

    def _collect_nat_gateways(self, options, region):
        region_name = region

        try:
            nat_gateways, account_id = self.connector.list_vpc_nat_gateways()

            for nat_gateway in nat_gateways:
                try:
                    nat_gateway_id = nat_gateway.get("NatGatewayId")

                    # Get NAT gateway tags
                    tags = self._get_nat_gateway_tags(nat_gateway_id)

                    nat_gateway_data = {
                        "nat_gateway_id": nat_gateway_id,
                        "create_time": nat_gateway.get("CreateTime"),
                        "delete_time": nat_gateway.get("DeleteTime"),
                        "nat_gateway_addresses": nat_gateway.get(
                            "NatGatewayAddresses", []
                        ),
                        "state": nat_gateway.get("State", ""),
                        "subnet_id": nat_gateway.get("SubnetId", ""),
                        "vpc_id": nat_gateway.get("VpcId", ""),
                        "tags": nat_gateway.get("Tags", []),
                        "connectivity_type": nat_gateway.get("ConnectivityType", ""),
                    }

                    nat_gateway_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                nat_gateway_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                nat_gateway_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#NatGateways:search={nat_gateway_id}"
                    resource_id = nat_gateway_id
                    reference = self.get_reference(resource_id, link)

                    nat_gateway_vo = NATGateway(nat_gateway_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=nat_gateway_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=nat_gateway_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=nat_gateway_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_nat_gateways] [{nat_gateway.get("NatGatewayId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_nat_gateways] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_nat_gateway_tags(self, nat_gateway_id):
        """Get NAT gateway tags"""
        try:
            return self.connector.get_nat_gateway_tags(nat_gateway_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for NAT gateway {nat_gateway_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
