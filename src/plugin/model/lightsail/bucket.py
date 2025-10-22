import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Bucket(Model):
    name = StringType(deserialize_from="name")
    arn = StringType(deserialize_from="arn")
    support_code = StringType(deserialize_from="supportCode")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    bundle_id = StringType(deserialize_from="bundleId")
    object_versioning = StringType(deserialize_from="objectVersioning")
    readable_anonymous_access = BooleanType(deserialize_from="readableAnonymousAccess")
    access_rules = StringType(deserialize_from="accessRules")
    access_log_config = StringType(deserialize_from="accessLogConfig")
    transfer_acceleration = StringType(deserialize_from="transferAcceleration")
    resources_receiving_access = StringType(deserialize_from="resourcesReceivingAccess")
    state = StringType(
        deserialize_from="state",
        choices=(
            "pending",
            "available",
            "warning",
            "updating",
            "deleting",
            "deleted",
            "error",
        ),
    )
    url = StringType(deserialize_from="url")
