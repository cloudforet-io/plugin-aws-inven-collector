import logging
from schematics import Model
from schematics.types import (
    StringType,
    IntType,
    FloatType,
    DateTimeType,
    ListType,
    BooleanType,
)

_LOGGER = logging.getLogger(__name__)


class LAG(Model):
    connections_bandwidth = StringType(deserialize_from="connectionsBandwidth")
    number_of_connections = IntType(deserialize_from="numberOfConnections")
    lag_id = StringType(deserialize_from="lagId")
    owner_account = StringType(deserialize_from="ownerAccount")
    lag_name = StringType(deserialize_from="lagName")
    lag_state = StringType(
        deserialize_from="lagState",
        choices=(
            "requested",
            "pending",
            "available",
            "down",
            "deleting",
            "deleted",
            "unknown",
        ),
    )
    location = StringType(deserialize_from="location")
    region = StringType(deserialize_from="region")
    minimum_links = IntType(deserialize_from="minimumLinks")
    aws_device = StringType(deserialize_from="awsDevice")
    aws_device_v2 = StringType(deserialize_from="awsDeviceV2")
    connections = StringType(deserialize_from="connections")
    allows_hosted_connections = BooleanType(deserialize_from="allowsHostedConnections")
    jumbo_frame_capable = BooleanType(deserialize_from="jumboFrameCapable")
    has_logical_redundancy = StringType(
        deserialize_from="hasLogicalRedundancy", choices=("unknown", "yes", "no")
    )
    tags = StringType(deserialize_from="Tags")
    provider_name = StringType(deserialize_from="providerName")
    mac_sec_capable = BooleanType(deserialize_from="macSecCapable")
    encryption_mode = StringType(deserialize_from="encryptionMode")
    mac_sec_keys = StringType(deserialize_from="macSecKeys")
