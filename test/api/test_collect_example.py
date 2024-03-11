import os
import logging

from spaceone.core import utils, config
from spaceone.tester import TestCase, print_json
from google.protobuf.json_format import MessageToDict
import pprint

_LOGGER = logging.getLogger(__name__)

class TestCollect(TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))
    endpoints = config.get('ENDPOINTS', {})

    def test_init(self):
        v_info = self.inventory.Collector.init({'options': {}})
        print_json(v_info)

    def test_collect(self):
        pass