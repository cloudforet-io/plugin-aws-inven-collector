import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class Cluster(Model):
    name = StringType(deserialize_from="name")
    arn = StringType(deserialize_from="arn")
    created_at = DateTimeType(deserialize_from="createdAt")
    version = StringType(deserialize_from="version")
    endpoint = StringType(deserialize_from="endpoint")
    role_arn = StringType(deserialize_from="roleArn")
    resources_vpc_config = StringType(deserialize_from="resourcesVpcConfig")
    kubernetes_network_config = StringType(deserialize_from="kubernetesNetworkConfig")
    logging = StringType(deserialize_from="logging")
    identity = StringType(deserialize_from="identity")
    status = StringType(
        deserialize_from="status",
        choices=("CREATING", "ACTIVE", "DELETING", "FAILED", "UPDATING"),
    )
    certificate_authority = StringType(deserialize_from="certificateAuthority")
    client_request_token = StringType(deserialize_from="clientRequestToken")
    platform_version = StringType(deserialize_from="platformVersion")
    tags = StringType(deserialize_from="Tags")
    encryption_config = StringType(deserialize_from="encryptionConfig")
    connector_config = StringType(deserialize_from="connectorConfig")
    id = StringType(deserialize_from="id")
    health = StringType(deserialize_from="health")
    outpost_config = StringType(deserialize_from="outpostConfig")
    access_config = StringType(deserialize_from="accessConfig")
