import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class CustomerGateway(Model):
    bgp_asn = StringType(deserialize_from="BgpAsn")
    customer_gateway_id = StringType(deserialize_from="CustomerGatewayId")
    ip_address = StringType(deserialize_from="IpAddress")
    certificate_arn = StringType(deserialize_from="CertificateArn")
    state = StringType(
        deserialize_from="State",
        choices=("pending", "available", "deleting", "deleted"),
    )
    type = StringType(deserialize_from="Type")
    device_name = StringType(deserialize_from="DeviceName")
    tags = StringType(deserialize_from="Tags")
