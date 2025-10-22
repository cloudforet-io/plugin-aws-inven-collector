from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import Subnet


class SubnetManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "Subnet"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "Subnet"
        self.metadata_path = "metadata/vpc/subnet.yaml"

    def create_cloud_service_type(self):
        result = []
        subnet_cst_result = make_cloud_service_type(
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
        result.append(subnet_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_subnets(options, region)

    def _collect_subnets(self, options, region):
        region_name = region

        try:
            subnets, account_id = self.connector.list_vpc_subnets()

            for subnet in subnets:
                try:
                    subnet_id = subnet.get("SubnetId")

                    # Get subnet tags
                    tags = self._get_subnet_tags(subnet_id)

                    subnet_data = {
                        "subnet_id": subnet_id,
                        "vpc_id": subnet.get("VpcId", ""),
                        "availability_zone": subnet.get("AvailabilityZone", ""),
                        "availability_zone_id": subnet.get("AvailabilityZoneId", ""),
                        "available_ip_address_count": subnet.get(
                            "AvailableIpAddressCount", 0
                        ),
                        "cidr_block": subnet.get("CidrBlock", ""),
                        "default_for_az": subnet.get("DefaultForAz", False),
                        "map_public_ip_on_launch": subnet.get(
                            "MapPublicIpOnLaunch", False
                        ),
                        "map_customer_owned_ip_on_launch": subnet.get(
                            "MapCustomerOwnedIpOnLaunch", False
                        ),
                        "customer_owned_ipv4_pool": subnet.get(
                            "CustomerOwnedIpv4Pool", ""
                        ),
                        "state": subnet.get("State", ""),
                        "subnet_arn": subnet.get("SubnetArn", ""),
                        "outpost_arn": subnet.get("OutpostArn", ""),
                        "enable_dns64": subnet.get("EnableDns64", False),
                        "ipv6_native": subnet.get("Ipv6Native", False),
                        "private_dns_name_options_on_launch": subnet.get(
                            "PrivateDnsNameOptionsOnLaunch", {}
                        ),
                        "assign_ipv6_address_on_creation": subnet.get(
                            "AssignIpv6AddressOnCreation", False
                        ),
                        "ipv6_cidr_block_association_set": subnet.get(
                            "Ipv6CidrBlockAssociationSet", []
                        ),
                        "tags": subnet.get("Tags", []),
                        "owner_id": subnet.get("OwnerId", ""),
                    }

                    subnet_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                subnet_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                subnet_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#Subnets:search={subnet_id}"
                    resource_id = subnet_id
                    reference = self.get_reference(resource_id, link)

                    subnet_vo = Subnet(subnet_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=subnet_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=subnet_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=subnet_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_vpc_subnets] [{subnet.get("SubnetId")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_subnets] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_subnet_tags(self, subnet_id):
        """Get subnet tags"""
        try:
            return self.connector.get_subnet_tags(subnet_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for subnet {subnet_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
