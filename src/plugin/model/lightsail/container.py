import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Container(Model):
    container_service_name = StringType(deserialize_from="containerServiceName")
    arn = StringType(deserialize_from="arn")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    power = StringType(deserialize_from="power")
    power_id = StringType(deserialize_from="powerId")
    state = StringType(
        deserialize_from="state",
        choices=(
            "PENDING",
            "READY",
            "RUNNING",
            "UPDATING",
            "DELETING",
            "DISABLED",
            "DEPLOYING",
        ),
    )
    scale = IntType(deserialize_from="scale")
    current_deployment = StringType(deserialize_from="currentDeployment")
    next_deployment = StringType(deserialize_from="nextDeployment")
    is_disabled = BooleanType(deserialize_from="isDisabled")
    principal_arn = StringType(deserialize_from="principalArn")
    private_domain_name = StringType(deserialize_from="privateDomainName")
    public_domain_names = StringType(deserialize_from="publicDomainNames")
    url = StringType(deserialize_from="url")
    private_registry_access = StringType(deserialize_from="privateRegistryAccess")
