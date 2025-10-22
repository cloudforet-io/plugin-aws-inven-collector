import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Disk(Model):
    name = StringType(deserialize_from="name")
    arn = StringType(deserialize_from="arn")
    support_code = StringType(deserialize_from="supportCode")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    add_ons = StringType(deserialize_from="addOns")
    size_in_gb = IntType(deserialize_from="sizeInGb")
    is_system_disk = BooleanType(deserialize_from="isSystemDisk")
    iops = IntType(deserialize_from="iops")
    path = StringType(deserialize_from="path")
    state = StringType(
        deserialize_from="state",
        choices=("pending", "error", "available", "in-use", "unknown"),
    )
    attached_to = StringType(deserialize_from="attachedTo")
    is_attached = BooleanType(deserialize_from="isAttached")
    attachment_state = StringType(deserialize_from="attachmentState")
    gb_in_use = IntType(deserialize_from="gbInUse")
    auto_mount_status = StringType(deserialize_from="autoMountStatus")
