import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class DataStream(Model):
    stream_name = StringType(deserialize_from="StreamName")
    stream_arn = StringType(deserialize_from="StreamARN")
    stream_status = StringType(
        deserialize_from="StreamStatus",
        choices=("CREATING", "DELETING", "ACTIVE", "UPDATING"),
    )
    retention_period_hours = IntType(deserialize_from="RetentionPeriodHours")
    enhanced_monitoring = StringType(deserialize_from="EnhancedMonitoring")
    encryption_type = StringType(
        deserialize_from="EncryptionType", choices=("NONE", "KMS")
    )
    key_id = StringType(deserialize_from="KeyId")
    open_shard_count = IntType(deserialize_from="OpenShardCount")
    consumer_count = IntType(deserialize_from="ConsumerCount")
    tags = StringType(deserialize_from="Tags")
