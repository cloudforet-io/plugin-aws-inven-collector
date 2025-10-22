import logging
from schematics import Model
from schematics.types import StringType, ListType, DictType

_LOGGER = logging.getLogger(__name__)


class ParameterGroup(Model):
    db_cluster_parameter_group_name = StringType(
        deserialize_from="DBClusterParameterGroupName"
    )
    db_parameter_group_family = StringType(deserialize_from="DBParameterGroupFamily")
    description = StringType(deserialize_from="Description")
    db_cluster_parameter_group_arn = StringType(
        deserialize_from="DBClusterParameterGroupArn"
    )
    tags = StringType(deserialize_from="Tags")
    parameters = ListType(DictType, deserialize_from="parameters")
    cloudtrail = DictType(StringType, deserialize_from="cloudtrail")
