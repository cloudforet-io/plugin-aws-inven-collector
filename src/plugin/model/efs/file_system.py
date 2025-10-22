import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class FileSystem(Model):
    owner_id = StringType(deserialize_from="OwnerId")
    creation_token = StringType(deserialize_from="CreationToken")
    file_system_id = StringType(deserialize_from="FileSystemId")
    file_system_arn = StringType(deserialize_from="FileSystemArn")
    creation_time = DateTimeType(deserialize_from="CreationTime")
    life_cycle_state = StringType(
        deserialize_from="LifeCycleState",
        choices=("creating", "available", "updating", "deleting", "deleted", "error"),
    )
    name = StringType(deserialize_from="Name")
    number_of_mount_targets = IntType(deserialize_from="NumberOfMountTargets")
    size_in_bytes = StringType(deserialize_from="SizeInBytes")
    performance_mode = StringType(
        deserialize_from="PerformanceMode", choices=("generalPurpose", "maxIO")
    )
    encrypted = BooleanType(deserialize_from="Encrypted")
    kms_key_id = StringType(deserialize_from="KmsKeyId")
    throughput_mode = StringType(
        deserialize_from="ThroughputMode", choices=("bursting", "provisioned")
    )
    provisioned_throughput_in_mibps = StringType(
        deserialize_from="ProvisionedThroughputInMibps"
    )
    availability_zone_name = StringType(deserialize_from="AvailabilityZoneName")
    availability_zone_id = StringType(deserialize_from="AvailabilityZoneId")
    tags = StringType(deserialize_from="Tags")
