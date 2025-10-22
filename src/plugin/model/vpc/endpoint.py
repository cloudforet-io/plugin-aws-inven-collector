import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Endpoint(Model):
    vpc_endpoint_id = StringType(deserialize_from="VpcEndpointId")
    vpc_endpoint_type = StringType(
        deserialize_from="VpcEndpointType",
        choices=("Interface", "Gateway", "GatewayLoadBalancer"),
    )
    vpc_id = StringType(deserialize_from="VpcId")
    service_name = StringType(deserialize_from="ServiceName")
    state = StringType(
        deserialize_from="State",
        choices=(
            "PendingAcceptance",
            "Pending",
            "Available",
            "Deleting",
            "Deleted",
            "Rejected",
            "Failed",
            "Expired",
        ),
    )
    policy_document = StringType(deserialize_from="PolicyDocument")
    route_table_ids = ListType(StringType, deserialize_from="RouteTableIds")
    subnet_ids = ListType(StringType, deserialize_from="SubnetIds")
    groups = StringType(deserialize_from="Groups")
    ip_address_type = StringType(deserialize_from="IpAddressType")
    dns_options = StringType(deserialize_from="DnsOptions")
    private_dns_enabled = BooleanType(deserialize_from="PrivateDnsEnabled")
    requester_managed = BooleanType(deserialize_from="RequesterManaged")
    network_interface_ids = ListType(StringType, deserialize_from="NetworkInterfaceIds")
    dns_entries = StringType(deserialize_from="DnsEntries")
    creation_timestamp = DateTimeType(deserialize_from="CreationTimestamp")
    tags = StringType(deserialize_from="Tags")
    owner_id = StringType(deserialize_from="OwnerId")
    last_error = StringType(deserialize_from="LastError")
