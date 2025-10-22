import logging
import concurrent.futures

from spaceone.inventory.plugin.collector.lib.server import CollectorPluginServer
from spaceone.inventory.plugin.collector.lib import make_error_response

from .manager.base import ResourceManager
from .manager.job_manager import JobManager

from .conf.cloud_service_conf import MAX_WORKERS

_LOGGER = logging.getLogger("spaceone")

app = CollectorPluginServer()


@app.route("Collector.init")
def collector_init(params: dict) -> dict:
    """init plugin by options

    Args:
        params (CollectorInitRequest): {
            'options': 'dict',    # Required
            'domain_id': 'str'
        }

    Returns:
        PluginResponse: {
            'metadata': 'dict'
        }
    """

    return {
        "metadata": {
            "supported_resource_type": [
                "inventory.CloudService",
                "inventory.CloudServiceType",
                "inventory.Region",
                "inventory.ErrorResource",
            ],
        }
    }


@app.route("Collector.verify")
def collector_verify(params: dict) -> None:
    """Verifying collector plugin

    Args:
        params (CollectorVerifyRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'schema': 'str',
            'domain_id': 'str'
        }

    Returns:
        None
    """
    pass


@app.route("Job.get_tasks")
def job_get_tasks(params: dict) -> dict:
    """Get job tasks

    Args:
        params (JobGetTaskRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'domain_id': 'str'
        }

    Returns:
        TasksResponse: {
            'tasks': 'list'
        }

    """
    options = params.get("options", {})
    secret_data = params.get("secret_data", {})

    job_mgr = JobManager(options, secret_data)
    return job_mgr.get_tasks()


@app.route("Collector.collect")
def collector_collect(params):
    """Collect external data

    Args:
        params (CollectorCollectRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'schema': 'str',
            'task_options': 'dict',
            'domain_id': 'str'
        }

    Returns:
        Generator[ResourceResponse, None, None]
        {
            'state': 'SUCCESS | FAILURE',
            'resource_type': 'inventory.CloudService | inventory.CloudServiceType | inventory.Region',
            'cloud_service_type': CloudServiceType,
            'cloud_service': CloudService,
            'region': Region,
            'match_keys': 'list',
            'error_message': 'str'
            'metadata': 'dict'
        }

        CloudServiceType
        {
            'name': 'str',           # Required
            'group': 'str',          # Required
            'provider': 'str',       # Required
            'is_primary': 'bool',
            'is_major': 'bool',
            'metadata': 'dict',      # Required
            'service_code': 'str',
            'tags': 'dict'
            'labels': 'list'
        }

        CloudService
        {
            'name': 'str',
            'cloud_service_type': 'str',  # Required
            'cloud_service_group': 'str', # Required
            'provider': 'str',            # Required
            'ip_addresses' : 'list',
            'account' : 'str',
            'instance_type': 'str',
            'instance_size': 'float',
            'region_code': 'str',
            'data': 'dict'               # Required
            'metadata': 'dict'           # Required
            'reference': 'dict'
            'tags' : 'dict'
        }

        Region
        {
            'name': 'str',
            'region_code': 'str',        # Required
            'provider': 'str',           # Required
            'tags': 'dict'
        }

        Only one of the cloud_service_type, cloud_service and region fields is required.
    """
    options = params["options"]
    secret_data = params["secret_data"]
    schema = params.get("schema")
    task_options = params.get("task_options", {})
    resource_type = task_options.get("resource_type")

    if resource_type == "inventory.CloudServiceType":
        services = task_options.get("services")
        for service in services:
            for manager_class in ResourceManager.get_manager_by_service(service):
                manager = manager_class()
                yield from manager.collect_cloudn_service_types()

    elif resource_type == "inventory.CloudService":
        service = task_options.get("service")
        region = task_options.get("region")
        account_id = ResourceManager.get_account_id(secret_data, region)
        options["account_id"] = account_id

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            manager_classes = list(ResourceManager.get_manager_by_service(service))

            futures = []
            for manager_class in manager_classes:
                future = executor.submit(
                    lambda mc: list(
                        mc().collect_resources(region, options, secret_data, schema)
                    ),
                    manager_class,
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    for item in result:
                        yield item
                except Exception as e:
                    _LOGGER.error(f"Error collecting resources: {e}")
                    yield make_error_response(
                        error=e,
                        provider="aws",
                        cloud_service_group=service,
                        cloud_service_type="",
                    )

    elif resource_type == "inventory.Region":
        regions = task_options.get("regions")
        for region in regions:
            yield ResourceManager.collect_region(region)

    elif resource_type == "inventory.Metric":
        services = task_options.get("services")
        for service in services:
            yield from ResourceManager.collect_metrics(service)
