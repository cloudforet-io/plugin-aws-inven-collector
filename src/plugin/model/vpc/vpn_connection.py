import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class VPNConnection(Model):
    customer_gateway_configuration = StringType(
        deserialize_from="CustomerGatewayConfiguration"
    )
    customer_gateway_id = StringType(deserialize_from="CustomerGatewayId")
    category = StringType(deserialize_from="Category")
    state = StringType(
        deserialize_from="State",
        choices=("pending", "available", "deleting", "deleted"),
    )
    type = StringType(deserialize_from="Type")
    vpn_connection_id = StringType(deserialize_from="VpnConnectionId")
    vpn_gateway_id = StringType(deserialize_from="VpnGatewayId")
    transit_gateway_id = StringType(deserialize_from="TransitGatewayId")
    core_network_arn = StringType(deserialize_from="CoreNetworkArn")
    core_network_attachment_arn = StringType(
        deserialize_from="CoreNetworkAttachmentArn"
    )
    gateway_association_state = StringType(deserialize_from="GatewayAssociationState")
    options = StringType(deserialize_from="Options")
    routes = StringType(deserialize_from="Routes")
    tags = StringType(deserialize_from="Tags")
    vgw_telemetry = StringType(deserialize_from="VgwTelemetry")
