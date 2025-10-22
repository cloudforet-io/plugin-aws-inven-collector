from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import VPC


class VPCManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "VPC"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "VPC"
        self.metadata_path = "metadata/vpc/vpc.yaml"

    def create_cloud_service_type(self):
        result = []
        vpc_cst_result = make_cloud_service_type(
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
        result.append(vpc_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_vpcs(options, region)

    def _collect_vpcs(self, options, region):
        region_name = region

        try:
            vpcs, account_id = self.connector.list_vpcs()

            for vpc in vpcs:
                try:
                    vpc_id = vpc.get("VpcId")

                    # Get VPC tags
                    tags = self._get_vpc_tags(vpc_id)

                    # Get VPC subnets
                    subnets = self._get_vpc_subnets(vpc_id)

                    # Get VPC route tables
                    route_tables = self._get_vpc_route_tables(vpc_id)

                    # Get VPC network ACLs
                    network_acls = self._get_vpc_network_acls(vpc_id)

                    # Get VPC internet gateways
                    internet_gateways = self._get_vpc_internet_gateways(vpc_id)

                    vpc_data = {
                        "vpc_id": vpc_id,
                        "state": vpc.get("State", ""),
                        "cidr_block": vpc.get("CidrBlock", ""),
                        "dhcp_options_id": vpc.get("DhcpOptionsId", ""),
                        "instance_tenancy": vpc.get("InstanceTenancy", ""),
                        "is_default": vpc.get("IsDefault", False),
                        "owner_id": vpc.get("OwnerId", ""),
                        "cidr_block_association_set": vpc.get(
                            "CidrBlockAssociationSet", []
                        ),
                        "ipv6_cidr_block_association_set": vpc.get(
                            "Ipv6CidrBlockAssociationSet", []
                        ),
                        "tags": vpc.get("Tags", []),
                        "subnets": subnets,
                        "route_tables": route_tables,
                        "network_acls": network_acls,
                        "internet_gateways": internet_gateways,
                    }

                    vpc_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                vpc_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                vpc_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#Vpcs:search={vpc_id}"
                    resource_id = vpc_id
                    reference = self.get_reference(resource_id, link)

                    vpc_vo = VPC(vpc_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=vpc_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=vpc_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=vpc_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_vpcs] [{vpc.get("VpcId")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpcs] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_vpc_tags(self, vpc_id):
        """Get VPC tags"""
        try:
            return self.connector.get_vpc_tags(vpc_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for VPC {vpc_id}: {e}")
            return []

    def _get_vpc_subnets(self, vpc_id):
        """Get VPC subnets"""
        try:
            return self.connector.get_vpc_subnets(vpc_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get subnets for VPC {vpc_id}: {e}")
            return []

    def _get_vpc_route_tables(self, vpc_id):
        """Get VPC route tables"""
        try:
            return self.connector.get_vpc_route_tables(vpc_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get route tables for VPC {vpc_id}: {e}")
            return []

    def _get_vpc_network_acls(self, vpc_id):
        """Get VPC network ACLs"""
        try:
            return self.connector.get_vpc_network_acls(vpc_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get network ACLs for VPC {vpc_id}: {e}")
            return []

    def _get_vpc_internet_gateways(self, vpc_id):
        """Get VPC internet gateways"""
        try:
            return self.connector.get_vpc_internet_gateways(vpc_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get internet gateways for VPC {vpc_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
