import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class Group(Model):
    path = StringType(deserialize_from="Path")
    group_name = StringType(deserialize_from="GroupName")
    group_id = StringType(deserialize_from="GroupId")
    arn = StringType(deserialize_from="Arn")
    create_date = DateTimeType(deserialize_from="CreateDate")
    tags = StringType(deserialize_from="Tags")
