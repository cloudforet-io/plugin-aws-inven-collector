import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Cluster(Model):
    cluster_arn = StringType(deserialize_from="ClusterArn")
    cluster_name = StringType(deserialize_from="ClusterName")
    creation_time = DateTimeType(deserialize_from="CreationTime")
    current_version = StringType(deserialize_from="CurrentVersion")
    state = StringType(
        deserialize_from="State",
        choices=(
            "ACTIVE",
            "CREATING",
            "DELETING",
            "FAILED",
            "HEALING",
            "MAINTENANCE",
            "REBOOTING_BROKER",
            "UPDATING",
        ),
    )
    state_info = StringType(deserialize_from="StateInfo")
    tags = StringType(deserialize_from="Tags")
    active_operation_arn = StringType(deserialize_from="ActiveOperationArn")
    cluster_type = StringType(
        deserialize_from="ClusterType", choices=("PROVISIONED", "SERVERLESS")
    )
    provisioned = StringType(deserialize_from="Provisioned")
    serverless = StringType(deserialize_from="Serverless")
