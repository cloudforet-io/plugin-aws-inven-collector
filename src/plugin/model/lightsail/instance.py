import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Instance(Model):
    name = StringType(deserialize_from="name")
    arn = StringType(deserialize_from="arn")
    support_code = StringType(deserialize_from="supportCode")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    blueprint_id = StringType(deserialize_from="blueprintId")
    blueprint_name = StringType(deserialize_from="blueprintName")
    bundle_id = StringType(deserialize_from="bundleId")
    add_ons = StringType(deserialize_from="addOns")
    is_static_ip = BooleanType(deserialize_from="isStaticIp")
    private_ip_address = StringType(deserialize_from="privateIpAddress")
    public_ip_address = StringType(deserialize_from="publicIpAddress")
    ip_address_type = StringType(deserialize_from="ipAddressType")
    ipv6_addresses = ListType(StringType, deserialize_from="ipv6Addresses")
    key_pair_name = StringType(deserialize_from="keyPairName")
    networking = StringType(deserialize_from="networking")
    state = StringType(
        deserialize_from="state",
        choices=(
            "pending",
            "running",
            "stopping",
            "stopped",
            "starting",
            "rebooting",
            "shutting-down",
            "terminated",
        ),
    )
    username = StringType(deserialize_from="username")
    ssh_key_name = StringType(deserialize_from="sshKeyName")
    metadata_options = StringType(deserialize_from="metadataOptions")
    hardware = StringType(deserialize_from="hardware")
