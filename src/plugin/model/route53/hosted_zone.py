import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class HostedZone(Model):
    id = StringType(deserialize_from="Id")
    name = StringType(deserialize_from="Name")
    caller_reference = StringType(deserialize_from="CallerReference")
    config = StringType(deserialize_from="Config")
    resource_record_set_count = IntType(deserialize_from="ResourceRecordSetCount")
    linked_service = StringType(deserialize_from="LinkedService")
