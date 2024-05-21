import os
import logging

from spaceone.core import utils, config
from spaceone.tester import TestCase, print_json
from google.protobuf.json_format import MessageToDict
import pprint

_LOGGER = logging.getLogger(__name__)

AKI = os.environ.get("AWS_ACCESS_KEY_ID", None)
SAK = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
ROLE_ARN = os.environ.get("ROLE_ARN", None)
EXTERNAL_ID = os.environ.get("EXTERNAL_ID", None)
REGION_NAME = os.environ.get("REGION_NAME", None)

if AKI == None or SAK == None:
    print(
        """
##################################################
# ERROR 
#
# Configure your AWS credential first for test
##################################################
example)

export AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>

"""
    )
    exit


class TestCollect(TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get("SPACEONE_TEST_CONFIG_FILE", "./config.yml")
    )
    endpoints = config.get("ENDPOINTS", {})
    secret_data = {
        "aws_access_key_id": AKI,
        "aws_secret_access_key": SAK,
    }

    if ROLE_ARN is not None:
        secret_data.update({"role_arn": ROLE_ARN})

    if EXTERNAL_ID is not None:
        secret_data.update({"external_id": EXTERNAL_ID})

    if REGION_NAME is not None:
        secret_data.update({"region_name": REGION_NAME})

    def test_init(self):
        v_info = self.inventory.Collector.init({"options": {}})
        print_json(v_info)

    def test_verify(self):
        options = {"domain": "mz.co.kr"}
        v_info = self.inventory.Collector.verify(
            {"options": options, "secret_data": self.secret_data}
        )
        print_json(v_info)

    """
    ========================================================================================================================
    This test function below is simulating overall collecting process, from generating tasks to collecting resources. 
    ========================================================================================================================
    """

    def test_full_collect(self):
        print(f"Action 1: Generate Tasks!")
        print(f"=================== start get_tasks! ==========================")
        options = {
            "service_filter": None,
            "region_filter": None,
        }
        v_info = self.inventory.Job.get_tasks(
            {"options": options, "secret_data": self.secret_data}
        )
        print(f"=================== end get_tasks! ==========================")
        all_tasks = MessageToDict(v_info, preserving_proto_field_name=True)

        print(f"Action 2: Collect Resources!")
        print(
            f"=================== start collect_resources! =========================="
        )
        for task in all_tasks.get("tasks", []):
            task_options = task["task_options"]
            filter = {}
            params = {
                "options": {},
                "secret_data": self.secret_data,
                "filter": filter,
                "task_options": task_options,
            }
            res_stream = self.inventory.Collector.collect(params)
            for res in res_stream:
                print_json(res)
        print(f"=================== end collect_resources! ==========================")

    """
    ========================================================================================================================
    Test functions below are for individual test purposes. 
    ========================================================================================================================
    """

    def test_cloud_service_task(self):
        services = ["EC2"]
        regions = ["ap-northeast-2"]
        for service in services:
            for region in regions:
                self.test_collect_cloud_service(service, region)

    def test_cloud_service_type_task(self):
        services = ["EC2"]
        self.test_collect_cloud_service_type(services)

    def test_collect_cloud_service(self, service=None, region=None):
        options = {}
        # task_options = {
        #     'resource_type': 'inventory.CloudService',
        #     'region': 'ap-northeast-1',
        #     'service': 'EC2'
        # }
        region = "ap-northeast-2"
        service = "EC2"
        options = {
            "resource_type": "inventory.CloudService",
            "region": region,
            "service": service,
        }

        # options = {
        #     "resource_type": "inventory.CloudService",
        #     "region": "ap-northeast-2",
        #     "service": "CertificateManager",
        # }
        filter = {}
        params = {
            "options": {},
            "task_options": options,
            "secret_data": self.secret_data,
            "filter": filter,
        }

        res_stream = self.inventory.Collector.collect(params)
        for res in res_stream:
            print_json(res)

    def test_collect_cloud_service_type(self, services):
        options = {
            "resource_type": "inventory.CloudServiceType",
            "services": services,
        }
        filter = {}

        params = {
            "options": {},
            "task_options": options,
            "secret_data": self.secret_data,
            "filter": filter,
        }

        res_stream = self.inventory.Collector.collect(params)
        for res in res_stream:
            print_json(res)

    def test_collect_region(self):
        options = {
            "resource_type": "inventory.Region",
            "regions": [
                "ap-south-1",
                "eu-north-1",
                "eu-west-3",
                "eu-west-2",
                "eu-west-1",
                "ap-northeast-3",
                "ap-northeast-2",
                "ap-northeast-1",
                "ca-central-1",
                "sa-east-1",
                "ap-east-1",
                "ap-southeast-1",
                "ap-southeast-2",
                "eu-central-1",
                "ap-southeast-3",
                "us-east-1",
                "us-east-2",
                "us-west-1",
                "us-west-2",
            ],
        }
        filter = {}

        params = {
            "options": {},
            "task_options": options,
            "secret_data": self.secret_data,
            "filter": filter,
        }

        res_stream = self.inventory.Collector.collect(params)
        for res in res_stream:
            print_json(res)

    def test_get_tasks(self):
        print(f"=================== start get_tasks! ==========================")
        options = {}
        v_info = self.inventory.Job.get_tasks(
            {"options": options, "secret_data": self.secret_data}
        )
        print_json(v_info)

        return MessageToDict(v_info, preserving_proto_field_name=True)
