import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class SubnetGroup(Model):
    db_subnet_group_name = StringType(deserialize_from="DBSubnetGroupName")
    db_subnet_group_description = StringType(
        deserialize_from="DBSubnetGroupDescription"
    )
    vpc_id = StringType(deserialize_from="VpcId")
    subnet_group_status = StringType(deserialize_from="SubnetGroupStatus")
    subnets = StringType(deserialize_from="Subnets")
    db_subnet_group_arn = StringType(deserialize_from="DBSubnetGroupArn")
    supported_network_types = ListType(
        StringType, deserialize_from="SupportedNetworkTypes"
    )
