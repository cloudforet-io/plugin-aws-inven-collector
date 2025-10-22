import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Snapshot(Model):
    db_snapshot_identifier = StringType(deserialize_from="DBSnapshotIdentifier")
    db_instance_identifier = StringType(deserialize_from="DBInstanceIdentifier")
    snapshot_create_time = DateTimeType(deserialize_from="SnapshotCreateTime")
    engine = StringType(deserialize_from="Engine")
    allocated_storage = IntType(deserialize_from="AllocatedStorage")
    status = StringType(deserialize_from="Status")
    port = IntType(deserialize_from="Port")
    availability_zone = StringType(deserialize_from="AvailabilityZone")
    vpc_id = StringType(deserialize_from="VpcId")
    instance_create_time = DateTimeType(deserialize_from="InstanceCreateTime")
    master_username = StringType(deserialize_from="MasterUsername")
    engine_version = StringType(deserialize_from="EngineVersion")
    license_model = StringType(deserialize_from="LicenseModel")
    snapshot_type = StringType(deserialize_from="SnapshotType")
    iops = IntType(deserialize_from="Iops")
    option_group_name = StringType(deserialize_from="OptionGroupName")
    percent_progress = IntType(deserialize_from="PercentProgress")
    source_region = StringType(deserialize_from="SourceRegion")
    source_db_snapshot_identifier = StringType(
        deserialize_from="SourceDBSnapshotIdentifier"
    )
    storage_type = StringType(deserialize_from="StorageType")
    tde_credential_arn = StringType(deserialize_from="TdeCredentialArn")
    encrypted = BooleanType(deserialize_from="Encrypted")
    kms_key_id = StringType(deserialize_from="KmsKeyId")
    db_snapshot_arn = StringType(deserialize_from="DBSnapshotArn")
    timezone = StringType(deserialize_from="Timezone")
    iam_database_authentication_enabled = BooleanType(
        deserialize_from="IAMDatabaseAuthenticationEnabled"
    )
    processor_features = StringType(deserialize_from="ProcessorFeatures")
    dbi_resource_id = StringType(deserialize_from="DbiResourceId")
    tag_list = StringType(deserialize_from="TagList")
    original_snapshot_create_time = DateTimeType(
        deserialize_from="OriginalSnapshotCreateTime"
    )
    snapshot_database_time = DateTimeType(deserialize_from="SnapshotDatabaseTime")
    snapshot_target = StringType(deserialize_from="SnapshotTarget")
    storage_throughput = IntType(deserialize_from="StorageThroughput")
