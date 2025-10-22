from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.rds import Instance


class InstanceManager(ResourceManager):
    cloud_service_group = "RDS"
    cloud_service_type = "Instance"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "Instance"
        self.metadata_path = "metadata/rds/instance.yaml"

    def create_cloud_service_type(self):
        result = []
        instance_cst_result = make_cloud_service_type(
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
        result.append(instance_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_instances(options, region)

    def _collect_instances(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::RDS::DBInstance"

        try:
            instances, account_id = self.connector.list_rds_instances()

            for instance in instances:
                try:
                    instance_id = instance.get("DBInstanceIdentifier")

                    # Get instance tags
                    tags = self._get_instance_tags(instance_id)

                    # Get instance snapshots
                    snapshots = self._get_instance_snapshots(instance_id)

                    # Get instance parameter groups
                    parameter_groups = self._get_instance_parameter_groups(
                        instance.get("DBParameterGroups", [])
                    )

                    # Get instance option groups
                    option_groups = self._get_instance_option_groups(
                        instance.get("OptionGroupMemberships", [])
                    )

                    instance_data = {
                        "db_instance_identifier": instance_id,
                        "db_instance_arn": instance.get("DBInstanceArn"),
                        "db_instance_class": instance.get("DBInstanceClass", ""),
                        "engine": instance.get("Engine", ""),
                        "engine_version": instance.get("EngineVersion", ""),
                        "db_instance_status": instance.get("DBInstanceStatus", ""),
                        "master_username": instance.get("MasterUsername", ""),
                        "db_name": instance.get("DBName", ""),
                        "endpoint": instance.get("Endpoint", {}),
                        "allocated_storage": instance.get("AllocatedStorage", 0),
                        "instance_create_time": instance.get("InstanceCreateTime"),
                        "preferred_backup_window": instance.get(
                            "PreferredBackupWindow", ""
                        ),
                        "backup_retention_period": instance.get(
                            "BackupRetentionPeriod", 0
                        ),
                        "db_security_groups": instance.get("DBSecurityGroups", []),
                        "vpc_security_groups": instance.get("VpcSecurityGroups", []),
                        "db_parameter_groups": instance.get("DBParameterGroups", []),
                        "availability_zone": instance.get("AvailabilityZone", ""),
                        "db_subnet_group": instance.get("DBSubnetGroup", {}),
                        "preferred_maintenance_window": instance.get(
                            "PreferredMaintenanceWindow", ""
                        ),
                        "pending_modified_values": instance.get(
                            "PendingModifiedValues", {}
                        ),
                        "latest_restorable_time": instance.get("LatestRestorableTime"),
                        "multi_az": instance.get("MultiAZ", False),
                        "engine_version": instance.get("EngineVersion", ""),
                        "auto_minor_version_upgrade": instance.get(
                            "AutoMinorVersionUpgrade", False
                        ),
                        "read_replica_source_db_instance_identifier": instance.get(
                            "ReadReplicaSourceDBInstanceIdentifier", ""
                        ),
                        "read_replica_db_instance_identifiers": instance.get(
                            "ReadReplicaDBInstanceIdentifiers", []
                        ),
                        "read_replica_db_cluster_identifiers": instance.get(
                            "ReadReplicaDBClusterIdentifiers", []
                        ),
                        "license_model": instance.get("LicenseModel", ""),
                        "iops": instance.get("Iops", 0),
                        "option_group_memberships": instance.get(
                            "OptionGroupMemberships", []
                        ),
                        "character_set_name": instance.get("CharacterSetName", ""),
                        "nchar_character_set_name": instance.get(
                            "NcharCharacterSetName", ""
                        ),
                        "secondary_availability_zone": instance.get(
                            "SecondaryAvailabilityZone", ""
                        ),
                        "publicly_accessible": instance.get(
                            "PubliclyAccessible", False
                        ),
                        "status_infos": instance.get("StatusInfos", []),
                        "storage_type": instance.get("StorageType", ""),
                        "tde_credential_arn": instance.get("TdeCredentialArn", ""),
                        "db_instance_port": instance.get("DbInstancePort", 0),
                        "db_cluster_identifier": instance.get(
                            "DBClusterIdentifier", ""
                        ),
                        "storage_encrypted": instance.get("StorageEncrypted", False),
                        "kms_key_id": instance.get("KmsKeyId", ""),
                        "dbi_resource_id": instance.get("DbiResourceId", ""),
                        "ca_certificate_identifier": instance.get(
                            "CACertificateIdentifier", ""
                        ),
                        "domain_memberships": instance.get("DomainMemberships", []),
                        "copy_tags_to_snapshot": instance.get(
                            "CopyTagsToSnapshot", False
                        ),
                        "monitoring_interval": instance.get("MonitoringInterval", 0),
                        "enhanced_monitoring_resource_arn": instance.get(
                            "EnhancedMonitoringResourceArn", ""
                        ),
                        "monitoring_role_arn": instance.get("MonitoringRoleArn", ""),
                        "promotion_tier": instance.get("PromotionTier", 0),
                        "db_instance_automated_backups_replications": instance.get(
                            "DBInstanceAutomatedBackupsReplications", []
                        ),
                        "customer_owned_ip_enabled": instance.get(
                            "CustomerOwnedIpEnabled", False
                        ),
                        "aws_backup_recovery_point_arn": instance.get(
                            "AwsBackupRecoveryPointArn", ""
                        ),
                        "activity_stream_status": instance.get(
                            "ActivityStreamStatus", ""
                        ),
                        "activity_stream_kms_key_id": instance.get(
                            "ActivityStreamKmsKeyId", ""
                        ),
                        "activity_stream_kinesis_stream_name": instance.get(
                            "ActivityStreamKinesisStreamName", ""
                        ),
                        "activity_stream_mode": instance.get("ActivityStreamMode", ""),
                        "activity_stream_engine_native_audit_fields_included": instance.get(
                            "ActivityStreamEngineNativeAuditFieldsIncluded", False
                        ),
                        "automation_mode": instance.get("AutomationMode", ""),
                        "resume_full_automation_mode_time": instance.get(
                            "ResumeFullAutomationModeTime"
                        ),
                        "custom_iam_instance_profile": instance.get(
                            "CustomIamInstanceProfile", ""
                        ),
                        "backup_target": instance.get("BackupTarget", ""),
                        "network_type": instance.get("NetworkType", ""),
                        "activity_stream_policy_status": instance.get(
                            "ActivityStreamPolicyStatus", ""
                        ),
                        "storage_throughput": instance.get("StorageThroughput", 0),
                        "db_system_id": instance.get("DBSystemId", ""),
                        "master_user_secret": instance.get("MasterUserSecret", {}),
                        "certificate_details": instance.get("CertificateDetails", {}),
                        "read_replica_source_db_cluster_identifier": instance.get(
                            "ReadReplicaSourceDBClusterIdentifier", ""
                        ),
                        "snapshots": snapshots,
                        "parameter_groups": parameter_groups,
                        "option_groups": option_groups,
                    }

                    instance_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/rds/home?region={region}#database:id={instance_id};is-cluster=false"
                    resource_id = instance_id
                    reference = self.get_reference(resource_id, link)

                    instance_vo = Instance(instance_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=instance_id,
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
                        f'[list_rds_instances] [{instance.get("DBInstanceIdentifier")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_rds_instances] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_instance_tags(self, instance_id):
        """Get instance tags"""
        try:
            return self.connector.get_instance_tags(instance_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for instance {instance_id}: {e}")
            return []

    def _get_instance_snapshots(self, instance_id):
        """Get instance snapshots"""
        try:
            return self.connector.get_instance_snapshots(instance_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get snapshots for instance {instance_id}: {e}")
            return []

    def _get_instance_parameter_groups(self, parameter_groups):
        """Get instance parameter groups details"""
        if not parameter_groups:
            return []

        try:
            return self.connector.get_instance_parameter_groups(parameter_groups)
        except Exception as e:
            _LOGGER.warning(f"Failed to get parameter groups: {e}")
            return []

    def _get_instance_option_groups(self, option_groups):
        """Get instance option groups details"""
        if not option_groups:
            return []

        try:
            return self.connector.get_instance_option_groups(option_groups)
        except Exception as e:
            _LOGGER.warning(f"Failed to get option groups: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
