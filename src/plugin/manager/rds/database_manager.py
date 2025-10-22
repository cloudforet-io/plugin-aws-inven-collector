from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.rds import Database


class DatabaseManager(ResourceManager):
    cloud_service_group = "RDS"
    cloud_service_type = "Database"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "Database"
        self.metadata_path = "metadata/rds/database.yaml"

    def create_cloud_service_type(self):
        result = []
        database_cst_result = make_cloud_service_type(
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
        result.append(database_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_databases(options, region)

    def _collect_databases(self, options, region):
        region_name = region

        try:
            databases, account_id = self.connector.list_rds_databases()

            for database in databases:
                try:
                    database_id = database.get("DBClusterIdentifier")

                    # Get database tags
                    tags = self._get_database_tags(database_id)

                    # Get database members
                    members = self._get_database_members(database_id)

                    # Get database snapshots
                    snapshots = self._get_database_snapshots(database_id)

                    database_data = {
                        "db_cluster_identifier": database_id,
                        "db_cluster_arn": database.get("DBClusterArn"),
                        "status": database.get("Status", ""),
                        "percent_progress": database.get("PercentProgress", ""),
                        "earliest_restorable_time": database.get(
                            "EarliestRestorableTime"
                        ),
                        "endpoint": database.get("Endpoint", ""),
                        "reader_endpoint": database.get("ReaderEndpoint", ""),
                        "custom_endpoints": database.get("CustomEndpoints", []),
                        "multi_az": database.get("MultiAZ", False),
                        "engine": database.get("Engine", ""),
                        "engine_version": database.get("EngineVersion", ""),
                        "latest_restorable_time": database.get("LatestRestorableTime"),
                        "port": database.get("Port", 0),
                        "master_username": database.get("MasterUsername", ""),
                        "db_cluster_option_group_memberships": database.get(
                            "DBClusterOptionGroupMemberships", []
                        ),
                        "preferred_backup_window": database.get(
                            "PreferredBackupWindow", ""
                        ),
                        "preferred_maintenance_window": database.get(
                            "PreferredMaintenanceWindow", ""
                        ),
                        "replication_source_identifier": database.get(
                            "ReplicationSourceIdentifier", ""
                        ),
                        "read_replica_identifiers": database.get(
                            "ReadReplicaIdentifiers", []
                        ),
                        "db_cluster_members": database.get("DBClusterMembers", []),
                        "vpc_security_groups": database.get("VpcSecurityGroups", []),
                        "hosted_zone_id": database.get("HostedZoneId", ""),
                        "storage_encrypted": database.get("StorageEncrypted", False),
                        "kms_key_id": database.get("KmsKeyId", ""),
                        "db_cluster_resource_id": database.get(
                            "DbClusterResourceId", ""
                        ),
                        "db_cluster_arn": database.get("DBClusterArn"),
                        "associated_roles": database.get("AssociatedRoles", []),
                        "iam_database_authentication_enabled": database.get(
                            "IAMDatabaseAuthenticationEnabled", False
                        ),
                        "clone_group_id": database.get("CloneGroupId", ""),
                        "cluster_create_time": database.get("ClusterCreateTime"),
                        "earliest_backtrack_time": database.get(
                            "EarliestBacktrackTime"
                        ),
                        "backtrack_window": database.get("BacktrackWindow", 0),
                        "backtrack_consumed_change_records": database.get(
                            "BacktrackConsumedChangeRecords", 0
                        ),
                        "enabled_cloudwatch_logs_exports": database.get(
                            "EnabledCloudwatchLogsExports", []
                        ),
                        "capacity": database.get("Capacity", 0),
                        "engine_mode": database.get("EngineMode", ""),
                        "scaling_configuration_info": database.get(
                            "ScalingConfigurationInfo", {}
                        ),
                        "deletion_protection": database.get(
                            "DeletionProtection", False
                        ),
                        "http_endpoint_enabled": database.get(
                            "HttpEndpointEnabled", False
                        ),
                        "activity_stream_kinesis_stream_name": database.get(
                            "ActivityStreamKinesisStreamName", ""
                        ),
                        "activity_stream_kms_key_id": database.get(
                            "ActivityStreamKmsKeyId", ""
                        ),
                        "activity_stream_mode": database.get("ActivityStreamMode", ""),
                        "activity_stream_status": database.get(
                            "ActivityStreamStatus", ""
                        ),
                        "backtrack_window": database.get("BacktrackWindow", 0),
                        "backtrack_consumed_change_records": database.get(
                            "BacktrackConsumedChangeRecords", 0
                        ),
                        "enabled_cloudwatch_logs_exports": database.get(
                            "EnabledCloudwatchLogsExports", []
                        ),
                        "capacity": database.get("Capacity", 0),
                        "engine_mode": database.get("EngineMode", ""),
                        "scaling_configuration_info": database.get(
                            "ScalingConfigurationInfo", {}
                        ),
                        "deletion_protection": database.get(
                            "DeletionProtection", False
                        ),
                        "http_endpoint_enabled": database.get(
                            "HttpEndpointEnabled", False
                        ),
                        "activity_stream_kinesis_stream_name": database.get(
                            "ActivityStreamKinesisStreamName", ""
                        ),
                        "activity_stream_kms_key_id": database.get(
                            "ActivityStreamKmsKeyId", ""
                        ),
                        "activity_stream_mode": database.get("ActivityStreamMode", ""),
                        "activity_stream_status": database.get(
                            "ActivityStreamStatus", ""
                        ),
                        "copy_tags_to_snapshot": database.get(
                            "CopyTagsToSnapshot", False
                        ),
                        "cross_account_clone": database.get("CrossAccountClone", False),
                        "domain_memberships": database.get("DomainMemberships", []),
                        "tag_list": database.get("TagList", []),
                        "global_write_forwarding_status": database.get(
                            "GlobalWriteForwardingStatus", ""
                        ),
                        "global_write_forwarding_requested": database.get(
                            "GlobalWriteForwardingRequested", False
                        ),
                        "pending_modified_values": database.get(
                            "PendingModifiedValues", {}
                        ),
                        "db_cluster_instance_class": database.get(
                            "DBClusterInstanceClass", ""
                        ),
                        "storage_type": database.get("StorageType", ""),
                        "iops": database.get("Iops", 0),
                        "publicly_accessible": database.get(
                            "PubliclyAccessible", False
                        ),
                        "auto_minor_version_upgrade": database.get(
                            "AutoMinorVersionUpgrade", False
                        ),
                        "monitoring_interval": database.get("MonitoringInterval", 0),
                        "monitoring_role_arn": database.get("MonitoringRoleArn", ""),
                        "performance_insights_enabled": database.get(
                            "PerformanceInsightsEnabled", False
                        ),
                        "performance_insights_kms_key_id": database.get(
                            "PerformanceInsightsKmsKeyId", ""
                        ),
                        "performance_insights_retention_period": database.get(
                            "PerformanceInsightsRetentionPeriod", 0
                        ),
                        "serverless_v2_scaling_configuration": database.get(
                            "ServerlessV2ScalingConfiguration", {}
                        ),
                        "network_type": database.get("NetworkType", ""),
                        "db_system_id": database.get("DBSystemId", ""),
                        "master_user_secret": database.get("MasterUserSecret", {}),
                        "io_optimized_next_allowed_modification_time": database.get(
                            "IOOptimizedNextAllowedModificationTime"
                        ),
                        "local_write_forwarding_status": database.get(
                            "LocalWriteForwardingStatus", ""
                        ),
                        "aws_backup_recovery_point_arn": database.get(
                            "AwsBackupRecoveryPointArn", ""
                        ),
                        "members": members,
                        "snapshots": snapshots,
                    }

                    database_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                database_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                database_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/rds/home?region={region}#database:id={database_id};is-cluster=true"
                    resource_id = database_id
                    reference = self.get_reference(resource_id, link)

                    database_vo = Database(database_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=database_id,
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
                        f'[list_rds_databases] [{database.get("DBClusterIdentifier")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_rds_databases] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_database_tags(self, database_id):
        """Get database tags"""
        try:
            return self.connector.get_database_tags(database_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for database {database_id}: {e}")
            return []

    def _get_database_members(self, database_id):
        """Get database members"""
        try:
            return self.connector.get_database_members(database_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get members for database {database_id}: {e}")
            return []

    def _get_database_snapshots(self, database_id):
        """Get database snapshots"""
        try:
            return self.connector.get_database_snapshots(database_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get snapshots for database {database_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
