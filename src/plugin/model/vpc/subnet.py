import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Subnet(Model):
    availability_zone = StringType(deserialize_from="AvailabilityZone")
    availability_zone_id = StringType(deserialize_from="AvailabilityZoneId")
    available_ip_address_count = IntType(deserialize_from="AvailableIpAddressCount")
    cidr_block = StringType(deserialize_from="CidrBlock")
    default_for_az = BooleanType(deserialize_from="DefaultForAz")
    enable_lni_at_device_index = IntType(deserialize_from="EnableLniAtDeviceIndex")
    map_public_ip_on_launch = BooleanType(deserialize_from="MapPublicIpOnLaunch")
    map_customer_owned_ip_on_launch = BooleanType(
        deserialize_from="MapCustomerOwnedIpOnLaunch"
    )
    customer_owned_ipv4_pool = StringType(deserialize_from="CustomerOwnedIpv4Pool")
    state = StringType(deserialize_from="State", choices=("pending", "available"))
    subnet_id = StringType(deserialize_from="SubnetId")
    vpc_id = StringType(deserialize_from="VpcId")
    owner_id = StringType(deserialize_from="OwnerId")
    assign_ipv6_address_on_creation = BooleanType(
        deserialize_from="AssignIpv6AddressOnCreation"
    )
    ipv6_cidr_block_association_set = StringType(
        deserialize_from="Ipv6CidrBlockAssociationSet"
    )
    tags = StringType(deserialize_from="Tags")
    subnet_arn = StringType(deserialize_from="SubnetArn")
    outpost_arn = StringType(deserialize_from="OutpostArn")
    enable_dns64 = BooleanType(deserialize_from="EnableDns64")
    ipv6_native = BooleanType(deserialize_from="Ipv6Native")
    private_dns_name_options_on_launch = StringType(
        deserialize_from="PrivateDnsNameOptionsOnLaunch"
    )
