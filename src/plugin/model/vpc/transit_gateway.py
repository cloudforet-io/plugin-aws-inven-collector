import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class TransitGateway(Model):
    transit_gateway_id = StringType(deserialize_from="TransitGatewayId")
    transit_gateway_arn = StringType(deserialize_from="TransitGatewayArn")
    state = StringType(
        deserialize_from="State",
        choices=("pending", "available", "modifying", "deleting", "deleted"),
    )
    owner_id = StringType(deserialize_from="OwnerId")
    description = StringType(deserialize_from="Description")
    creation_time = DateTimeType(deserialize_from="CreationTime")
    options = StringType(deserialize_from="Options")
    tags = StringType(deserialize_from="Tags")
