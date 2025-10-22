import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Topic(Model):
    topic_arn = StringType(deserialize_from="TopicArn")
    display_name = StringType(deserialize_from="DisplayName")
    owner = StringType(deserialize_from="Owner")
    policy = StringType(deserialize_from="Policy")
    delivery_policy = StringType(deserialize_from="DeliveryPolicy")
    effective_delivery_policy = StringType(deserialize_from="EffectiveDeliveryPolicy")
    subscriptions_confirmed = IntType(deserialize_from="SubscriptionsConfirmed")
    subscriptions_deleted = IntType(deserialize_from="SubscriptionsDeleted")
    subscriptions_pending = IntType(deserialize_from="SubscriptionsPending")
    kms_master_key_id = StringType(deserialize_from="KmsMasterKeyId")
    fifo_topic = BooleanType(deserialize_from="FifoTopic")
    content_based_deduplication = BooleanType(
        deserialize_from="ContentBasedDeduplication"
    )
    tags = StringType(deserialize_from="Tags")
