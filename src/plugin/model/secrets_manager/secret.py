import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Secret(Model):
    arn = StringType(deserialize_from="ARN")
    name = StringType(deserialize_from="Name")
    description = StringType(deserialize_from="Description")
    kms_key_id = StringType(deserialize_from="KmsKeyId")
    rotation_enabled = BooleanType(deserialize_from="RotationEnabled")
    rotation_lambda_arn = StringType(deserialize_from="RotationLambdaARN")
    rotation_rules = StringType(deserialize_from="RotationRules")
    last_rotated_date = DateTimeType(deserialize_from="LastRotatedDate")
    last_changed_date = DateTimeType(deserialize_from="LastChangedDate")
    last_accessed_date = DateTimeType(deserialize_from="LastAccessedDate")
    deleted_date = DateTimeType(deserialize_from="DeletedDate")
    next_rotation_date = DateTimeType(deserialize_from="NextRotationDate")
    tags = StringType(deserialize_from="Tags")
    secret_versions_to_stages = StringType(deserialize_from="SecretVersionsToStages")
    owning_service = StringType(deserialize_from="OwningService")
    created_date = DateTimeType(deserialize_from="CreatedDate")
    primary_region = StringType(deserialize_from="PrimaryRegion")
    replication_status = StringType(deserialize_from="ReplicationStatus")
