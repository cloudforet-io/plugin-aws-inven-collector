from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.eip import EIP


class EIPManager(ResourceManager):
    cloud_service_group = "EIP"
    cloud_service_type = "EIP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EIP"
        self.cloud_service_type = "EIP"
        self.metadata_path = "metadata/eip/eip.yaml"

    def create_cloud_service_type(self):
        result = []
        eip_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEC2",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-eip.svg"
            },
            labels=["Networking"],
        )
        result.append(eip_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_eips(options, region)

    def _collect_eips(self, options, region):
        region_name = region

        try:
            eips, account_id = self.connector.list_eip_addresses()

            for eip in eips:
                try:
                    allocation_id = eip.get("AllocationId")
                    public_ip = eip.get("PublicIp")

                    # Get EIP tags
                    tags = self._get_eip_tags(allocation_id)

                    eip_data = {
                        "allocation_id": allocation_id,
                        "public_ip": public_ip,
                        "domain": eip.get("Domain", ""),
                        "instance_id": eip.get("InstanceId", ""),
                        "association_id": eip.get("AssociationId", ""),
                        "network_interface_id": eip.get("NetworkInterfaceId", ""),
                        "network_interface_owner_id": eip.get(
                            "NetworkInterfaceOwnerId", ""
                        ),
                        "private_ip_address": eip.get("PrivateIpAddress", ""),
                        "public_ipv4_pool": eip.get("PublicIpv4Pool", ""),
                        "network_border_group": eip.get("NetworkBorderGroup", ""),
                        "carrier_ip": eip.get("CarrierIp", ""),
                        "customer_owned_ip": eip.get("CustomerOwnedIp", ""),
                        "customer_owned_ipv4_pool": eip.get(
                            "CustomerOwnedIpv4Pool", ""
                        ),
                    }

                    eip_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                allocation_id or public_ip,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                allocation_id or public_ip,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#Addresses:search={public_ip}"
                    resource_id = allocation_id or public_ip
                    reference = self.get_reference(resource_id, link)

                    eip_vo = EIP(eip_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=public_ip,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=eip_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=eip_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_eip_addresses] [{eip.get("PublicIp")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_eip_addresses] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_eip_tags(self, allocation_id):
        """Get EIP tags"""
        try:
            return self.connector.get_eip_tags(allocation_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for EIP {allocation_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
