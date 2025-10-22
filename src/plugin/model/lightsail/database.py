import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Database(Model):
    relational_database_name = StringType(deserialize_from="relationalDatabaseName")
    arn = StringType(deserialize_from="arn")
    support_code = StringType(deserialize_from="supportCode")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    relational_database_blueprint_id = StringType(
        deserialize_from="relationalDatabaseBlueprintId"
    )
    relational_database_bundle_id = StringType(
        deserialize_from="relationalDatabaseBundleId"
    )
    master_database_name = StringType(deserialize_from="masterDatabaseName")
    hardware = StringType(deserialize_from="hardware")
    state = StringType(
        deserialize_from="state",
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
    secondary_availability_zone = StringType(
        deserialize_from="secondaryAvailabilityZone"
    )
    backup_retention_enabled = BooleanType(deserialize_from="backupRetentionEnabled")
    pending_modified_values = StringType(deserialize_from="pendingModifiedValues")
    engine = StringType(deserialize_from="engine")
    engine_version = StringType(deserialize_from="engineVersion")
    latest_restorable_time = DateTimeType(deserialize_from="latestRestorableTime")
    master_endpoint = StringType(deserialize_from="masterEndpoint")
    pending_maintenance_actions = StringType(
        deserialize_from="pendingMaintenanceActions"
    )
    preferred_backup_window = StringType(deserialize_from="preferredBackupWindow")
    preferred_maintenance_window = StringType(
        deserialize_from="preferredMaintenanceWindow"
    )
    publicly_accessible = BooleanType(deserialize_from="publiclyAccessible")
    master_username = StringType(deserialize_from="masterUsername")
    parameter_apply_status = StringType(deserialize_from="parameterApplyStatus")
    backup_retention_period = IntType(deserialize_from="backupRetentionPeriod")
    ca_certificate_identifier = StringType(deserialize_from="caCertificateIdentifier")
    performance_insights_enabled = BooleanType(
        deserialize_from="performanceInsightsEnabled"
    )
    performance_insights_kms_key_id = StringType(
        deserialize_from="performanceInsightsKmsKeyId"
    )
    performance_insights_retention_period = IntType(
        deserialize_from="performanceInsightsRetentionPeriod"
    )
    enabled_cloudwatch_logs_exports = ListType(
        StringType, deserialize_from="enabledCloudwatchLogsExports"
    )
    processor_features = StringType(deserialize_from="processorFeatures")
    deletion_protection = BooleanType(deserialize_from="deletionProtection")
    associated_roles = StringType(deserialize_from="associatedRoles")
    listener_endpoint = StringType(deserialize_from="listenerEndpoint")
    high_availability_config = StringType(deserialize_from="highAvailabilityConfig")
