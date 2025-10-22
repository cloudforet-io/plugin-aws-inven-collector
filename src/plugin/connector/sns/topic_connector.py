from plugin.connector.base import ResourceConnector


class TopicConnector(ResourceConnector):
    service_name = "sns"
    cloud_service_group = "SNS"
    cloud_service_type = "Topic"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "sns"
        self.cloud_service_group = "SNS"
        self.cloud_service_type = "Topic"
        self.rest_service_name = "sns"

    def list_topics(self):
        paginator = self.client.get_paginator("list_topics")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def get_topic_attributes(self, topic_arn):
        response = self.client.get_topic_attributes(TopicArn=topic_arn)
        return response.get("Attributes", {})

    def list_subscriptions_by_topic(self, topic_arn):
        response = self.client.list_subscriptions_by_topic(TopicArn=topic_arn)
        return response.get("Subscriptions", [])

    def list_tags_for_resource(self, resource_arn):
        response = self.client.list_tags_for_resource(ResourceArn=resource_arn)
        return response.get("Tags", [])
