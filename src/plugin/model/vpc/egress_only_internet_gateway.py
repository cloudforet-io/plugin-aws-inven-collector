import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class EgressOnlyInternetGateway(Model):
    attachments = StringType(deserialize_from="Attachments")
    egress_only_internet_gateway_id = StringType(
        deserialize_from="EgressOnlyInternetGatewayId"
    )
    tags = StringType(deserialize_from="Tags")
