import logging
from schematics import Model
from schematics.types import StringType, ListType

_LOGGER = logging.getLogger(__name__)


class VirtualPrivateGateway(Model):
    virtual_gateway_id = StringType(deserialize_from="virtualGatewayId")
    virtual_gateway_state = StringType(deserialize_from="virtualGatewayState")
    tags = StringType(deserialize_from="Tags")
