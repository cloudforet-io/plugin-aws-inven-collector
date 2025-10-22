from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Database


class DatabaseManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Database"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Database"
        self.metadata_path = "metadata/lightsail/database.yaml"

    def create_cloud_service_type(self):
        result = []
        database_cst_result = make_cloud_service_type(
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
            labels=["Database"],
        )
        result.append(database_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_databases(options, region)

    def _collect_databases(self, options, region):
        region_name = region

        try:
            databases, account_id = self.connector.list_lightsail_databases()

            for database in databases:
                try:
                    database_name = database.get("RelationalDatabaseName")
                    database_arn = database.get("Arn")

                    # Get database tags
                    tags = self._get_database_tags(database_arn)

                    # Get database events
                    events = self._get_database_events(database_name)

                    # Get database logs
                    logs = self._get_database_logs(database_name)

                    database_data = {
                        "relational_database_name": database_name,
                        "arn": database_arn,
                        "relational_database_arn": database.get(
                            "RelationalDatabaseArn", ""
                        ),
                        "created_at": database.get("CreatedAt"),
                        "location": database.get("Location", {}),
                        "resource_type": database.get("ResourceType", ""),
                        "tags": database.get("Tags", []),
                        "relational_database_blueprint_id": database.get(
                            "RelationalDatabaseBlueprintId", ""
                        ),
                        "relational_database_bundle_id": database.get(
                            "RelationalDatabaseBundleId", ""
                        ),
                        "master_database_name": database.get("MasterDatabaseName", ""),
                        "hardware": database.get("Hardware", {}),
                        "state": database.get("State", ""),
                        "secondary_availability_zone": database.get(
                            "SecondaryAvailabilityZone", ""
                        ),
                        "backup_retention_enabled": database.get(
                            "BackupRetentionEnabled", False
                        ),
                        "pending_modified_values": database.get(
                            "PendingModifiedValues", {}
                        ),
                        "engine": database.get("Engine", ""),
                        "engine_version": database.get("EngineVersion", ""),
                        "latest_restorable_time": database.get("LatestRestorableTime"),
                        "master_endpoint": database.get("MasterEndpoint", {}),
                        "preferred_backup_window": database.get(
                            "PreferredBackupWindow", ""
                        ),
                        "preferred_maintenance_window": database.get(
                            "PreferredMaintenanceWindow", ""
                        ),
                        "publicly_accessible": database.get(
                            "PubliclyAccessible", False
                        ),
                        "master_username": database.get("MasterUsername", ""),
                        "parameter_apply_status": database.get(
                            "ParameterApplyStatus", ""
                        ),
                        "ca_certificate_identifier": database.get(
                            "CaCertificateIdentifier", ""
                        ),
                        "pending_maintenance_actions": database.get(
                            "PendingMaintenanceActions", []
                        ),
                        "automatic_snapshot_retention_days": database.get(
                            "AutomaticSnapshotRetentionDays", 0
                        ),
                        "events": events,
                        "logs": logs,
                    }

                    database_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                database_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                database_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/databases/{database_name}"
                    resource_id = database_arn
                    reference = self.get_reference(resource_id, link)

                    database_vo = Database(database_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=database_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=database_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=database_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_databases] [{database.get("RelationalDatabaseName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_databases] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_database_tags(self, database_arn):
        """Get database tags"""
        try:
            return self.connector.get_database_tags(database_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for database {database_arn}: {e}")
            return []

    def _get_database_events(self, database_name):
        """Get database events"""
        try:
            return self.connector.get_database_events(database_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get events for database {database_name}: {e}")
            return []

    def _get_database_logs(self, database_name):
        """Get database logs"""
        try:
            return self.connector.get_database_logs(database_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get logs for database {database_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
