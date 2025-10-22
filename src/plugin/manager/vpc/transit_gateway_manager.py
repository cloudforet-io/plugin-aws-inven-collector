from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import TransitGateway


class TransitGatewayManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "TransitGateway"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "TransitGateway"
        self.metadata_path = "metadata/vpc/transit_gateway.yaml"

    def create_cloud_service_type(self):
        result = []
        transit_gateway_cst_result = make_cloud_service_type(
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
        result.append(transit_gateway_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_transit_gateways(options, region)

    def _collect_transit_gateways(self, options, region):
        region_name = region

        try:
            transit_gateways, account_id = self.connector.list_vpc_transit_gateways()

            for transit_gateway in transit_gateways:
                try:
                    transit_gateway_id = transit_gateway.get("TransitGatewayId")

                    # Get transit gateway tags
                    tags = self._get_transit_gateway_tags(transit_gateway_id)

                    # Get transit gateway attachments
                    attachments = self._get_transit_gateway_attachments(
                        transit_gateway_id
                    )

                    transit_gateway_data = {
                        "transit_gateway_id": transit_gateway_id,
                        "transit_gateway_arn": transit_gateway.get(
                            "TransitGatewayArn", ""
                        ),
                        "state": transit_gateway.get("State", ""),
                        "owner_id": transit_gateway.get("OwnerId", ""),
                        "description": transit_gateway.get("Description", ""),
                        "creation_time": transit_gateway.get("CreationTime"),
                        "options": transit_gateway.get("Options", {}),
                        "tags": transit_gateway.get("Tags", []),
                        "attachments": attachments,
                    }

                    transit_gateway_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                transit_gateway_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                transit_gateway_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#TransitGateways:search={transit_gateway_id}"
                    resource_id = transit_gateway_id
                    reference = self.get_reference(resource_id, link)

                    transit_gateway_vo = TransitGateway(
                        transit_gateway_data, strict=False
                    )
                    cloud_service = make_cloud_service(
                        name=transit_gateway_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=transit_gateway_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=transit_gateway_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_transit_gateways] [{transit_gateway.get("TransitGatewayId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_transit_gateways] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_transit_gateway_tags(self, transit_gateway_id):
        """Get transit gateway tags"""
        try:
            return self.connector.get_transit_gateway_tags(transit_gateway_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for transit gateway {transit_gateway_id}: {e}"
            )
            return []

    def _get_transit_gateway_attachments(self, transit_gateway_id):
        """Get transit gateway attachments"""
        try:
            return self.connector.get_transit_gateway_attachments(transit_gateway_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get attachments for transit gateway {transit_gateway_id}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
