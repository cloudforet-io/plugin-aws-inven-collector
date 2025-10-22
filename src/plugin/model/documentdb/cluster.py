import logging
from schematics import Model
from schematics.types import StringType, IntType, DateTimeType, ListType, BooleanType, DictType

_LOGGER = logging.getLogger(__name__)


class Cluster(Model):
    availability_zones = ListType(StringType, deserialize_from="AvailabilityZones")
    backup_retention_period = IntType(deserialize_from="BackupRetentionPeriod")
    db_cluster_identifier = StringType(deserialize_from="DBClusterIdentifier")
    db_cluster_parameter_group = StringType(deserialize_from="DBClusterParameterGroup")
    db_subnet_group = StringType(deserialize_from="DBSubnetGroup")
    status = StringType(deserialize_from="Status")
    percent_progress = StringType(deserialize_from="PercentProgress")
    earliest_restorable_time = DateTimeType(deserialize_from="EarliestRestorableTime")
    endpoint = StringType(deserialize_from="Endpoint")
    reader_endpoint = StringType(deserialize_from="ReaderEndpoint")
    multi_az = BooleanType(deserialize_from="MultiAZ")
    engine = StringType(deserialize_from="Engine")
    engine_version = StringType(deserialize_from="EngineVersion")
    latest_restorable_time = DateTimeType(deserialize_from="LatestRestorableTime")
    port = IntType(deserialize_from="Port")
    master_username = StringType(deserialize_from="MasterUsername")
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
    copy_tags_to_snapshot = BooleanType(deserialize_from="CopyTagsToSnapshot")
    enabled_cloudwatch_logs_exports = ListType(
        StringType, deserialize_from="EnabledCloudwatchLogsExports"
    )
    deletion_protection = BooleanType(deserialize_from="DeletionProtection")
    tags = StringType(deserialize_from="Tags")
    instances = ListType(StringType, deserialize_from="instances")
    instance_count = IntType(deserialize_from="instance_count")
    cloudwatch = DictType(StringType, deserialize_from="cloudwatch")
    cloudtrail = DictType(StringType, deserialize_from="cloudtrail")
