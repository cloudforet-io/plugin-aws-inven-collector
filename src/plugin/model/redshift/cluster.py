import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Cluster(Model):
    cluster_identifier = StringType(deserialize_from="ClusterIdentifier")
    node_type = StringType(deserialize_from="NodeType")
    cluster_status = StringType(
        deserialize_from="ClusterStatus",
        choices=(
            "available",
            "available, prep-for-resize",
            "available, resize-cleanup",
            "cancelling-resize",
            "creating",
            "deleting",
            "final-snapshot",
            "hardware-failure",
            "incompatible-hsm",
            "incompatible-network",
            "incompatible-parameters",
            "incompatible-restore",
            "modifying",
            "paused",
            "rebooting",
            "renaming",
            "resizing",
            "rotating-keys",
            "storage-full",
            "updating-hsm",
        ),
    )
    cluster_availability_status = StringType(
        deserialize_from="ClusterAvailabilityStatus"
    )
    modify_status = StringType(deserialize_from="ModifyStatus")
    master_username = StringType(deserialize_from="MasterUsername")
    db_name = StringType(deserialize_from="DBName")
    endpoint = StringType(deserialize_from="Endpoint")
    cluster_create_time = DateTimeType(deserialize_from="ClusterCreateTime")
    automated_snapshot_retention_period = IntType(
        deserialize_from="AutomatedSnapshotRetentionPeriod"
    )
    manual_snapshot_retention_period = IntType(
        deserialize_from="ManualSnapshotRetentionPeriod"
    )
    cluster_security_groups = StringType(deserialize_from="ClusterSecurityGroups")
    vpc_security_groups = StringType(deserialize_from="VpcSecurityGroups")
    cluster_parameter_groups = StringType(deserialize_from="ClusterParameterGroups")
    cluster_subnet_group_name = StringType(deserialize_from="ClusterSubnetGroupName")
    vpc_id = StringType(deserialize_from="VpcId")
    availability_zone = StringType(deserialize_from="AvailabilityZone")
    preferred_maintenance_window = StringType(
        deserialize_from="PreferredMaintenanceWindow"
    )
    pending_modified_values = StringType(deserialize_from="PendingModifiedValues")
    cluster_version = StringType(deserialize_from="ClusterVersion")
    allow_version_upgrade = BooleanType(deserialize_from="AllowVersionUpgrade")
    number_of_nodes = IntType(deserialize_from="NumberOfNodes")
    publicly_accessible = BooleanType(deserialize_from="PubliclyAccessible")
    encrypted = BooleanType(deserialize_from="Encrypted")
    restore_status = StringType(deserialize_from="RestoreStatus")
    data_transfer_progress = StringType(deserialize_from="DataTransferProgress")
    hsm_status = StringType(deserialize_from="HsmStatus")
    cluster_snapshot_copy_status = StringType(
        deserialize_from="ClusterSnapshotCopyStatus"
    )
    cluster_public_key = StringType(deserialize_from="ClusterPublicKey")
    cluster_nodes = StringType(deserialize_from="ClusterNodes")
    elastic_ip_status = StringType(deserialize_from="ElasticIpStatus")
    cluster_revision_number = StringType(deserialize_from="ClusterRevisionNumber")
    tags = StringType(deserialize_from="Tags")
    kms_key_id = StringType(deserialize_from="KmsKeyId")
    enhanced_vpc_routing = BooleanType(deserialize_from="EnhancedVpcRouting")
    iam_roles = StringType(deserialize_from="IamRoles")
    pending_actions = ListType(StringType, deserialize_from="PendingActions")
    maintenance_track_name = StringType(deserialize_from="MaintenanceTrackName")
    elastic_resize_number_of_node_options = StringType(
        deserialize_from="ElasticResizeNumberOfNodeOptions"
    )
    deferred_maintenance_windows = StringType(
        deserialize_from="DeferredMaintenanceWindows"
    )
    snapshot_schedule_identifier = StringType(
        deserialize_from="SnapshotScheduleIdentifier"
    )
    snapshot_schedule_state = StringType(deserialize_from="SnapshotScheduleState")
    expected_next_snapshot_schedule_time = DateTimeType(
        deserialize_from="ExpectedNextSnapshotScheduleTime"
    )
    expected_next_snapshot_schedule_time_status = StringType(
        deserialize_from="ExpectedNextSnapshotScheduleTimeStatus"
    )
    next_maintenance_window_start_time = DateTimeType(
        deserialize_from="NextMaintenanceWindowStartTime"
    )
    resize_info = StringType(deserialize_from="ResizeInfo")
    availability_zone_relocation_status = StringType(
        deserialize_from="AvailabilityZoneRelocationStatus"
    )
    cluster_namespace_arn = StringType(deserialize_from="ClusterNamespaceArn")
    total_storage_capacity_in_mega_bytes = IntType(
        deserialize_from="TotalStorageCapacityInMegaBytes"
    )
    aqua_configuration = StringType(deserialize_from="AquaConfiguration")
    default_iam_role_arn = StringType(deserialize_from="DefaultIamRoleArn")
    reserved_node_exchange_status = StringType(
        deserialize_from="ReservedNodeExchangeStatus"
    )
    custom_domain_name = StringType(deserialize_from="CustomDomainName")
    custom_domain_certificate_arn = StringType(
        deserialize_from="CustomDomainCertificateArn"
    )
    custom_domain_certificate_expiry_date = DateTimeType(
        deserialize_from="CustomDomainCertificateExpiryDate"
    )
    master_password_secret_arn = StringType(deserialize_from="MasterPasswordSecretArn")
    master_password_secret_kms_key_id = StringType(
        deserialize_from="MasterPasswordSecretKmsKeyId"
    )
    ip_address_type = StringType(deserialize_from="IpAddressType")
    multi_az = StringType(deserialize_from="MultiAZ")
    multi_az_secondary = StringType(deserialize_from="MultiAZSecondary")
