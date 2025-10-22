import logging
from schematics import Model
from schematics.types import (
    StringType,
    IntType,
    DateTimeType,
    ListType,
    BooleanType,
    ModelType, DictType,
)

_LOGGER = logging.getLogger(__name__)


class Table(Model):
    table_name = StringType(deserialize_from="TableName")
    table_status = StringType(
        deserialize_from="TableStatus",
        choices=(
            "CREATING",
            "UPDATING",
            "DELETING",
            "ACTIVE",
            "INACCESSIBLE_ENCRYPTION_CREDENTIALS",
            "ARCHIVING",
            "ARCHIVED",
        ),
    )
    creation_date_time = DateTimeType(deserialize_from="CreationDateTime")
    table_size_bytes = IntType(deserialize_from="TableSizeBytes")
    item_count = IntType(deserialize_from="ItemCount")
    table_arn = StringType(deserialize_from="TableArn")
    table_id = StringType(deserialize_from="TableId")
    billing_mode_summary = StringType(deserialize_from="BillingModeSummary")
    local_secondary_indexes = StringType(deserialize_from="LocalSecondaryIndexes")
    global_secondary_indexes = StringType(deserialize_from="GlobalSecondaryIndexes")
    stream_specification = StringType(deserialize_from="StreamSpecification")
    sse_description = StringType(deserialize_from="SSEDescription")
    tags = StringType(deserialize_from="Tags")
    cloudwatch = DictType(StringType, deserialize_from="cloudwatch")
    cloudtrail = DictType(StringType, deserialize_from="cloudtrail")
