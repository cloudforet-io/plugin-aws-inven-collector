import json
import logging
import datetime
from functools import partial
from typing import List
from boto3.session import Session
from spaceone.core import utils
from spaceone.core.connector import BaseConnector
from spaceone.core.error import *
from plugin.conf.cloud_service_conf import *

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCHEMA = "google_oauth_client_id"
DEFAULT_REGION = "us-east-1"
ARN_DEFAULT_PARTITION = "aws"
REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "ap-south-1",
    "ap-northeast-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-northeast-1",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-north-1",
    "sa-east-1",
]


def get_session(secret_data, region_name):
    params = {
        "aws_access_key_id": secret_data["aws_access_key_id"],
        "aws_secret_access_key": secret_data["aws_secret_access_key"],
        "region_name": region_name,
    }

    session = Session(**params)

    # ASSUME ROLE
    if role_arn := secret_data.get("role_arn"):
        sts = session.client("sts", verify=BOTO3_HTTPS_VERIFIED)

        _assume_role_request = {
            "RoleArn": role_arn,
            "RoleSessionName": utils.generate_id("AssumeRoleSession"),
        }

        if external_id := secret_data.get("external_id"):
            _assume_role_request.update({"ExternalId": external_id})

        assume_role_object = sts.assume_role(**_assume_role_request)
        credentials = assume_role_object["Credentials"]

        assume_role_params = {
            "aws_access_key_id": credentials["AccessKeyId"],
            "aws_secret_access_key": credentials["SecretAccessKey"],
            "region_name": region_name,
            "aws_session_token": credentials["SessionToken"],
        }
        session = Session(**assume_role_params)
    return session


class ResourceConnector(BaseConnector):
    service_name = ""
    rest_service_name = ""
    _session = None
    _client = None
    _init_client = None
    account_id = None
    region_name = DEFAULT_REGION
    region_names = []
    cloud_service_types = []
    cloud_service_group = ""
    cloud_service_type = ""

    def init_property(self, name: str, init_data: callable):
        if self.__getattribute__(name) is None:
            self.__setattr__(name, init_data())
        return self.__getattribute__(name)

    def __init__(
        self,
        secret_data={},
        region_name={},
        config={},
        options={},
        region_id=None,
        zone_id=None,
        pool_id=None,
        filter={},
        **kwargs,
    ):
        super().__init__(config=config, **kwargs)
        self.options = options
        self.secret_data = secret_data
        self.region_name = region_name
        self.region_id = region_id
        self.zone_id = zone_id
        self.pool_id = pool_id
        self.filter = filter
        self.region_names = kwargs.get("regions", [])

    def reset_region(self, region_name):
        self.region_name = region_name
        self._client = None
        self._session = None

    def set_client(self, service_name):
        self.service_name = service_name
        self._client = self.session.client(
            self.service_name, verify=BOTO3_HTTPS_VERIFIED
        )
        return self._client

    def get_account_id(self):
        return self.account_id

    def load_account_id(self, account_id):
        self.account_id = account_id

    def set_account_id(self):
        sts_client = self.session.client("sts", verify=BOTO3_HTTPS_VERIFIED)
        self.account_id = sts_client.get_caller_identity()["Account"]

    def set_cloud_service_types(self):
        if "service_code_mappers" in self.options:
            svc_code_maps = self.options["service_code_mappers"]

            for cst in self.cloud_service_types:
                if (
                    getattr(cst.resource, "service_code")
                    and cst.resource.service_code in svc_code_maps
                ):
                    cst.resource.service_code = svc_code_maps[cst.resource.service_code]

        if "custom_asset_url" in self.options:
            for cst in self.cloud_service_types:
                _tags = cst.resource.tags

                if "spaceone:icon" in _tags:
                    _icon = _tags["spaceone:icon"]
                    _tags["spaceone:icon"] = (
                        f'{self.options["custom_asset_url"]}/{_icon.split("/")[-1]}'
                    )

        return self.cloud_service_types

    @property
    def session(self):
        return self.init_property(
            "_session", partial(get_session, self.secret_data, self.region_name)
        )

    @property
    def client(self):
        if self._client is None:
            self._client = self.session.client(
                self.rest_service_name, verify=BOTO3_HTTPS_VERIFIED
            )
        return self._client

    @classmethod
    def get_connector(cls, service, service_type):
        for connector in cls.list_services():
            if (
                connector.cloud_service_group == service
                and connector.cloud_service_type == service_type
            ):
                return connector
        raise ERROR_INVALID_PARAMETER(key="service", reason="Not supported service")

    @classmethod
    def list_services(cls):
        return cls.__subclasses__()

    @classmethod
    def get_regions(cls, secret_data):
        _session = get_session(secret_data, DEFAULT_REGION)
        ec2_client = _session.client("ec2", verify=BOTO3_HTTPS_VERIFIED)

        return list(
            map(
                lambda region_info: region_info.get("RegionName"),
                ec2_client.describe_regions().get("Regions"),
            )
        )
