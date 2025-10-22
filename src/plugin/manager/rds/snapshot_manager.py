from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.rds import Snapshot


class SnapshotManager(ResourceManager):
    cloud_service_group = "RDS"
    cloud_service_type = "Snapshot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "Snapshot"
        self.metadata_path = "metadata/rds/snapshot.yaml"

    def create_cloud_service_type(self):
        result = []
        snapshot_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonRDS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-rds.svg"
            },
            labels=["Database"],
        )
        result.append(snapshot_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_snapshots(options, region)

    def _collect_snapshots(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::RDS::DBSnapshot"

        try:
            snapshots, account_id = self.connector.list_rds_snapshots()

            for snapshot in snapshots:
                try:
                    snapshot_id = snapshot.get("DBSnapshotIdentifier")

                    # Get snapshot tags
                    tags = self._get_snapshot_tags(snapshot_id)

                    snapshot_data = {
                        "db_snapshot_identifier": snapshot_id,
                        "db_instance_identifier": snapshot.get(
                            "DBInstanceIdentifier", ""
                        ),
                        "snapshot_create_time": snapshot.get("SnapshotCreateTime"),
                        "engine": snapshot.get("Engine", ""),
                        "allocated_storage": snapshot.get("AllocatedStorage", 0),
                        "status": snapshot.get("Status", ""),
                        "port": snapshot.get("Port", 0),
                        "availability_zone": snapshot.get("AvailabilityZone", ""),
                        "vpc_id": snapshot.get("VpcId", ""),
                        "instance_create_time": snapshot.get("InstanceCreateTime"),
                        "master_username": snapshot.get("MasterUsername", ""),
                        "engine_version": snapshot.get("EngineVersion", ""),
                        "license_model": snapshot.get("LicenseModel", ""),
                        "snapshot_type": snapshot.get("SnapshotType", ""),
                        "iops": snapshot.get("Iops", 0),
                        "option_group_name": snapshot.get("OptionGroupName", ""),
                        "percent_progress": snapshot.get("PercentProgress", 0),
                        "source_region": snapshot.get("SourceRegion", ""),
                        "source_db_snapshot_identifier": snapshot.get(
                            "SourceDBSnapshotIdentifier", ""
                        ),
                        "storage_type": snapshot.get("StorageType", ""),
                        "tde_credential_arn": snapshot.get("TdeCredentialArn", ""),
                        "encrypted": snapshot.get("Encrypted", False),
                        "kms_key_id": snapshot.get("KmsKeyId", ""),
                        "db_snapshot_arn": snapshot.get("DBSnapshotArn"),
                        "timezone": snapshot.get("Timezone", ""),
                        "iam_database_authentication_enabled": snapshot.get(
                            "IAMDatabaseAuthenticationEnabled", False
                        ),
                        "processor_features": snapshot.get("ProcessorFeatures", []),
                        "dbi_resource_id": snapshot.get("DbiResourceId", ""),
                        "tag_list": snapshot.get("TagList", []),
                        "original_snapshot_create_time": snapshot.get(
                            "OriginalSnapshotCreateTime"
                        ),
                        "snapshot_database_time": snapshot.get("SnapshotDatabaseTime"),
                        "snapshot_target": snapshot.get("SnapshotTarget", ""),
                        "storage_throughput": snapshot.get("StorageThroughput", 0),
                        "db_system_id": snapshot.get("DBSystemId", ""),
                        "dedicated_log_volume": snapshot.get(
                            "DedicatedLogVolume", False
                        ),
                        "multi_tenant": snapshot.get("MultiTenant", False),
                    }

                    snapshot_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/rds/home?region={region}#snapshots:snapshot-id={snapshot_id}"
                    resource_id = snapshot_id
                    reference = self.get_reference(resource_id, link)

                    snapshot_vo = Snapshot(snapshot_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=snapshot_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=snapshot_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=snapshot_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_rds_snapshots] [{snapshot.get("DBSnapshotIdentifier")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_rds_snapshots] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_snapshot_tags(self, snapshot_id):
        """Get snapshot tags"""
        try:
            return self.connector.get_snapshot_tags(snapshot_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for snapshot {snapshot_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
