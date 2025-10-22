from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.kinesis_firehose import DeliveryStream


class DeliveryStreamManager(ResourceManager):
    cloud_service_group = "Kinesis"
    cloud_service_type = "DeliveryStream"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Kinesis"
        self.cloud_service_type = "DeliveryStream"
        self.metadata_path = "metadata/kinesis_firehose/delivery_stream.yaml"

    def create_cloud_service_type(self):
        result = []
        deliverystream_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonKinesisFirehose",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-kinesis-firehose.svg"
            },
            labels=["Analytics", "Streaming"],
        )
        result.append(deliverystream_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_delivery_streams(options, region)

    def _collect_delivery_streams(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::KinesisFirehose::DeliveryStream"

        try:
            delivery_streams, account_id = self.connector.list_delivery_streams()

            for stream in delivery_streams:
                try:
                    stream_name = stream.get("DeliveryStreamName")

                    # Get delivery stream tags
                    tags = self._get_delivery_stream_tags(stream_name)

                    stream_data = {
                        "delivery_stream_name": stream_name,
                        "delivery_stream_arn": stream.get("DeliveryStreamARN"),
                        "delivery_stream_status": stream.get(
                            "DeliveryStreamStatus", ""
                        ),
                        "delivery_stream_type": stream.get("DeliveryStreamType", ""),
                        "version_id": stream.get("VersionId", ""),
                        "create_timestamp": stream.get("CreateTimestamp"),
                        "last_update_timestamp": stream.get("LastUpdateTimestamp"),
                        "source": stream.get("Source", {}),
                        "destinations": stream.get("Destinations", []),
                        "has_more_destinations": stream.get(
                            "HasMoreDestinations", False
                        ),
                    }

                    stream_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/firehose/home?region={region}#/details/{stream_name}"
                    resource_id = stream_name
                    reference = self.get_reference(resource_id, link)

                    delivery_stream_vo = DeliveryStream(stream_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=stream_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=delivery_stream_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=stream_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_delivery_streams] [{stream.get("DeliveryStreamName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_delivery_streams] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_delivery_stream_tags(self, stream_name):
        """Get delivery stream tags"""
        try:
            return self.connector.get_delivery_stream_tags(stream_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for delivery stream {stream_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
