import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class AccessKey(Model):
    user_name = StringType(deserialize_from="UserName")
    access_key_id = StringType(deserialize_from="AccessKeyId")
    status = StringType(deserialize_from="Status", choices=("Active", "Inactive"))
    secret_access_key = StringType(deserialize_from="SecretAccessKey")
    create_date = DateTimeType(deserialize_from="CreateDate")
