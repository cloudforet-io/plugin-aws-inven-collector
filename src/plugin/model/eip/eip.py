import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class EIP(Model):
    public_ip = StringType(deserialize_from="PublicIp")
    allocation_id = StringType(deserialize_from="AllocationId")
    association_id = StringType(deserialize_from="AssociationId")
    domain = StringType(deserialize_from="Domain", choices=("vpc", "standard"))
    network_interface_id = StringType(deserialize_from="NetworkInterfaceId")
    network_interface_owner_id = StringType(deserialize_from="NetworkInterfaceOwnerId")
    private_ip_address = StringType(deserialize_from="PrivateIpAddress")
    public_ipv4_pool = StringType(deserialize_from="PublicIpv4Pool")
    network_border_group = StringType(deserialize_from="NetworkBorderGroup")
    customer_owned_ip = StringType(deserialize_from="CustomerOwnedIp")
    customer_owned_ipv4_pool = StringType(deserialize_from="CustomerOwnedIpv4Pool")
    carrier_ip = StringType(deserialize_from="CarrierIp")
    tags = StringType(deserialize_from="Tags")
