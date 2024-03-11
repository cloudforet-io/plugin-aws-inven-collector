from plugin.conf.cloud_service_conf import BOTO3_HTTPS_VERIFIED
from plugin.connector.base import ResourceConnector


class TableConnector(ResourceConnector):
    service_name = "dynamodb"
    cloud_service_group = "DynamoDB"
    cloud_service_type = "Table"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "dynamodb"
        self.cloud_service_type = "Table"
        self.cloud_service_group = "DynamoDB"
        self.rest_service_name = "dynamodb"

    def get_tables(self):
        paginator = self.client.get_paginator("list_tables")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_table(self, table_name):
        return self.client.describe_table(TableName=table_name)

    def describe_contributor_insights(self, table_name):
        return self.client.describe_contributor_insights(TableName=table_name)

    def describe_continuous_backups(self, table_name):
        return self.client.describe_continuous_backups(TableName=table_name)

    def describe_time_to_live(self, table_name):
        return self.client.describe_time_to_live(TableName=table_name)

    def describe_scaling_policies(self, namespace):
        auto_scaling_client = self.session.client(
            "application-autoscaling", verify=BOTO3_HTTPS_VERIFIED
        )
        return auto_scaling_client.describe_scaling_policies(ServiceNamespace=namespace)

    def list_tags_of_resource(self, resource_arn):
        return self.client.list_tags_of_resource(ResourceArn=resource_arn)
