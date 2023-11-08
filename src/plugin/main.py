from spaceone.inventory.plugin.collector.lib.server import CollectorPluginServer
from .manager.collector_manager import CollectorManager
from .conf.cloud_service_conf import *

app = CollectorPluginServer()

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
    options = params['options']

    collector_mgr = CollectorManager()
    return collector_mgr.init_response(options)


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
    region_name = params.get('region_name', DEFAULT_REGION)
    active = collector_mgr.verify(secret_data, region_name)

    return {}


@app.route('Collector.collect')
def collector_colllect(params: dict) -> dict:
    """ Collect external data

    Args:
        params (CollectorCollectRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'schema': 'str',
            'domain_id': 'str'
        }

    Returns:
        Generator[ResourceResponse, None, None]
        {
            'state': 'SUCCESS | FAILURE',
            'resource_type': 'inventory.CloudService | inventory.CloudServiceType | inventory.Region',
            'resource_data': 'dict',
            'match_keys': 'list',
            'error_message': 'str'
            'metadata': 'dict'
        }
    """
    pass


@app.route('Job.get_tasks')
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
    pass
