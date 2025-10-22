import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class NodeGroup(Model):
    nodegroup_name = StringType(deserialize_from="nodegroupName")
    nodegroup_arn = StringType(deserialize_from="nodegroupArn")
    cluster_name = StringType(deserialize_from="clusterName")
    version = StringType(deserialize_from="version")
    release_version = StringType(deserialize_from="releaseVersion")
    created_at = DateTimeType(deserialize_from="createdAt")
    modified_at = DateTimeType(deserialize_from="modifiedAt")
    status = StringType(
        deserialize_from="status",
        choices=(
            "CREATING",
            "ACTIVE",
            "UPDATING",
            "DELETING",
            "CREATE_FAILED",
            "DELETE_FAILED",
            "DEGRADED",
        ),
    )
    capacity_type = StringType(
        deserialize_from="capacityType", choices=("ON_DEMAND", "SPOT")
    )
    scaling_config = StringType(deserialize_from="scalingConfig")
    instance_types = ListType(StringType, deserialize_from="instanceTypes")
    ami_type = StringType(
        deserialize_from="amiType",
        choices=(
            "AL2_x86_64",
            "AL2_x86_64_GPU",
            "AL2_ARM_64",
            "CUSTOM",
            "BOTTLEROCKET_ARM_64",
            "BOTTLEROCKET_x86_64",
            "BOTTLEROCKET_ARM_64_NVIDIA",
            "BOTTLEROCKET_x86_64_NVIDIA",
            "WINDOWS_CORE_2019_x86_64",
            "WINDOWS_FULL_2019_x86_64",
            "WINDOWS_CORE_2022_x86_64",
            "WINDOWS_FULL_2022_x86_64",
        ),
    )
    operating_system = StringType(
        deserialize_from="operatingSystem",
        choices=("Amazon Linux 2", "Windows", "Bottlerocket"),
    )
    node_role = StringType(deserialize_from="nodeRole")
    labels = StringType(deserialize_from="labels")
    taints = StringType(deserialize_from="taints")
    resources = StringType(deserialize_from="resources")
    disk_size = IntType(deserialize_from="diskSize")
    health = StringType(deserialize_from="health")
    update_config = StringType(deserialize_from="updateConfig")
    launch_template = StringType(deserialize_from="launchTemplate")
    tags = StringType(deserialize_from="Tags")
    remote_access = StringType(deserialize_from="remoteAccess")
