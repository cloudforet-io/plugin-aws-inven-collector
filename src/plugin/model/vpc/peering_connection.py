import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class PeeringConnection(Model):
    accepter_vpc_info = StringType(deserialize_from="AccepterVpcInfo")
    expiration_time = DateTimeType(deserialize_from="ExpirationTime")
    requester_vpc_info = StringType(deserialize_from="RequesterVpcInfo")
    status = StringType(deserialize_from="Status")
    tags = StringType(deserialize_from="Tags")
    vpc_peering_connection_id = StringType(deserialize_from="VpcPeeringConnectionId")
