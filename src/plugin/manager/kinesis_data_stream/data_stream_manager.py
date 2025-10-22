from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.kinesis_data_stream import DataStream


class DataStreamManager(ResourceManager):
    cloud_service_group = "Kinesis"
    cloud_service_type = "DataStream"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Kinesis"
        self.cloud_service_type = "DataStream"
        self.metadata_path = "metadata/kinesis_data_stream/data_stream.yaml"

    def create_cloud_service_type(self):
        result = []
        datastream_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonKinesis",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-kinesis.svg"
            },
            labels=["Analytics", "Streaming"],
        )
        result.append(datastream_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_data_streams(options, region)

    def _collect_data_streams(self, options, region):
        region_name = region

        try:
            data_streams, account_id = self.connector.list_kinesis_data_streams()

            for stream in data_streams:
                try:
                    stream_name = stream.get("StreamName")

                    # Get stream consumers
                    consumers = self._get_stream_consumers(stream_name)

                    # Get stream tags
                    tags = self._get_stream_tags(stream_name)

                    stream_data = {
                        "stream_name": stream_name,
                        "stream_arn": stream.get("StreamARN"),
                        "stream_status": stream.get("StreamStatus", ""),
                        "stream_mode_details": stream.get("StreamModeDetails", {}),
                        "retention_period_hours": stream.get("RetentionPeriodHours", 0),
                        "stream_creation_timestamp": stream.get(
                            "StreamCreationTimestamp"
                        ),
                        "enhanced_monitoring": stream.get("EnhancedMonitoring", []),
                        "encryption_type": stream.get("EncryptionType", ""),
                        "key_id": stream.get("KeyId", ""),
                        "open_shard_count": stream.get("OpenShardCount", 0),
                        "consumer_count": stream.get("ConsumerCount", 0),
                        "consumers": consumers,
                    }

                    stream_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                stream_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                stream_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/kinesis/home?region={region}#/streams/details/{stream_name}"
                    resource_id = stream_name
                    reference = self.get_reference(resource_id, link)

                    stream_vo = DataStream(stream_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=stream_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=stream_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=stream_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_kinesis_data_streams] [{stream.get("StreamName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_kinesis_data_streams] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_stream_consumers(self, stream_name):
        """Get stream consumers"""
        try:
            return self.connector.get_stream_consumers(stream_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get consumers for stream {stream_name}: {e}")
            return []

    def _get_stream_tags(self, stream_name):
        """Get stream tags"""
        try:
            return self.connector.get_stream_tags(stream_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for stream {stream_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
