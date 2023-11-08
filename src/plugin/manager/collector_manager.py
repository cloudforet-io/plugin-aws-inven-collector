import logging

from spaceone.core.manager import BaseManager
from ..conf.cloud_service_conf import *
from ..connector.ec2 import CollectorManager

class CollectorManager(BaseManager):

    def init_response(options: dict) -> dict:
        capability = {
            'filter_format': FILTER_FORMAT,
            'supported_resource_type': SUPPORTED_RESOURCE_TYPE,
            'supported_features': SUPPORTED_FEATURES,
            'supported_schedules': SUPPORTED_SCHEDULES
        }
        return {'metadata': capability}

    def verify(self, secret_data, region_name):
        ec2_connector = self.locator.get_connector('EC2Connector')
        r = ec2_connector.verify(secret_data, region_name)
        # ACTIVE/UNKNOWN
        return r
