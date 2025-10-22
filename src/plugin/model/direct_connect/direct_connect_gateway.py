import logging
from schematics import Model
from schematics.types import StringType, ListType

_LOGGER = logging.getLogger(__name__)


class DirectConnectGateway(Model):
    direct_connect_gateway_id = StringType(deserialize_from="directConnectGatewayId")
    direct_connect_gateway_name = StringType(
        deserialize_from="directConnectGatewayName"
    )
    amazon_side_asn = StringType(deserialize_from="amazonSideAsn")
    owner_account = StringType(deserialize_from="ownerAccount")
    direct_connect_gateway_state = StringType(
        deserialize_from="directConnectGatewayState",
        choices=("pending", "available", "deleting", "deleted"),
    )
    state_change_error = StringType(deserialize_from="stateChangeError")
    tags = StringType(deserialize_from="Tags")
