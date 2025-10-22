from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.efs import FileSystem


class FileSystemManager(ResourceManager):
    cloud_service_group = "EFS"
    cloud_service_type = "FileSystem"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EFS"
        self.cloud_service_type = "FileSystem"
        self.metadata_path = "metadata/efs/file_system.yaml"

    def create_cloud_service_type(self):
        result = []
        file_system_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEFS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-efs.svg"
            },
            labels=["Storage"],
        )
        result.append(file_system_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_file_systems(options, region)

    def _collect_file_systems(self, options, region):
        region_name = region

        try:
            file_systems, account_id = self.connector.list_efs_file_systems()

            for file_system in file_systems:
                try:
                    file_system_id = file_system.get("FileSystemId")

                    # Get file system tags
                    tags = self._get_file_system_tags(file_system_id)

                    # Get mount targets
                    mount_targets = self._get_file_system_mount_targets(file_system_id)

                    # Get access points
                    access_points = self._get_file_system_access_points(file_system_id)

                    file_system_data = {
                        "file_system_id": file_system_id,
                        "creation_token": file_system.get("CreationToken", ""),
                        "creation_time": file_system.get("CreationTime"),
                        "life_cycle_state": file_system.get("LifeCycleState", ""),
                        "name": file_system.get("Name", ""),
                        "number_of_mount_targets": file_system.get(
                            "NumberOfMountTargets", 0
                        ),
                        "owner_id": file_system.get("OwnerId", ""),
                        "size_in_bytes": file_system.get("SizeInBytes", {}),
                        "performance_mode": file_system.get("PerformanceMode", ""),
                        "encrypted": file_system.get("Encrypted", False),
                        "kms_key_id": file_system.get("KmsKeyId", ""),
                        "throughput_mode": file_system.get("ThroughputMode", ""),
                        "provisioned_throughput_in_mibps": file_system.get(
                            "ProvisionedThroughputInMibps", 0
                        ),
                        "availability_zone_name": file_system.get(
                            "AvailabilityZoneName", ""
                        ),
                        "availability_zone_id": file_system.get(
                            "AvailabilityZoneId", ""
                        ),
                        "tags": file_system.get("Tags", []),
                        "mount_targets": mount_targets,
                        "access_points": access_points,
                    }

                    file_system_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                file_system_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                file_system_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/efs/home?region={region}#/file-systems/{file_system_id}"
                    resource_id = file_system_id
                    reference = self.get_reference(resource_id, link)

                    file_system_vo = FileSystem(file_system_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=file_system_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=file_system_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=file_system_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_efs_file_systems] [{file_system.get("FileSystemId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_efs_file_systems] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_file_system_tags(self, file_system_id):
        """Get file system tags"""
        try:
            return self.connector.get_file_system_tags(file_system_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for file system {file_system_id}: {e}")
            return []

    def _get_file_system_mount_targets(self, file_system_id):
        """Get file system mount targets"""
        try:
            return self.connector.get_file_system_mount_targets(file_system_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get mount targets for file system {file_system_id}: {e}"
            )
            return []

    def _get_file_system_access_points(self, file_system_id):
        """Get file system access points"""
        try:
            return self.connector.get_file_system_access_points(file_system_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get access points for file system {file_system_id}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
