import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Snapshot(Model):
    name = StringType(deserialize_from="name")
    arn = StringType(deserialize_from="arn")
    support_code = StringType(deserialize_from="supportCode")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    state = StringType(
        deserialize_from="state", choices=("pending", "completed", "error", "unknown")
    )
    progress = StringType(deserialize_from="progress")
    from_resource_name = StringType(deserialize_from="fromResourceName")
    from_resource_arn = StringType(deserialize_from="fromResourceArn")
    from_blueprint_id = StringType(deserialize_from="fromBlueprintId")
    from_bundle_id = StringType(deserialize_from="fromBundleId")
    is_from_auto_snapshot = BooleanType(deserialize_from="isFromAutoSnapshot")
    size_in_gb = IntType(deserialize_from="sizeInGb")
