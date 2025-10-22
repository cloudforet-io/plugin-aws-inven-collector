import logging
from schematics import Model
from schematics.types import StringType, IntType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class Cluster(Model):
    cluster_arn = StringType(deserialize_from="clusterArn")
    cluster_name = StringType(deserialize_from="clusterName")
    status = StringType(deserialize_from="status")
    running_tasks_count = IntType(deserialize_from="runningTasksCount")
    pending_tasks_count = IntType(deserialize_from="pendingTasksCount")
    active_services_count = IntType(deserialize_from="activeServicesCount")
    registered_container_instances_count = IntType(
        deserialize_from="registeredContainerInstancesCount"
    )
    running_tasks_count = IntType(deserialize_from="runningTasksCount")
    pending_tasks_count = IntType(deserialize_from="pendingTasksCount")
    active_services_count = IntType(deserialize_from="activeServicesCount")
    registered_container_instances_count = IntType(
        deserialize_from="registeredContainerInstancesCount"
    )
    capacity_providers = ListType(StringType, deserialize_from="capacityProviders")
    default_capacity_provider_strategy = StringType(
        deserialize_from="defaultCapacityProviderStrategy"
    )
    tags = StringType(deserialize_from="Tags")
    settings = StringType(deserialize_from="settings")
    statistics = StringType(deserialize_from="statistics")
    attachments = StringType(deserialize_from="attachments")
    attachments_status = StringType(deserialize_from="attachmentsStatus")
    service_connect_defaults = StringType(deserialize_from="serviceConnectDefaults")
