from plugin.connector.base import ResourceConnector


class NetworkACLConnector(ResourceConnector):
    service_name = "ec2"
    cloud_service_group = "VPC"
    cloud_service_type = "NetworkACL"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "ec2"
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "NetworkACL"
        self.rest_service_name = "ec2"

    def describe_network_acls(self, filters=None):
        if filters is None:
            filters = []
        response = self.client.describe_network_acls(Filters=filters)
        return response.get("NetworkAcls", [])

    def describe_network_acl_attribute(self, network_acl_id, attribute):
        response = self.client.describe_network_acl_attribute(
            NetworkAclId=network_acl_id, Attribute=attribute
        )
        return response
