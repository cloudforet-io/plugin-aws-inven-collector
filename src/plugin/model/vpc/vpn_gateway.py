import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class VPNGateway(Model):
    availability_zone = StringType(deserialize_from="AvailabilityZone")
    state = StringType(
        deserialize_from="State",
        choices=("pending", "available", "deleting", "deleted"),
    )
    type = StringType(deserialize_from="Type")
    vpc_attachments = StringType(deserialize_from="VpcAttachments")
    vpn_gateway_id = StringType(deserialize_from="VpnGatewayId")
    amazon_side_asn = IntType(deserialize_from="AmazonSideAsn")
    tags = StringType(deserialize_from="Tags")
