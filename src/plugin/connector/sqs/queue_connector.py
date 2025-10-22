from plugin.connector.base import ResourceConnector


class QueueConnector(ResourceConnector):
    service_name = "sqs"
    cloud_service_group = "SQS"
    cloud_service_type = "Queue"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "sqs"
        self.cloud_service_group = "SQS"
        self.cloud_service_type = "Queue"
        self.rest_service_name = "sqs"

    def list_queues(self):
        response = self.client.list_queues()
        return response.get("QueueUrls", [])

    def get_queue_attributes(self, queue_url):
        response = self.client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["All"]
        )
        return response.get("Attributes", {})

    def list_queue_tags(self, queue_url):
        response = self.client.list_queue_tags(QueueUrl=queue_url)
        return response.get("Tags", {})
