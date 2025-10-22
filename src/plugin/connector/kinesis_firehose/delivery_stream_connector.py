from plugin.connector.base import ResourceConnector


class DeliveryStreamConnector(ResourceConnector):
    service_name = "firehose"
    cloud_service_group = "KinesisFirehose"
    cloud_service_type = "DeliveryStream"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "firehose"
        self.cloud_service_group = "KinesisFirehose"
        self.cloud_service_type = "DeliveryStream"
        self.rest_service_name = "firehose"

    def list_delivery_streams(self):
        response = self.client.list_delivery_streams()
        return response.get("DeliveryStreamNames", [])

    def describe_delivery_stream(self, stream_name):
        response = self.client.describe_delivery_stream(DeliveryStreamName=stream_name)
        return response.get("DeliveryStreamDescription", {})

    def get_delivery_stream_tags(self, stream_name):
        response = self.client.list_tags_for_delivery_stream(
            DeliveryStreamName=stream_name
        )
        return response.get("Tags", [])
