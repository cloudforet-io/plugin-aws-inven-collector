from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import NetworkACL


class NetworkACLManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "NetworkACL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "NetworkACL"
        self.metadata_path = "metadata/vpc/network_acl.yaml"

    def create_cloud_service_type(self):
        result = []
        network_acl_cst_result = make_cloud_service_type(
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
        result.append(network_acl_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_network_acls(options, region)

    def _collect_network_acls(self, options, region):
        region_name = region

        try:
            network_acls, account_id = self.connector.list_vpc_network_acls()

            for network_acl in network_acls:
                try:
                    network_acl_id = network_acl.get("NetworkAclId")

                    # Get network ACL tags
                    tags = self._get_network_acl_tags(network_acl_id)

                    # Get network ACL entries
                    entries = self._get_network_acl_entries(network_acl_id)

                    # Get network ACL associations
                    associations = self._get_network_acl_associations(network_acl_id)

                    network_acl_data = {
                        "network_acl_id": network_acl_id,
                        "vpc_id": network_acl.get("VpcId", ""),
                        "is_default": network_acl.get("IsDefault", False),
                        "associations": network_acl.get("Associations", []),
                        "entries": network_acl.get("Entries", []),
                        "owner_id": network_acl.get("OwnerId", ""),
                        "tags": network_acl.get("Tags", []),
                        "acl_entries": entries,
                        "acl_associations": associations,
                    }

                    network_acl_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                network_acl_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                network_acl_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#NetworkAcls:search={network_acl_id}"
                    resource_id = network_acl_id
                    reference = self.get_reference(resource_id, link)

                    network_acl_vo = NetworkACL(network_acl_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=network_acl_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=network_acl_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=network_acl_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_network_acls] [{network_acl.get("NetworkAclId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_network_acls] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_network_acl_tags(self, network_acl_id):
        """Get network ACL tags"""
        try:
            return self.connector.get_network_acl_tags(network_acl_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for network ACL {network_acl_id}: {e}")
            return []

    def _get_network_acl_entries(self, network_acl_id):
        """Get network ACL entries"""
        try:
            return self.connector.get_network_acl_entries(network_acl_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get entries for network ACL {network_acl_id}: {e}"
            )
            return []

    def _get_network_acl_associations(self, network_acl_id):
        """Get network ACL associations"""
        try:
            return self.connector.get_network_acl_associations(network_acl_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get associations for network ACL {network_acl_id}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
