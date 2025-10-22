import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class DeliveryStream(Model):
    delivery_stream_name = StringType(deserialize_from="DeliveryStreamName")
    delivery_stream_arn = StringType(deserialize_from="DeliveryStreamARN")
    delivery_stream_status = StringType(
        deserialize_from="DeliveryStreamStatus",
        choices=(
            "CREATING",
            "CREATING_FAILED",
            "DELETING",
            "DELETING_FAILED",
            "ACTIVE",
            "SUSPENDED",
        ),
    )
    delivery_stream_type = StringType(
        deserialize_from="DeliveryStreamType",
        choices=("DirectPut", "KinesisStreamAsSource"),
    )
    version_id = StringType(deserialize_from="VersionId")
    create_timestamp = DateTimeType(deserialize_from="CreateTimestamp")
    last_update_timestamp = DateTimeType(deserialize_from="LastUpdateTimestamp")
    source = StringType(deserialize_from="Source")
    destinations = StringType(deserialize_from="Destinations")
    has_more_destinations = BooleanType(deserialize_from="HasMoreDestinations")
    tags = StringType(deserialize_from="Tags")

    def reference(self, region_code):
        return {
            "resource_id": self.delivery_stream_arn,
            "external_link": f"https://console.aws.amazon.com/firehose/home?region={region_code}#/details/{self.delivery_stream_name}",
        }
