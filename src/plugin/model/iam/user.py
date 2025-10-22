import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class User(Model):
    path = StringType(deserialize_from="Path")
    user_name = StringType(deserialize_from="UserName")
    user_id = StringType(deserialize_from="UserId")
    arn = StringType(deserialize_from="Arn")
    create_date = DateTimeType(deserialize_from="CreateDate")
    password_last_used = DateTimeType(deserialize_from="PasswordLastUsed")
    permissions_boundary = StringType(deserialize_from="PermissionsBoundary")
    tags = StringType(deserialize_from="Tags")
