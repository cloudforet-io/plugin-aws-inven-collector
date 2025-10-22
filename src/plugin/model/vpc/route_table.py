import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class RouteTable(Model):
    associations = StringType(deserialize_from="Associations")
    propagating_vgws = StringType(deserialize_from="PropagatingVgws")
    route_table_id = StringType(deserialize_from="RouteTableId")
    routes = StringType(deserialize_from="Routes")
    tags = StringType(deserialize_from="Tags")
    vpc_id = StringType(deserialize_from="VpcId")
    owner_id = StringType(deserialize_from="OwnerId")
