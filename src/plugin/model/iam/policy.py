import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class Policy(Model):
    policy_name = StringType(deserialize_from="PolicyName")
    policy_id = StringType(deserialize_from="PolicyId")
    arn = StringType(deserialize_from="Arn")
    path = StringType(deserialize_from="Path")
    default_version_id = StringType(deserialize_from="DefaultVersionId")
    attachment_count = IntType(deserialize_from="AttachmentCount")
    permissions_boundary_usage_count = IntType(
        deserialize_from="PermissionsBoundaryUsageCount"
    )
    is_attachable = BooleanType(deserialize_from="IsAttachable")
    description = StringType(deserialize_from="Description")
    create_date = DateTimeType(deserialize_from="CreateDate")
    update_date = DateTimeType(deserialize_from="UpdateDate")
    tags = StringType(deserialize_from="Tags")
