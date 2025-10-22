from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Disk


class DiskManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Disk"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Disk"
        self.metadata_path = "metadata/lightsail/disk.yaml"

    def create_cloud_service_type(self):
        result = []
        disk_cst_result = make_cloud_service_type(
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
            labels=["Storage"],
        )
        result.append(disk_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_disks(options, region)

    def _collect_disks(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Lightsail::Disk"

        try:
            disks, account_id = self.connector.list_lightsail_disks()

            for disk in disks:
                try:
                    disk_name = disk.get("Name")
                    disk_arn = disk.get("Arn")

                    # Get disk tags
                    tags = self._get_disk_tags(disk_arn)

                    # Get disk snapshots
                    snapshots = self._get_disk_snapshots(disk_name)

                    # Get disk attachments
                    attachments = self._get_disk_attachments(disk_name)

                    disk_data = {
                        "name": disk_name,
                        "arn": disk_arn,
                        "created_at": disk.get("CreatedAt"),
                        "location": disk.get("Location", {}),
                        "resource_type": disk.get("ResourceType", ""),
                        "tags": disk.get("Tags", []),
                        "support_code": disk.get("SupportCode", ""),
                        "size_in_gb": disk.get("SizeInGb", 0),
                        "is_system_disk": disk.get("IsSystemDisk", False),
                        "iops": disk.get("Iops", 0),
                        "path": disk.get("Path", ""),
                        "state": disk.get("State", ""),
                        "attached_to": disk.get("AttachedTo", ""),
                        "is_attached": disk.get("IsAttached", False),
                        "attachment_state": disk.get("AttachmentState", ""),
                        "gb_in_use": disk.get("GbInUse", 0),
                        "auto_mount_status": disk.get("AutoMountStatus", ""),
                        "snapshots": snapshots,
                        "attachments": attachments,
                    }

                    disk_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/storage/disks/{disk_name}"
                    resource_id = disk_arn
                    reference = self.get_reference(resource_id, link)

                    disk_vo = Disk(disk_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=disk_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=disk_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=disk_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_lightsail_disks] [{disk.get("Name")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_disks] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_disk_tags(self, disk_arn):
        """Get disk tags"""
        try:
            return self.connector.get_disk_tags(disk_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for disk {disk_arn}: {e}")
            return []

    def _get_disk_snapshots(self, disk_name):
        """Get disk snapshots"""
        try:
            return self.connector.get_disk_snapshots(disk_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get snapshots for disk {disk_name}: {e}")
            return []

    def _get_disk_attachments(self, disk_name):
        """Get disk attachments"""
        try:
            return self.connector.get_disk_attachments(disk_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get attachments for disk {disk_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
