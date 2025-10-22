import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class ParameterGroup(Model):
    db_parameter_group_name = StringType(deserialize_from="DBParameterGroupName")
    db_parameter_group_family = StringType(deserialize_from="DBParameterGroupFamily")
    description = StringType(deserialize_from="Description")
    db_parameter_group_arn = StringType(deserialize_from="DBParameterGroupArn")
