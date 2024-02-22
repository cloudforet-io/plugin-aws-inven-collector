import os
import json
import logging
import abc
import datetime

from spaceone.core.utils import dump_yaml, load_yaml_from_file
from spaceone.core.manager import BaseManager
from spaceone.core import config
from ..conf.cloud_service_conf import *
from ..connector.collector_connector import CollectorConnector

_LOGGER = logging.getLogger(__name__)


class CollectorManager(BaseManager):
    """
    이 collect()함수를 cloud_service_type_manager 와 region_manager, 그리고 cloud_service_manager가 implement한다
    필요하면, 공통적으로 들어가는 util functions 들이 여기 들어가면 된다 (예를 들어, generate_error_response())

    """

    cloud_service_types = []
    cloud_service_group = ""
    cloud_service_type = ""
    # _session = None
    connector = None

    def __init__(self, session=None, service=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connector = CollectorConnector.get_connector_by_service(service)()

    @abc.abstractmethod
    def collect(self, options, secret_data, schema, task_options):
        raise NotImplementedError()

    # @property
    # def session(self):
    #     return self._session

    def set_connector(self, service):
        # if cls._connector is None:
        #     print("HOW MANY TIMES AM I GETTING PRINTED?")
        self.connector = CollectorConnector.get_connector_by_service(service)()

    # def create_session(self, secret_data, region):
    #     '''
    #     secret_data를 받아서, connector를 생성하는 함수        '''
    #     if not self.connector:
    #         raise ValueError('Connector is not set!')
    #     self._session = self.connector.get_session(secret_data, region)

    def collect_resources(self, options, secret_data, schema, task_options):
        print("CONNECTOR IS ")
        print(self.connector)
        service = task_options.get("service")
        region = task_options.get("region")
        service_type_managers = self.get_service_type_managers(service)
        # for service_type_manager in service_type_managers:
        #     yield from service_type_manager().collect_resources(options, secret_data, schema, task_options)
        resources = []
        additional_data = ["name", "type", "size", "launched_at"]
        region = task_options.get("region")
        service = task_options.get("service")
        collector_connector = CollectorConnector()
        values = (secret_data, region)
        collector_connector.session(values)
        collector_connector.client(service)
        for mgr in service_type_managers:
            mgr_instance = mgr(collector_connector.client())
            print(mgr_instance.connector)
            try:
                for collected_dict in mgr_instance.collect(
                    options, secret_data, schema, task_options
                ):
                    resources.append(collected_dict)
            # for collected_dict in mgr.collect(options, secret_data, schema, task_options):
            #     data = collected_dict['data']
            #     if getattr(data, 'resource_type', None) and data.resource_type == 'inventory.ErrorResource':
            #         # Error Resource
            #         resources.append(data)
            #     else:
            #         # Cloud Service Resource
            #         if getattr(data, 'set_cloudwatch', None):
            #             data.cloudwatch = data.set_cloudwatch(region)
            #
            #         resource_dict = {
            #             'data': data,
            #             'account': collected_dict.get('account'),
            #             'instance_size': float(collected_dict.get('instance_size', 0)),
            #             'instance_type': collected_dict.get('instance_type', ''),
            #             'launched_at': str(collected_dict.get('launched_at', '')),
            #             'tags': collected_dict.get('tags', {}),
            #             'region_code': region,
            #             'reference': data.reference(region)
            #         }
            #
            #         for add_field in additional_data:
            #             if add_field in collected_dict:
            #                 resource_dict.update({add_field: collected_dict[add_field]})
            #         resource_dict.update({'cloud_service_group': self.cloud_service_group})
            #         resources.append({'resource': resource_dict})
            except Exception as e:
                resource_id = ""
                error_resource_response = self.generate_error(
                    "ec2",
                    region,
                    resource_id,
                    "EC2",
                    mgr_instance.cloud_service_type,
                    e,
                )
                resources.append(error_resource_response)
        return resources

    def generate_error(
        self,
        service_name,
        region_name,
        resource_id,
        cloud_service_group,
        cloud_service_type,
        error_message,
    ):
        _LOGGER.error(
            f"[generate_error] [{service_name}] [{region_name}] {error_message}",
            exc_info=True,
        )

        error_resource_response = {
            "state": "FAILURE",
            "resource_type": "inventory.ErrorResource",
        }
        if type(error_message) is dict:
            error_resource_response.update(
                {
                    "message": json.dumps(error_message),
                    "resource": {
                        "resource_id": resource_id,
                        "resource_type": "inventory.CloudService",
                        "provider": "aws",
                        "cloud_service_group": cloud_service_group,
                        "cloud_service_type": cloud_service_type,
                    },
                }
            )
        else:
            error_resource_response.update(
                {
                    "message": str(error_message),
                    "resource": {
                        "resource_id": resource_id,
                        "resource_type": "inventory.CloudService",
                        "provider": "aws",
                        "cloud_service_group": cloud_service_group,
                        "cloud_service_type": cloud_service_type,
                    },
                }
            )

        return error_resource_response

    @classmethod
    def get_all_managers_in_service(cls):
        return cls.__subclasses__()

    @classmethod
    def get_service_type_managers(cls, service):
        service_type_managers = []
        for sub_cls in cls.__subclasses__():
            print(sub_cls.cloud_service_group)
            if sub_cls.cloud_service_group == service:
                service_type_managers.append(sub_cls)
        return service_type_managers

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
            "LookupAttributes": [
                {
                    "AttributeKey": "ResourceName",
                    "AttributeValue": resource_name,
                }
            ],
            "region_name": region_name,
            "resource_type": resource_type,
        }

        return cloudtrail

    def set_cloudwatch(self, namespace, dimension_name, resource_id, region_name):
        """
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
        """

        cloudwatch_data = {
            "region_name": region_name,
            "metrics_info": self.set_metrics_info(
                namespace, dimension_name, resource_id
            ),
        }

        return cloudwatch_data

    def set_metrics_info(self, namespace, dimension_name, resource_id):
        metric_info = {"Namespace": namespace}

        if dimension_name:
            metric_info.update(
                {"Dimensions": self.set_dimensions(dimension_name, resource_id)}
            )

        return [metric_info]

    @staticmethod
    def set_dimensions(dimension_name, resource_id):
        dimension = {"Name": dimension_name, "Value": resource_id}

        return [dimension]

    # @staticmethod
    # def set_data_and_yaml(field, folder_name):
    #     project_path = __import__(config.get_package()).__path__[0]
    #     file_path = os.path.join(
    #         project_path, "metadata", "dynamic_ui", f"{folder_name}"
    #     )
    #
    #     for file in os.listdir(file_path):
    #         if file.endswith(".yaml") or file.endswith(".yml"):
    #             field_type, _ = file.rsplit("_", 1)
    #
    #             field[f"{field_type}_example"] = {
    #                 "data": {
    #                     "data": {f"{field_type}": field.get(field_type, {})},
    #                 },
    #                 "yaml": dump_yaml(
    #                     load_yaml_from_file(os.path.join(file_path, file))
    #                 ),
    #             }
    #     return field

    @staticmethod
    def convert_tags_to_dict_type(tags, key="Key", value="Value"):
        dict_tags = {}

        for _tag in tags:
            dict_tags[_tag.get(key)] = _tag.get(value)

        return dict_tags
