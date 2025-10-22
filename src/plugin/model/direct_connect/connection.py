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


class Connection(Model):
    owner_account = StringType(deserialize_from="ownerAccount")
    connection_id = StringType(deserialize_from="connectionId")
    connection_name = StringType(deserialize_from="connectionName")
    connection_state = StringType(
        deserialize_from="connectionState",
        choices=(
            "ordering",
            "requested",
            "pending",
            "available",
            "down",
            "deleting",
            "deleted",
            "rejected",
            "unknown",
        ),
    )
    region = StringType(deserialize_from="region")
    location = StringType(deserialize_from="location")
    bandwidth = StringType(deserialize_from="bandwidth")
    bandwidth_gbps = FloatType(serialize_when_none=False)
    vlan = IntType(deserialize_from="vlan")
    partner_name = StringType(deserialize_from="partnerName")
    loa_issue_time = DateTimeType(deserialize_from="loaIssueTime")
    lag_id = StringType(deserialize_from="lagId")
    aws_device = StringType(deserialize_from="awsDevice")
    jumbo_frame_capable = BooleanType(deserialize_from="jumboFrameCapable")
    aws_device_v2 = StringType(deserialize_from="awsDeviceV2")
    has_logical_redundancy = StringType(
        deserialize_from="hasLogicalRedundancy", choices=("unknown", "yes", "no")
    )
    tags = StringType(deserialize_from="Tags")
    provider_name = StringType(deserialize_from="providerName")
    mac_sec_capable = BooleanType(deserialize_from="macSecCapable")
    port_encryption_status = StringType(deserialize_from="portEncryptionStatus")
    encryption_mode = StringType(deserialize_from="encryptionMode")
    mac_sec_keys = StringType(deserialize_from="macSecKeys")
