import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class VPC(Model):
    cidr_block = StringType(deserialize_from="CidrBlock")
    dhcp_options_id = StringType(deserialize_from="DhcpOptionsId")
    state = StringType(deserialize_from="State", choices=("pending", "available"))
    vpc_id = StringType(deserialize_from="VpcId")
    owner_id = StringType(deserialize_from="OwnerId")
    instance_tenancy = StringType(
        deserialize_from="InstanceTenancy", choices=("default", "dedicated", "host")
    )
    ipv6_cidr_block_association_set = StringType(
        deserialize_from="Ipv6CidrBlockAssociationSet"
    )
    cidr_block_association_set = StringType(deserialize_from="CidrBlockAssociationSet")
    is_default = BooleanType(deserialize_from="IsDefault")
    tags = StringType(deserialize_from="Tags")
