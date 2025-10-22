import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Instance(Model):
    db_instance_identifier = StringType(deserialize_from="DBInstanceIdentifier")
    db_instance_class = StringType(deserialize_from="DBInstanceClass")
    engine = StringType(deserialize_from="Engine")
    engine_version = StringType(deserialize_from="EngineVersion")
    db_instance_status = StringType(
        deserialize_from="DBInstanceStatus",
        choices=(
            "available",
            "backing-up",
            "configuring-enhanced-monitoring",
            "configuring-log-exports",
            "configuring-read-replica",
            "creating",
            "deleting",
            "failed",
            "inaccessible-encryption-credentials",
            "incompatible-credentials",
            "incompatible-network",
            "incompatible-option-group",
            "incompatible-parameters",
            "incompatible-restore",
            "maintenance",
            "modifying",
            "rebooting",
            "renaming",
            "resetting-master-credentials",
            "restore-error",
            "starting",
            "stopped",
            "stopping",
            "storage-full",
            "storage-optimization",
            "upgrading",
        ),
    )
    master_username = StringType(deserialize_from="MasterUsername")
    db_name = StringType(deserialize_from="DBName")
    endpoint = StringType(deserialize_from="Endpoint")
    allocated_storage = IntType(deserialize_from="AllocatedStorage")
    instance_create_time = DateTimeType(deserialize_from="InstanceCreateTime")
    preferred_backup_window = StringType(deserialize_from="PreferredBackupWindow")
    backup_retention_period = IntType(deserialize_from="BackupRetentionPeriod")
    db_security_groups = StringType(deserialize_from="DBSecurityGroups")
    vpc_security_groups = StringType(deserialize_from="VpcSecurityGroups")
    db_parameter_groups = StringType(deserialize_from="DBParameterGroups")
    availability_zone = StringType(deserialize_from="AvailabilityZone")
    db_subnet_group = StringType(deserialize_from="DBSubnetGroup")
    preferred_maintenance_window = StringType(
        deserialize_from="PreferredMaintenanceWindow"
    )
    pending_modified_values = StringType(deserialize_from="PendingModifiedValues")
    latest_restorable_time = DateTimeType(deserialize_from="LatestRestorableTime")
    multi_az = BooleanType(deserialize_from="MultiAZ")
    engine_version = StringType(deserialize_from="EngineVersion")
    auto_minor_version_upgrade = BooleanType(deserialize_from="AutoMinorVersionUpgrade")
    read_replica_source_db_instance_identifier = StringType(
        deserialize_from="ReadReplicaSourceDBInstanceIdentifier"
    )
    read_replica_db_instance_identifiers = ListType(
        StringType, deserialize_from="ReadReplicaDBInstanceIdentifiers"
    )
    read_replica_db_cluster_identifiers = ListType(
        StringType, deserialize_from="ReadReplicaDBClusterIdentifiers"
    )
    replica_mode = StringType(deserialize_from="ReplicaMode")
    iops = IntType(deserialize_from="Iops")
    option_group_memberships = StringType(deserialize_from="OptionGroupMemberships")
    character_set_name = StringType(deserialize_from="CharacterSetName")
    nchar_character_set_name = StringType(deserialize_from="NcharCharacterSetName")
    secondary_availability_zone = StringType(
        deserialize_from="SecondaryAvailabilityZone"
    )
    publicly_accessible = BooleanType(deserialize_from="PubliclyAccessible")
    status_infos = StringType(deserialize_from="StatusInfos")
    storage_type = StringType(deserialize_from="StorageType")
    tde_credential_arn = StringType(deserialize_from="TdeCredentialArn")
    db_instance_port = IntType(deserialize_from="DbInstancePort")
    db_cluster_identifier = StringType(deserialize_from="DBClusterIdentifier")
    storage_encrypted = BooleanType(deserialize_from="StorageEncrypted")
    kms_key_id = StringType(deserialize_from="KmsKeyId")
    dbi_resource_id = StringType(deserialize_from="DbiResourceId")
    ca_certificate_identifier = StringType(deserialize_from="CACertificateIdentifier")
    domain_memberships = StringType(deserialize_from="DomainMemberships")
    copy_tags_to_snapshot = BooleanType(deserialize_from="CopyTagsToSnapshot")
    monitoring_interval = IntType(deserialize_from="MonitoringInterval")
    enhanced_monitoring_resource_arn = StringType(
        deserialize_from="EnhancedMonitoringResourceArn"
    )
    monitoring_role_arn = StringType(deserialize_from="MonitoringRoleArn")
    promotion_tier = IntType(deserialize_from="PromotionTier")
    db_instance_arn = StringType(deserialize_from="DBInstanceArn")
    timezone = StringType(deserialize_from="Timezone")
    iam_database_authentication_enabled = BooleanType(
        deserialize_from="IAMDatabaseAuthenticationEnabled"
    )
    performance_insights_enabled = BooleanType(
        deserialize_from="PerformanceInsightsEnabled"
    )
    performance_insights_kms_key_id = StringType(
        deserialize_from="PerformanceInsightsKmsKeyId"
    )
    performance_insights_retention_period = IntType(
        deserialize_from="PerformanceInsightsRetentionPeriod"
    )
    enabled_cloudwatch_logs_exports = ListType(
        StringType, deserialize_from="EnabledCloudwatchLogsExports"
    )
    processor_features = StringType(deserialize_from="ProcessorFeatures")
    deletion_protection = BooleanType(deserialize_from="DeletionProtection")
    associated_roles = StringType(deserialize_from="AssociatedRoles")
    listener_endpoint = StringType(deserialize_from="ListenerEndpoint")
    max_allocated_storage = IntType(deserialize_from="MaxAllocatedStorage")
    tag_list = StringType(deserialize_from="TagList")
    db_instance_automated_backups_replications = StringType(
        deserialize_from="DBInstanceAutomatedBackupsReplications"
    )
    customer_owned_ip_enabled = BooleanType(deserialize_from="CustomerOwnedIpEnabled")
    aws_backup_recovery_point_arn = StringType(
        deserialize_from="AwsBackupRecoveryPointArn"
    )
    activity_stream_status = StringType(deserialize_from="ActivityStreamStatus")
    activity_stream_kms_key_id = StringType(deserialize_from="ActivityStreamKmsKeyId")
    activity_stream_kinesis_stream_name = StringType(
        deserialize_from="ActivityStreamKinesisStreamName"
    )
    activity_stream_mode = StringType(deserialize_from="ActivityStreamMode")
    activity_stream_engine_native_audit_fields_included = BooleanType(
        deserialize_from="ActivityStreamEngineNativeAuditFieldsIncluded"
    )
    automation_mode = StringType(deserialize_from="AutomationMode")
    resume_full_automation_mode_time = DateTimeType(
        deserialize_from="ResumeFullAutomationModeTime"
    )
    custom_iam_instance_profile = StringType(
        deserialize_from="CustomIamInstanceProfile"
    )
    backup_target = StringType(deserialize_from="BackupTarget")
    network_type = StringType(deserialize_from="NetworkType")
    activity_stream_policy_status = StringType(
        deserialize_from="ActivityStreamPolicyStatus"
    )
    storage_throughput = IntType(deserialize_from="StorageThroughput")
    db_system_id = StringType(deserialize_from="DBSystemId")
    master_user_secret = StringType(deserialize_from="MasterUserSecret")
    certificate_details = StringType(deserialize_from="CertificateDetails")
    read_replica_source_db_cluster_identifier = StringType(
        deserialize_from="ReadReplicaSourceDBClusterIdentifier"
    )
