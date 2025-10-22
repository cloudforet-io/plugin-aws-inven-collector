from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Instance


class InstanceManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Instance"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Instance"
        self.metadata_path = "metadata/lightsail/instance.yaml"

    def create_cloud_service_type(self):
        result = []
        instance_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonLightsail",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-lightsail.svg"
            },
            labels=["Compute"],
        )
        result.append(instance_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_instances(options, region)

    def _collect_instances(self, options, region):
        region_name = region

        try:
            instances, account_id = self.connector.list_lightsail_instances()

            for instance in instances:
                try:
                    instance_name = instance.get("Name")
                    instance_arn = instance.get("Arn")

                    # Get instance tags
                    tags = self._get_instance_tags(instance_arn)

                    # Get instance ports
                    ports = self._get_instance_ports(instance_name)

                    # Get instance networking
                    networking = self._get_instance_networking(instance_name)

                    instance_data = {
                        "name": instance_name,
                        "arn": instance_arn,
                        "support_code": instance.get("SupportCode", ""),
                        "created_at": instance.get("CreatedAt"),
                        "location": instance.get("Location", {}),
                        "resource_type": instance.get("ResourceType", ""),
                        "tags": instance.get("Tags", []),
                        "blueprint_id": instance.get("BlueprintId", ""),
                        "blueprint_name": instance.get("BlueprintName", ""),
                        "bundle_id": instance.get("BundleId", ""),
                        "is_static_ip": instance.get("IsStaticIp", False),
                        "private_ip_address": instance.get("PrivateIpAddress", ""),
                        "public_ip_address": instance.get("PublicIpAddress", ""),
                        "ip_address_type": instance.get("IpAddressType", ""),
                        "ipv6_addresses": instance.get("Ipv6Addresses", []),
                        "hardware": instance.get("Hardware", {}),
                        "networking": instance.get("Networking", {}),
                        "state": instance.get("State", {}),
                        "username": instance.get("Username", ""),
                        "ssh_key_name": instance.get("SshKeyName", ""),
                        "ports": ports,
                        "networking_details": networking,
                    }

                    instance_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                instance_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                instance_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/instances/{instance_name}"
                    resource_id = instance_arn
                    reference = self.get_reference(resource_id, link)

                    instance_vo = Instance(instance_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=instance_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=instance_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=instance_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_instances] [{instance.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_instances] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_instance_tags(self, instance_arn):
        """Get instance tags"""
        try:
            return self.connector.get_instance_tags(instance_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for instance {instance_arn}: {e}")
            return []

    def _get_instance_ports(self, instance_name):
        """Get instance ports"""
        try:
            return self.connector.get_instance_ports(instance_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get ports for instance {instance_name}: {e}")
            return []

    def _get_instance_networking(self, instance_name):
        """Get instance networking"""
        try:
            return self.connector.get_instance_networking(instance_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get networking for instance {instance_name}: {e}"
            )
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
