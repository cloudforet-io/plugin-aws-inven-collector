import json
import logging
from spaceone.core.service import check_required, transaction
from spaceone.inventory.plugin.collector.lib.server import CollectorPluginServer
from .conf.cloud_service_conf import *
from .connector.base import ResourceConnector
from .connector.collector_connector import CollectorConnector
from .manager.base import ResourceManager
from .manager.cloud_service_manager import CloudServiceManager
from .manager.collector_manager import CollectorManager
from .manager.ec2 import EC2Manager
from .manager.region_manager import RegionManager

_LOGGER = logging.getLogger('cloudforet')

app = CollectorPluginServer()


# def collect_cloud_service_type_data(manager, params):
#     options = params.get('options')
#     services = options.get('services')
#     if not services:
#         raise ValueError('Must have a list of targeted services!')
#     for cloud_service_group in services:
#         for cloud_service_type in manager.list_cloud_service_types(cloud_service_group):
#             yield {'resource': cloud_service_type}
#
#
# def collect_region_data(manager, params):
#     '''
#         원래 알고리즘은 모든 데이터를 collect한 후에 데이터가 존재했던 region들의 metadata만을 추가했고, 추가적으로
#         해당 region에 대해 데이터 수집이 Success 인지 Failure인지도 체크했다.
#
#         현재 알고리즘은 해당 region에 대한 metadata를 모든 데이터 수집 완료여부랑 관계없이 따로 수집하는 알고리즘인데,
#         이게 맞는 방향성인지..?
#     '''
#     options = params.get('options')
#     regions = options.get('regions')
#     if not regions:
#         raise ValueError('Must have a list of targeted regions!')
#     for cloud_service_region in regions:
#         pass
#
#
# def collect_cloud_service_data(manager, params):
#     options = params.get('options')
#     service, region = options.get('service'), options.get('region')
#     if not region or not service:
#         raise ValueError('Must have both target service and region!')
#     target_resources = manager.collect_resources(**params)
#     for each_resource in target_resources:
#         try:
#             # if getattr(each_resource, 'resource', None) and getattr(each_resource.resource, 'region_code', None):
#             #     collected_region = self.get_region_from_result(each_resource.resource.region_code)
#             #
#             #     if collected_region and collected_region.resource.region_code not in collected_region_code:
#             #         resource_regions.append(collected_region)
#             #         collected_region_code.append(collected_region.resource.region_code)
#             pass
#         except Exception as e:
#             _LOGGER.error(f'[collect] {e}')
#
#             if type(e) is dict:
#                 error_resource_response = {'message': json.dumps(e),
#                                            'resource': {'resource_type': 'inventory.CloudService'}}
#             else:
#                 error_resource_response = {'message': str(e), 'resource': {'resource_type': 'inventory.CloudService'}}
#
#             yield error_resource_response
#
#         yield each_resource
#
#
# RESOURCE_TYPE_MAP = {
#     'inventory.CloudServiceType': collect_cloud_service_type_data,
#     'inventory.Region': collect_region_data,
#     'inventory.CloudService': collect_cloud_service_data
# }


@app.route('Collector.init')
def collector_init(params: dict) -> dict:
    """ init plugin by options

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
    '''
    Conf variable 굳이..?
    supported_features? 
    supported_schedules?
    options_schema 새로 받을 것 (설민님과 상의)
    '''
    return _create_init_metadata()


@app.route('Collector.verify')
def collector_verify(params: dict) -> None:
    """ Verifying collector plugin

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
    collector_mgr = CollectorManager()
    secret_data = params['secret_data']
    # collector_mgr.create_session(secret_data)


@app.route('Collector.collect')
def collector_collect(params):
    """ Collect external data

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

    task_options = params.get('task_options', {})
    resource_type = options.get('resource_type')

    # if services := options.get("cloud_service_types"):
    #     for service in services:
    #         resource_mgrs = ResourceManager.get_manager_by_service(service)
    #         for resource_mgr in resource_mgrs:
    #             results = resource_mgr().collect_resources(options, secret_data, schema)
    #             for result in results:
    #                 yield result
    # else:
    #     resource_mgrs = ResourceManager.list_managers()
    #     for manager in resource_mgrs:
    #         results = manager().collect_resources(options, secret_data, schema)
    #
    #         for result in results:
    #             yield result
    if resource_type == 'inventory.Region':
        return
    elif resource_type == 'inventory.CloudService':
        service = options.get('service')
        region = options.get('region')
        resource_mgrs = ResourceManager.get_manager_by_service(service)
        for resource_mgr in resource_mgrs:
            service_type = resource_mgr.cloud_service_type
            results = resource_mgr().collect_resources(service, service_type, region, options, secret_data, schema)
            for result in results:
                yield result
    #     service = task_options.get('service')
    #     region = task_options.get('region')
    #     print("CONNECTOR HERE IS ")
    #     # collector_manager.set_connector(service)
    #     # collector_manager.create_session(secret_data, region)
    #     # managers = CollectorManager.get_service_type_managers(service)
    #     print("AM I HERE?")
    #
    #     #return collector_manager.collect_resources(options, secret_data, schema, task_options)
    #     # for manager in managers:
    #     #     manager_instance = manager()
    #     #     for resource in manager_instance.collect(options, secret_data, schema, task_options):
    #     #         print(resource)
    #     #         #yield resource
    #
    #
    # else:
    #     raise ValueError('Invalid resource type!')


@app.route('Job.get_tasks')
@check_required(['options', 'secret_data'])
def job_get_tasks(params: dict) -> dict:
    """ Get job tasks

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
    options = params.get('options', {})

    services = _set_service_filter(options)
    regions = _set_region_filter(options, params)

    # create task 1: task for collecting only cloud service type metadata
    tasks.extend(_add_cloud_service_type_tasks(services))

    # create task 2: task for collecting only cloud service region metadata
    tasks.extend(_add_cloud_service_region_tasks(regions))

    # create task 3: task for collecting only cloud service group metadata
    tasks.extend(_add_cloud_service_group_tasks(services, regions))

    return {'tasks': tasks}


def _set_service_filter(options):
    '''
    1. service_filter type check (is it an array?)
    2. service_filter 내용물 자체 check (it could have sth that is not valid, like ECD instead of EC2
    '''

    available_services = CloudServiceManager.get_service_names()

    if service_filter := options.get('service_filter'):
        _validate_service_filter(service_filter, available_services)
        return service_filter
    else:
        return available_services


def _validate_service_filter(service_filter, available_services):
    if not isinstance(service_filter, list):
        raise ValueError(f'Services input is supposed to be a list type! Your input is {service_filter}.')
    for each_service in service_filter:
        if each_service not in available_services:
            raise ValueError('Not a valid service!')


def _set_region_filter(options, params):
    _manager = RegionManager()
    available_regions = _manager.get_region_names()

    if region_filter := options.get('region_filter'):
        _validate_region_filter(region_filter, available_regions)
        return region_filter
    else:
        return available_regions


def _validate_region_filter(region_filter, available_regions):
    if not isinstance(region_filter, list):
        raise ValueError(f'Regions input is supposed to be a list type! Your input is {region_filter}.')
    for each_region in region_filter:
        if each_region not in available_regions:
            raise ValueError('Not a valid region!')


def _add_cloud_service_type_tasks(services: list) -> list:
    return [_make_task_wrapper(resource_type='inventory.CloudServiceType', services=services)]


def _add_cloud_service_region_tasks(regions: list) -> list:
    return [_make_task_wrapper(resource_type='inventory.Region', regions=regions)]


def _add_cloud_service_group_tasks(services, regions):
    tasks = []
    '''
    TODO: Certain services are not available in certain regions.
    
    '''
    for service in services:
        for region in regions:
            tasks.append(_make_task_wrapper(resource_type='inventory.CloudService', service=service, region=region))
    return tasks


def _make_task_wrapper(**kwargs) -> dict:
    task_options = {}
    for key, value in kwargs.items():
        task_options[key] = value
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
