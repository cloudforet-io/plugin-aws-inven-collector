from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import EgressOnlyInternetGateway


class EgressOnlyInternetGatewayManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "EgressOnlyInternetGateway"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "EgressOnlyInternetGateway"
        self.metadata_path = "metadata/vpc/egress_only_internet_gateway.yaml"

    def create_cloud_service_type(self):
        result = []
        egress_only_internet_gateway_cst_result = make_cloud_service_type(
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
        result.append(egress_only_internet_gateway_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_egress_only_internet_gateways(options, region)

    def _collect_egress_only_internet_gateways(self, options, region):
        region_name = region

        try:
            egress_only_internet_gateways, account_id = (
                self.connector.list_vpc_egress_only_internet_gateways()
            )

            for egress_only_internet_gateway in egress_only_internet_gateways:
                try:
                    egress_only_internet_gateway_id = egress_only_internet_gateway.get(
                        "EgressOnlyInternetGatewayId"
                    )

                    # Get egress only internet gateway tags
                    tags = self._get_egress_only_internet_gateway_tags(
                        egress_only_internet_gateway_id
                    )

                    egress_only_internet_gateway_data = {
                        "egress_only_internet_gateway_id": egress_only_internet_gateway_id,
                        "attachments": egress_only_internet_gateway.get(
                            "Attachments", []
                        ),
                        "tags": egress_only_internet_gateway.get("Tags", []),
                    }

                    egress_only_internet_gateway_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                egress_only_internet_gateway_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                egress_only_internet_gateway_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#EgressOnlyInternetGateways:search={egress_only_internet_gateway_id}"
                    resource_id = egress_only_internet_gateway_id
                    reference = self.get_reference(resource_id, link)

                    egress_only_internet_gateway_vo = EgressOnlyInternetGateway(
                        egress_only_internet_gateway_data, strict=False
                    )
                    cloud_service = make_cloud_service(
                        name=egress_only_internet_gateway_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=egress_only_internet_gateway_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=egress_only_internet_gateway_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_egress_only_internet_gateways] [{egress_only_internet_gateway.get("EgressOnlyInternetGatewayId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(
                f"[list_vpc_egress_only_internet_gateways] [{region_name}] {e}"
            )
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_egress_only_internet_gateway_tags(self, egress_only_internet_gateway_id):
        """Get egress only internet gateway tags"""
        try:
            return self.connector.get_egress_only_internet_gateway_tags(
                egress_only_internet_gateway_id
            )
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for egress only internet gateway {egress_only_internet_gateway_id}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
