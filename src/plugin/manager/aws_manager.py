import os
import json
import logging
import abc
import datetime

from spaceone.core.utils import dump_yaml, load_yaml_from_file
from spaceone.core.manager import BaseManager
from spaceone.core import config

from .cloud_service_manager import CloudServiceManager
from .collector_manager import CollectorManager
from .region_manager import RegionManager
from ..conf.cloud_service_conf import *
from ..connector.collector_connector import CollectorConnector

_LOGGER = logging.getLogger(__name__)


class AWSManager(BaseManager):

    def __init__(self, options, secret_data, schema, task_options, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = options
        self.secret_data = secret_data
        self.schema = schema
        self.task_options = task_options

    def collect_cloud_service_types(self):
        cloud_service_type_manager = CloudServiceManager()
        return cloud_service_type_manager.collect(self.options, self.secret_data, self.schema, self.task_options)

    def collect_regions(self):
        region_manager = RegionManager()
        return region_manager.collect(self.options, self.secret_data, self.schema, self.task_options)

    def collect_cloud_services(self):
        service = self.task_options.get('service')
        service_type_managers = CollectorManager.get_service_type_managers(service)
        resources = []
        for mgr in service_type_managers:
            mgr_instance = mgr()
            print(mgr_instance.connector)
            try:
                for collected_dict in mgr_instance.collect(self.options, self.secret_data, self.schema, self.task_options):
                    resources.append(collected_dict)
            except Exception as e:
                print(e)

        return resources
