import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Database(Model):
    db_cluster_identifier = StringType(deserialize_from="DBClusterIdentifier")
    db_cluster_parameter_group = StringType(deserialize_from="DBClusterParameterGroup")
    db_subnet_group = StringType(deserialize_from="DBSubnetGroup")
    status = StringType(deserialize_from="Status")
    percent_progress = StringType(deserialize_from="PercentProgress")
    earliest_restorable_time = DateTimeType(deserialize_from="EarliestRestorableTime")
    endpoint = StringType(deserialize_from="Endpoint")
    reader_endpoint = StringType(deserialize_from="ReaderEndpoint")
    custom_endpoints = ListType(StringType, deserialize_from="CustomEndpoints")
    multi_az = BooleanType(deserialize_from="MultiAZ")
    engine = StringType(deserialize_from="Engine")
    engine_version = StringType(deserialize_from="EngineVersion")
    latest_restorable_time = DateTimeType(deserialize_from="LatestRestorableTime")
    port = IntType(deserialize_from="Port")
    master_username = StringType(deserialize_from="MasterUsername")
    db_cluster_option_group_memberships = StringType(
        deserialize_from="DBClusterOptionGroupMemberships"
    )
    preferred_backup_window = StringType(deserialize_from="PreferredBackupWindow")
    preferred_maintenance_window = StringType(
        deserialize_from="PreferredMaintenanceWindow"
    )
    replication_source_identifier = StringType(
        deserialize_from="ReplicationSourceIdentifier"
    )
    read_replica_identifiers = ListType(
        StringType, deserialize_from="ReadReplicaIdentifiers"
    )
    db_cluster_members = StringType(deserialize_from="DBClusterMembers")
    vpc_security_groups = StringType(deserialize_from="VpcSecurityGroups")
    hosted_zone_id = StringType(deserialize_from="HostedZoneId")
    storage_encrypted = BooleanType(deserialize_from="StorageEncrypted")
    kms_key_id = StringType(deserialize_from="KmsKeyId")
    db_cluster_resource_id = StringType(deserialize_from="DbClusterResourceId")
    db_cluster_arn = StringType(deserialize_from="DBClusterArn")
    associated_roles = StringType(deserialize_from="AssociatedRoles")
    iam_database_authentication_enabled = BooleanType(
        deserialize_from="IAMDatabaseAuthenticationEnabled"
    )
    clone_group_id = StringType(deserialize_from="CloneGroupId")
    cluster_create_time = DateTimeType(deserialize_from="ClusterCreateTime")
    earliest_backtrack_time = DateTimeType(deserialize_from="EarliestBacktrackTime")
    backtrack_window = IntType(deserialize_from="BacktrackWindow")
    backtrack_consumed_change_records = IntType(
        deserialize_from="BacktrackConsumedChangeRecords"
    )
    enabled_cloudwatch_logs_exports = ListType(
        StringType, deserialize_from="EnabledCloudwatchLogsExports"
    )
    capacity = StringType(deserialize_from="Capacity")
    engine_mode = StringType(deserialize_from="EngineMode")
    scaling_configuration_info = StringType(deserialize_from="ScalingConfigurationInfo")
    deletion_protection = BooleanType(deserialize_from="DeletionProtection")
    http_endpoint_enabled = BooleanType(deserialize_from="HttpEndpointEnabled")
    activity_stream_mode = StringType(deserialize_from="ActivityStreamMode")
    activity_stream_status = StringType(deserialize_from="ActivityStreamStatus")
    activity_stream_kms_key_id = StringType(deserialize_from="ActivityStreamKmsKeyId")
    activity_stream_kinesis_stream_name = StringType(
        deserialize_from="ActivityStreamKinesisStreamName"
    )
    copy_tags_to_snapshot = BooleanType(deserialize_from="CopyTagsToSnapshot")
    cross_account_clone = BooleanType(deserialize_from="CrossAccountClone")
    domain_memberships = StringType(deserialize_from="DomainMemberships")
    tag_list = StringType(deserialize_from="TagList")
    global_write_forwarding_status = StringType(
        deserialize_from="GlobalWriteForwardingStatus"
    )
    global_write_forwarding_requested = BooleanType(
        deserialize_from="GlobalWriteForwardingRequested"
    )
    pending_modified_values = StringType(deserialize_from="PendingModifiedValues")
    db_cluster_instance_class = StringType(deserialize_from="DBClusterInstanceClass")
    storage_type = StringType(deserialize_from="StorageType")
    iops = IntType(deserialize_from="Iops")
    publicly_accessible = BooleanType(deserialize_from="PubliclyAccessible")
    auto_minor_version_upgrade = BooleanType(deserialize_from="AutoMinorVersionUpgrade")
    monitoring_interval = IntType(deserialize_from="MonitoringInterval")
    monitoring_role_arn = StringType(deserialize_from="MonitoringRoleArn")
    database_insights_mode = StringType(deserialize_from="DatabaseInsightsMode")
    performance_insights_enabled = BooleanType(
        deserialize_from="PerformanceInsightsEnabled"
    )
    performance_insights_kms_key_id = StringType(
        deserialize_from="PerformanceInsightsKmsKeyId"
    )
    performance_insights_retention_period = IntType(
        deserialize_from="PerformanceInsightsRetentionPeriod"
    )
    serverless_v2_scaling_configuration = StringType(
        deserialize_from="ServerlessV2ScalingConfiguration"
    )
    network_type = StringType(deserialize_from="NetworkType")
    db_system_id = StringType(deserialize_from="DBSystemId")
    master_user_secret = StringType(deserialize_from="MasterUserSecret")
    io_optimized_next_allowed_modification_time = DateTimeType(
        deserialize_from="IOOptimizedNextAllowedModificationTime"
    )
    local_write_forwarding_status = StringType(
        deserialize_from="LocalWriteForwardingStatus"
    )
    aws_backup_recovery_point_arn = StringType(
        deserialize_from="AwsBackupRecoveryPointArn"
    )
