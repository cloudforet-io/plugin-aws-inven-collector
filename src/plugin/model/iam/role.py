import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class Role(Model):
    path = StringType(deserialize_from="Path")
    role_name = StringType(deserialize_from="RoleName")
    role_id = StringType(deserialize_from="RoleId")
    arn = StringType(deserialize_from="Arn")
    create_date = DateTimeType(deserialize_from="CreateDate")
    assume_role_policy_document = StringType(
        deserialize_from="AssumeRolePolicyDocument"
    )
    description = StringType(deserialize_from="Description")
    max_session_duration = IntType(deserialize_from="MaxSessionDuration")
    permissions_boundary = StringType(deserialize_from="PermissionsBoundary")
    tags = StringType(deserialize_from="Tags")
    role_last_used = StringType(deserialize_from="RoleLastUsed")
