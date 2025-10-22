from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.sns import Topic


class TopicManager(ResourceManager):
    cloud_service_group = "SNS"
    cloud_service_type = "Topic"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "SNS"
        self.cloud_service_type = "Topic"
        self.metadata_path = "metadata/sns/topic.yaml"

    def create_cloud_service_type(self):
        result = []
        topic_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonSNS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-sns.svg"
            },
            labels=["Messaging"],
        )
        result.append(topic_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_topics(options, region)

    def _collect_topics(self, options, region):
        region_name = region

        try:
            topics, account_id = self.connector.list_sns_topics()

            for topic in topics:
                try:
                    topic_arn = topic.get("TopicArn")
                    topic_name = (
                        topic.get("TopicName", "").split(":")[-1]
                        if ":" in topic.get("TopicName", "")
                        else topic.get("TopicName", "")
                    )

                    # Get topic attributes
                    attributes = self._get_topic_attributes(topic_arn)

                    # Get topic subscriptions
                    subscriptions = self._get_topic_subscriptions(topic_arn)

                    # Get topic tags
                    tags = self._get_topic_tags(topic_arn)

                    topic_data = {
                        "topic_arn": topic_arn,
                        "topic_name": topic_name,
                        "display_name": attributes.get("DisplayName", ""),
                        "owner": attributes.get("Owner", ""),
                        "subscriptions_confirmed": attributes.get(
                            "SubscriptionsConfirmed", "0"
                        ),
                        "subscriptions_deleted": attributes.get(
                            "SubscriptionsDeleted", "0"
                        ),
                        "subscriptions_pending": attributes.get(
                            "SubscriptionsPending", "0"
                        ),
                        "effective_delivery_policy": attributes.get(
                            "EffectiveDeliveryPolicy", ""
                        ),
                        "policy": attributes.get("Policy", ""),
                        "kms_master_key_id": attributes.get("KmsMasterKeyId", ""),
                        "fifo_topic": attributes.get("FifoTopic", "false").lower()
                        == "true",
                        "content_based_deduplication": attributes.get(
                            "ContentBasedDeduplication", "false"
                        ).lower()
                        == "true",
                        "subscriptions": subscriptions,
                    }

                    topic_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                topic_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                topic_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/sns/v3/home?region={region}#/topic/{topic_arn}"
                    resource_id = topic_arn
                    reference = self.get_reference(resource_id, link)

                    topic_vo = Topic(topic_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=topic_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=topic_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=topic_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_sns_topics] [{topic.get("TopicArn")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_sns_topics] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_topic_attributes(self, topic_arn):
        """Get topic attributes"""
        try:
            return self.connector.get_topic_attributes(topic_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get attributes for topic {topic_arn}: {e}")
            return {}

    def _get_topic_subscriptions(self, topic_arn):
        """Get topic subscriptions"""
        try:
            return self.connector.get_topic_subscriptions(topic_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get subscriptions for topic {topic_arn}: {e}")
            return []

    def _get_topic_tags(self, topic_arn):
        """Get topic tags"""
        try:
            return self.connector.get_topic_tags(topic_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for topic {topic_arn}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
