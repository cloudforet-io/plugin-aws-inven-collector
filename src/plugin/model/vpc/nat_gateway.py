import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class NATGateway(Model):
    create_time = DateTimeType(deserialize_from="CreateTime")
    delete_time = DateTimeType(deserialize_from="DeleteTime")
    failure_code = StringType(deserialize_from="FailureCode")
    failure_message = StringType(deserialize_from="FailureMessage")
    nat_gateway_addresses = StringType(deserialize_from="NatGatewayAddresses")
    nat_gateway_id = StringType(deserialize_from="NatGatewayId")
    provisioned_bandwidth = StringType(deserialize_from="ProvisionedBandwidth")
    state = StringType(
        deserialize_from="State",
        choices=("pending", "failed", "available", "deleting", "deleted"),
    )
    subnet_id = StringType(deserialize_from="SubnetId")
    vpc_id = StringType(deserialize_from="VpcId")
    tags = StringType(deserialize_from="Tags")
    connectivity_type = StringType(
        deserialize_from="ConnectivityType", choices=("private", "public")
    )
