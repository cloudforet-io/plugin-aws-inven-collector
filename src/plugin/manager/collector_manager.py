import json
import logging
import abc
import datetime

from spaceone.core.manager import BaseManager
from ..conf.cloud_service_conf import *

_LOGGER = logging.getLogger(__name__)


class CollectorManager(BaseManager):
    '''
    이 collect()함수를 cloud_service_type_manager 와 region_manager, 그리고 cloud_service_manager가 implement한다
    필요하면, 공통적으로 들어가는 util functions 들이 여기 들어가면 된다 (예를 들어, generate_error_response())

    '''

    cloud_service_types = []

    cloud_service_group = ''
    cloud_service_type = ''

    def __init__(self, session=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = session
        self.connector = None

    @abc.abstractmethod
    def collect(self, options, secret_data, schema, task_options):
        raise NotImplementedError()

    @property
    def session(self):
        return self._session

    def create_session(self, secret_data, region):
        '''
        secret_data를 받아서, connector를 생성하는 함수        '''
        if not self.connector:
            raise ValueError('Connector is not set!')
        self._session = self.connector.get_session(secret_data, region)

    def generate_error(self, service_name, region_name, resource_id, cloud_service_group, cloud_service_type,
                       error_message):
        _LOGGER.error(f'[generate_error] [{service_name}] [{region_name}] {error_message}', exc_info=True)

        if type(error_message) is dict:
            error_resource_response = {'message': json.dumps(error_message),
                                       'resource': {'resource_id': resource_id,
                                                    'cloud_service_group': cloud_service_group,
                                                    'cloud_service_type': cloud_service_type}}
        else:
            error_resource_response = {'message': str(error_message),
                                       'resource': {'resource_id': resource_id,
                                                    'cloud_service_group': cloud_service_group,
                                                    'cloud_service_type': cloud_service_type}}

        return error_resource_response

    @classmethod
    def get_target_manager(cls, service):
        for sub_cls in cls.__subclasses__():
            if sub_cls.service_type == service:
                return sub_cls


    # def set_cloud_service_types(self):
    #     if 'service_code_mappers' in self.options:
    #         svc_code_maps = self.options['service_code_mappers']
    #         for cst in self.cloud_service_types:
    #             if getattr(cst.resource, 'service_code') and cst.resource.service_code in svc_code_maps:
    #                 cst.resource.service_code = svc_code_maps[cst.resource.service_code]
    #
    #     if 'custom_asset_url' in self.options:
    #         for cst in self.cloud_service_types:
    #             _tags = cst.resource.tags
    #
    #             if 'spaceone:icon' in _tags:
    #                 _icon = _tags['spaceone:icon']
    #                 _tags['spaceone:icon'] = f'{self.options["custom_asset_url"]}/{_icon.split("/")[-1]}'
    #     return self.cloud_service_types

    @staticmethod
    def datetime_to_iso8601(value: datetime.datetime):
        if isinstance(value, datetime.datetime):
            value = value.replace(tzinfo=None)
            return f"{value.isoformat(timespec='seconds')}TZD"

        return None

    @staticmethod
    def set_cloudtrail(region_name, resource_type, resource_name):
        cloudtrail = {
            'LookupAttributes': [
                {
                    "AttributeKey": "ResourceName",
                    "AttributeValue": resource_name,
                }
            ],
            'region_name': region_name,
            'resource_type': resource_type
        }

        return cloudtrail

    def set_cloudwatch(self, namespace, dimension_name, resource_id, region_name):
        '''
        data.cloudwatch: {
            "metrics_info": [
                {
                    "Namespace": "AWS/XXXX",
                    "Dimensions": [
                        {
                            "Name": "XXXXX",
                            "Value": "i-xxxxxx"
                        }
                    ]
                }
            ]
            "region_name": region_name
        }
        '''

        cloudwatch_data = {
            'region_name': region_name,
            'metrics_info': self.set_metrics_info(namespace, dimension_name, resource_id)
        }

        return cloudwatch_data

    def set_metrics_info(self, namespace, dimension_name, resource_id):
        metric_info = {'Namespace': namespace}

        if dimension_name:
            metric_info.update({'Dimensions': self.set_dimensions(dimension_name, resource_id)})

        return [metric_info]

    @staticmethod
    def set_dimensions(dimension_name, resource_id):
        dimension = {
            'Name': dimension_name,
            'Value': resource_id
        }

        return [dimension]

    @staticmethod
    def convert_tags_to_dict_type(tags, key='Key', value='Value'):
        dict_tags = {}

        for _tag in tags:
            dict_tags[_tag.get(key)] = _tag.get(value)

        return dict_tags
