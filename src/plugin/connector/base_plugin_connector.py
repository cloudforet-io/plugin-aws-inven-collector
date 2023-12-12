import json
import logging
from spaceone.core.connector import BaseConnector
from ..conf.cloud_service_conf import *

_LOGGER = logging.getLogger(__name__)

def get_session(secret_data, region_name):
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


class BasePluginManager(BaseConnector):
    connector_name = None

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
    def verify(self, options, secret_data, **kwargs):
        """ Check collector's status.
        """
        #connector = EC2Connector()
        #r = connector.verify(secret_data)
        return

    def get_regions(self):
        _session = get_session(self.secret_data, DEFAULT_REGION)
        ec2_client = _session.client('ec2', verify=BOTO3_HTTPS_VERIFIED)
        return list(map(lambda region_info: region_info.get('RegionName'),
                        ec2_client.describe_regions().get('Regions')))
