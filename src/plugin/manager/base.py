import abc
import logging
import datetime

from plugin.conf.cloud_service_conf import REGION_INFO
from plugin.connector.base import ResourceConnector
from spaceone.core.manager import BaseManager
from spaceone.inventory.plugin.collector.lib import *


_LOGGER = logging.getLogger(__name__)

__all__ = ["ResourceManager"]


class ResourceManager(BaseManager):
    cloud_service_group = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.provider = "aws"
        self.cloud_service_group = ""
        self.cloud_service_type = ""
        self.connector = None

    @classmethod
    def list_managers(cls):
        return cls.__subclasses__()

    @classmethod
    def get_manager_by_service(cls, service):
        for manager in cls.list_managers():
            print(manager)
            print(manager.cloud_service_group)
            if manager.cloud_service_group == service:
                yield manager

    @classmethod
    def get_service_names(cls):
        services_name = set()
        for sub_cls in cls.__subclasses__():
            services_name.add(sub_cls.cloud_service_group)
        return list(services_name)

    @classmethod
    def collect_region(cls, region):
        match_region_info = REGION_INFO.get(region, None)
        if match_region_info is not None:
            region_info = match_region_info.copy()
            region_info.update(
                {
                    "name": match_region_info.get("name", ""),
                    "region_code": region,
                    "provider": "aws",
                }
            )

            return make_response(
                region=region_info,
                match_keys=[["provider", "region_code"]],
                resource_type="inventory.Region",
            )

        return None

    def collect_resources(
        self, service, service_type, region, options, secret_data, schema
    ):
        _LOGGER.debug(
            f"[collect_resources] collect Field resources (options: {options})"
        )
        target_connector = ResourceConnector.get_connector(service, service_type)
        self.connector = target_connector(secret_data=secret_data, region_name=region)
        self.connector.set_account_id()
        try:
            # yield from self.collect_cloud_service_type()
            yield from self.collect_cloud_service(region, options, secret_data, schema)
        except Exception as e:
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
            )

    def collect_cloud_service_type(self):
        cloud_service_type = self.create_cloud_service_type()
        yield make_response(
            cloud_service_type=cloud_service_type,
            match_keys=[["name", "group", "provider"]],
            resource_type="inventory.CloudServiceType",
        )

    def collect_cloud_service(self, region, options, secret_data, schema):
        cloud_services = self.create_cloud_service(region, options, secret_data, schema)
        for cloud_service in cloud_services:
            data = cloud_service.get("data")
            if (
                getattr(data, "resource_type", None)
                and data.resource_type == "inventory.CloudService"
            ):
                # Cloud Service Resource
                if getattr(data, "set_cloudwatch", None):
                    cloud_service.get("data").cloudwatch = data.set_cloudwatch(region)

                data.update(
                    {
                        "launched_at": str(data.get("launched_at", "")),
                    }
                )
            yield make_response(
                cloud_service=cloud_service,
                match_keys=[
                    [
                        "reference.resource_id",
                        "provider",
                        "cloud_service_type",
                        "cloud_service_group",
                        "account",
                    ]
                ],
                resource_type="inventory.CloudService",
            )

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
    def get_reference(resource_id, link):
        return {
            "resource_id": resource_id,
            "external_link": link,
        }

    @staticmethod
    def set_dimensions(dimension_name, resource_id):
        dimension = {"Name": dimension_name, "Value": resource_id}

        return [dimension]

    @staticmethod
    def convert_tags_to_dict_type(tags, key="Key", value="Value"):
        dict_tags = {}

        for _tag in tags:
            dict_tags[_tag.get(key)] = _tag.get(value)

        return dict_tags

    @staticmethod
    def generate_arn(
        partition="aws",
        service="",
        region="",
        account_id="",
        resource_type="",
        resource_id="",
    ):
        return f"arn:{partition}:{service}:{region}:{account_id}:{resource_type}/{resource_id}"

    @staticmethod
    def datetime_to_iso8601(value: datetime.datetime):
        if isinstance(value, datetime.datetime):
            value = value.replace(tzinfo=None)
            return f"{value.isoformat()}"
        return None

    @abc.abstractmethod
    def create_cloud_service_type(self):
        raise NotImplementedError(
            "method `create_cloud_service_type` should be implemented"
        )

    @abc.abstractmethod
    def create_cloud_service(self, region, options, secret_data, schema):
        raise NotImplementedError("method `create_cloud_service` should be implemented")

    @classmethod
    def get_region_names(cls):
        return list(REGION_INFO.keys())
