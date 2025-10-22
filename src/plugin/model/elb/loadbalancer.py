import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class LoadBalancer(Model):
    load_balancer_arn = StringType(deserialize_from="LoadBalancerArn")
    dns_name = StringType(deserialize_from="DNSName")
    canonical_hosted_zone_id = StringType(deserialize_from="CanonicalHostedZoneId")
    created_time = DateTimeType(deserialize_from="CreatedTime")
    load_balancer_name = StringType(deserialize_from="LoadBalancerName")
    scheme = StringType(
        deserialize_from="Scheme", choices=("internet-facing", "internal")
    )
    vpc_id = StringType(deserialize_from="VpcId")
    state = StringType(deserialize_from="State")
    type = StringType(
        deserialize_from="Type", choices=("application", "network", "gateway")
    )
    availability_zones = StringType(deserialize_from="AvailabilityZones")
    security_groups = ListType(StringType, deserialize_from="SecurityGroups")
    ip_address_type = StringType(
        deserialize_from="IpAddressType", choices=("ipv4", "dualstack")
    )
    customer_owned_ipv4_pool = StringType(deserialize_from="CustomerOwnedIpv4Pool")
    tags = StringType(deserialize_from="Tags")
