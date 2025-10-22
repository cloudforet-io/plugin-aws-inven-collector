import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Queue(Model):
    queue_url = StringType(deserialize_from="QueueUrl")
    approximate_number_of_messages = IntType(
        deserialize_from="ApproximateNumberOfMessages"
    )
    approximate_number_of_messages_not_visible = IntType(
        deserialize_from="ApproximateNumberOfMessagesNotVisible"
    )
    approximate_number_of_messages_delayed = IntType(
        deserialize_from="ApproximateNumberOfMessagesDelayed"
    )
    created_timestamp = DateTimeType(deserialize_from="CreatedTimestamp")
    last_modified_timestamp = DateTimeType(deserialize_from="LastModifiedTimestamp")
    visibility_timeout_seconds = IntType(deserialize_from="VisibilityTimeoutSeconds")
    maximum_message_size = IntType(deserialize_from="MaximumMessageSize")
    message_retention_period = IntType(deserialize_from="MessageRetentionPeriod")
    delay_seconds = IntType(deserialize_from="DelaySeconds")
    receive_message_wait_time_seconds = IntType(
        deserialize_from="ReceiveMessageWaitTimeSeconds"
    )
    policy = StringType(deserialize_from="Policy")
    redrive_policy = StringType(deserialize_from="RedrivePolicy")
    fifo_queue = BooleanType(deserialize_from="FifoQueue")
    content_based_deduplication = BooleanType(
        deserialize_from="ContentBasedDeduplication"
    )
    kms_master_key_id = StringType(deserialize_from="KmsMasterKeyId")
    kms_data_key_reuse_period_seconds = IntType(
        deserialize_from="KmsDataKeyReusePeriodSeconds"
    )
    deduplication_scope = StringType(deserialize_from="DeduplicationScope")
    fifo_throughput_limit = StringType(deserialize_from="FifoThroughputLimit")
    redrive_allow_policy = StringType(deserialize_from="RedriveAllowPolicy")
    sqs_managed_sse_enabled = BooleanType(deserialize_from="SqsManagedSseEnabled")
    tags = StringType(deserialize_from="Tags")
