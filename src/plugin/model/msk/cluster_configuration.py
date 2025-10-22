import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class ClusterConfiguration(Model):
    arn = StringType(deserialize_from="Arn")
    creation_time = DateTimeType(deserialize_from="CreationTime")
    description = StringType(deserialize_from="Description")
    kafka_versions = ListType(StringType, deserialize_from="KafkaVersions")
    latest_revision = StringType(deserialize_from="LatestRevision")
    name = StringType(deserialize_from="Name")
    state = StringType(
        deserialize_from="State", choices=("ACTIVE", "DELETING", "DELETE_FAILED")
    )
