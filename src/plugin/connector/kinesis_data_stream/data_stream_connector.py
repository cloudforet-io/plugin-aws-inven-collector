from plugin.connector.base import ResourceConnector


class DataStreamConnector(ResourceConnector):
    service_name = "kinesis"
    cloud_service_group = "KinesisDataStream"
    cloud_service_type = "DataStream"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "kinesis"
        self.cloud_service_group = "KinesisDataStream"
        self.cloud_service_type = "DataStream"
        self.rest_service_name = "kinesis"

    def list_streams(self):
        paginator = self.client.get_paginator("list_streams")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_stream(self, stream_name):
        response = self.client.describe_stream(StreamName=stream_name)
        return response.get("StreamDescription", {})

    def list_tags_for_stream(self, stream_name):
        response = self.client.list_tags_for_stream(StreamName=stream_name)
        return response.get("Tags", [])

    def list_stream_consumers(self, stream_arn):
        paginator = self.client.get_paginator("list_stream_consumers")
        response_iterator = paginator.paginate(
            StreamARN=stream_arn,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator
