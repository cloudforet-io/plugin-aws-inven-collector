import json
import logging
import datetime
from functools import partial
from typing import List
from boto3.session import Session
from spaceone.core import utils
from spaceone.core.connector import BaseConnector
from ..conf.cloud_service_conf import *

_LOGGER = logging.getLogger(__name__)

DEFAULT_REGION = 'us-east-1'
ARN_DEFAULT_PARTITION = 'aws'
REGIONS = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ap-south-1', 'ap-northeast-2',
           'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ca-central-1', 'eu-central-1', 'eu-west-1',
           'eu-west-2', 'eu-west-3', 'eu-north-1', 'sa-east-1']



class CollectorConnector(BaseConnector):
    cloud_service_group = None
    service_name = ''
    _session = None
    _client = None
    _init_client = None
    account_id = None
    region_name = DEFAULT_REGION
    region_names = []

    def init_property(self, name: str, init_data: callable):
        if self.__getattribute__(name) is None:
            self.__setattr__(name, init_data())
        return self.__getattribute__(name)

    def __init__(self, config={}, options={}, secret_data={}, region_id=None, zone_id=None, pool_id=None,
                 filter={}, **kwargs):

        super().__init__(config=config, **kwargs)
        self.options = options
        self.secret_data = secret_data
        self.region_id = region_id
        self.zone_id = zone_id
        self.pool_id = pool_id
        self.filter = filter
        self.account_id = kwargs.get('account_id')
        self.region_names = kwargs.get('regions', [])

    def reset_region(self, region_name):
        self.region_name = region_name
        self._client = None
        self._session = None

    def get_regions(self):
        _session = self.get_session(self.secret_data, DEFAULT_REGION)
        ec2_client = _session.client('ec2', verify=BOTO3_HTTPS_VERIFIED)
        return list(map(lambda region_info: region_info.get('RegionName'),
                        ec2_client.describe_regions().get('Regions')))

    def get_session(self, secret_data, region_name):
        params = {
            'aws_access_key_id': secret_data['aws_access_key_id'],
            'aws_secret_access_key': secret_data['aws_secret_access_key'],
            'region_name': region_name
        }

        session = Session(**params)

        # ASSUME ROLE
        if role_arn := secret_data.get('role_arn'):
            sts = session.client('sts', verify=BOTO3_HTTPS_VERIFIED)

            _assume_role_request = {
                'RoleArn': role_arn,
                'RoleSessionName': utils.generate_id('AssumeRoleSession'),
            }

            if external_id := secret_data.get('external_id'):
                _assume_role_request.update({'ExternalId': external_id})

            assume_role_object = sts.assume_role(**_assume_role_request)
            credentials = assume_role_object['Credentials']

            assume_role_params = {
                'aws_access_key_id': credentials['AccessKeyId'],
                'aws_secret_access_key': credentials['SecretAccessKey'],
                'region_name': region_name,
                'aws_session_token': credentials['SessionToken']
            }
            session = Session(**assume_role_params)
        return session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, values):
        secret_data, region_name = values
        self.init_property('session', partial(self.get_session, secret_data, region_name))

    @property
    def init_client(self):
        if self._init_client is None:
            self._init_client = self.session.client('ec2', verify=BOTO3_HTTPS_VERIFIED)
        return self._init_client

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, service_name):
        if self._client is None:
            self._client = self.session.client(service_name, verify=BOTO3_HTTPS_VERIFIED)

    @staticmethod
    def generate_arn(partition=ARN_DEFAULT_PARTITION, service="", region="", account_id="", resource_type="",
                     resource_id=""):
        return f'arn:{partition}:{service}:{region}:{account_id}:{resource_type}/{resource_id}'

    @staticmethod
    def divide_to_chunks(resources, n):
        """
         For some API parameters, there is a limit to the number that can be described at one time.
         This method divides the list value of a resource by a certain number and divides it.
         The "resources" argument is a list value of resources, and divides it into a list of "n" arguments.
        """
        for i in range(0, len(resources), n):
            yield resources[i:i + n]

    def get_region_from_result(self, region_code):
        region_resource = self.match_region_info(region_code)

        if region_resource:
            return {'resource': region_resource}

        return None

    # @staticmethod
    # def _match_execute_manager(cloud_service_groups):
    #     return [CLOUD_SERVICE_GROUP_MAP[_cloud_service_group] for _cloud_service_group in cloud_service_groups
    #             if _cloud_service_group in CLOUD_SERVICE_GROUP_MAP]

    # def get_account_id(self, secret_data, region=DEFAULT_REGION):
    #     _session = self.get_session(secret_data, region)
    #     sts_client = _session.client('sts', verify=BOTO3_HTTPS_VERIFIED)
    #     return sts_client.get_caller_identity()['Account']

    @classmethod
    def get_connector_by_service(cls, service):
        for sub_cls in cls.__subclasses__():
            if sub_cls.cloud_service_group == service:
                return sub_cls

    # def get_regions(secret_data):
    #     _session = get_session(secret_data, DEFAULT_REGION)
    #     ec2_client = _session.client('ec2', verify=BOTO3_HTTPS_VERIFIED)
    #
    #     return list(map(lambda region_info: region_info.get('RegionName'),
    #                     ec2_client.describe_regions().get('Regions')))

    @staticmethod
    def match_region_info(region_name):
        match_region_info = REGION_INFO.get(region_name, None)
        if match_region_info is not None:
            region_info = match_region_info.copy()
            region_info.update({
                'region_code': region_name
            })
            return region_info
        return None