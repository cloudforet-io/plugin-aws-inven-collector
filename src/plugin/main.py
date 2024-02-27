import logging
from spaceone.inventory.plugin.collector.lib.server import CollectorPluginServer
from .manager.base import ResourceManager

_LOGGER = logging.getLogger("cloudforet")

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
    """
    Conf variable 굳이..?
    supported_features? 
    supported_schedules?
    options_schema 새로 받을 것 (설민님과 상의)
    """
    return _create_init_metadata()


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

    resource_type = options.get("resource_type")

    if resource_type == "inventory.CloudServiceType":
        services = options.get("services")
        for service in services:
            resource_mgrs = ResourceManager.get_manager_by_service(service)
            for resource_mgr in resource_mgrs:
                results = resource_mgr().collect_cloud_service_types()
                for result in results:
                    yield result

    elif resource_type == "inventory.CloudService":
        service = options.get("service")
        region = options.get("region")
        resource_mgrs = ResourceManager.get_manager_by_service(service)
        resource_exists = False
        for resource_mgr in resource_mgrs:
            results = resource_mgr().collect_resources(
                region, options, secret_data, schema
            )
            for result in results:
                resource_exists = True
                yield result

        if resource_exists:
            yield ResourceManager.collect_region(region)
    else:
        raise ValueError("Invalid resource type!")


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
    tasks = []
    options = params.get("options", {})
    secret_data = params.get("secret_data", {})
    services = _set_service_filter(options)
    regions = _set_region_filter(options, secret_data)

    # create task 1: task for collecting only cloud service type metadata
    tasks.extend(_add_cloud_service_type_tasks(services))

    # create task 2: task for collecting only cloud service region metadata
    # Commented out for now
    # tasks.extend(_add_cloud_service_region_tasks(regions))

    # create task 3: task for collecting only cloud service group metadata
    tasks.extend(_add_cloud_service_group_tasks(services, regions))

    return {"tasks": tasks}


def _set_service_filter(options):
    """
    1. service_filter type check (is it an array?)
    2. service_filter 내용물 자체 check (it could have sth that is not valid, like ECD instead of EC2
    """

    available_services = ResourceManager.get_service_names()

    if service_filter := options.get("service_filter"):
        _validate_service_filter(service_filter, available_services)
        return service_filter
    else:
        return available_services


def _validate_service_filter(service_filter, available_services):
    if not isinstance(service_filter, list):
        raise ValueError(
            f"Services input is supposed to be a list type! Your input is {service_filter}."
        )
    for each_service in service_filter:
        if each_service not in available_services:
            raise ValueError("Not a valid service!")


def _set_region_filter(options, secret_data):
    available_regions = ResourceManager.get_region_names(secret_data)

    if region_filter := options.get("region_filter"):
        _validate_region_filter(region_filter, available_regions)
        return region_filter
    else:
        return available_regions


def _validate_region_filter(region_filter, available_regions):
    if not isinstance(region_filter, list):
        raise ValueError(
            f"Regions input is supposed to be a list type! Your input is {region_filter}."
        )
    for each_region in region_filter:
        if each_region not in available_regions:
            raise ValueError("Not a valid region!")


def _add_cloud_service_type_tasks(services: list) -> list:
    return [
        _make_task_wrapper(
            resource_type="inventory.CloudServiceType", services=services
        )
    ]


def _add_cloud_service_region_tasks(regions: list) -> list:
    return [_make_task_wrapper(resource_type="inventory.Region", regions=regions)]


def _add_cloud_service_group_tasks(services, regions):
    tasks = []
    """
    TODO: Certain services are not available in certain regions.
    
    """
    for service in services:
        for region in regions:
            tasks.append(
                _make_task_wrapper(
                    resource_type="inventory.CloudService",
                    service=service,
                    region=region,
                )
            )
    return tasks


def _make_task_wrapper(**kwargs) -> dict:
    task_options = {"task_options": {}}
    for key, value in kwargs.items():
        task_options["task_options"][key] = value
    return task_options


def _create_init_metadata():
    return {
        "metadata": {
            "supported_resource_type": [
                "inventory.CloudService",
                "inventory.CloudServiceType",
                "inventory.Region",
                "inventory.ErrorResource",
            ],
            "options_schema": {},
        }
    }
