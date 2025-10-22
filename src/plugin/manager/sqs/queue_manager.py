from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.sqs import Queue


class QueueManager(ResourceManager):
    cloud_service_group = "SQS"
    cloud_service_type = "Queue"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "SQS"
        self.cloud_service_type = "Queue"
        self.metadata_path = "metadata/sqs/queue.yaml"

    def create_cloud_service_type(self):
        result = []
        queue_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonSQS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-sqs.svg"
            },
            labels=["Messaging"],
        )
        result.append(queue_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_queues(options, region)

    def _collect_queues(self, options, region):
        region_name = region

        try:
            queues, account_id = self.connector.list_sqs_queues()

            for queue in queues:
                try:
                    queue_url = queue.get("QueueUrl")
                    queue_name = queue.get("QueueName")

                    # Get queue attributes
                    attributes = self._get_queue_attributes(queue_url)

                    # Get queue tags
                    tags = self._get_queue_tags(queue_url)

                    queue_data = {
                        "queue_url": queue_url,
                        "queue_name": queue_name,
                        "queue_arn": attributes.get("QueueArn", ""),
                        "visibility_timeout_seconds": attributes.get(
                            "VisibilityTimeoutSeconds", "30"
                        ),
                        "message_retention_period": attributes.get(
                            "MessageRetentionPeriod", "1209600"
                        ),
                        "maximum_message_size": attributes.get(
                            "MaximumMessageSize", "262144"
                        ),
                        "delay_seconds": attributes.get("DelaySeconds", "0"),
                        "receive_message_wait_time_seconds": attributes.get(
                            "ReceiveMessageWaitTimeSeconds", "0"
                        ),
                        "redrive_policy": attributes.get("RedrivePolicy", ""),
                        "fifo_queue": attributes.get("FifoQueue", "false").lower()
                        == "true",
                        "content_based_deduplication": attributes.get(
                            "ContentBasedDeduplication", "false"
                        ).lower()
                        == "true",
                        "kms_master_key_id": attributes.get("KmsMasterKeyId", ""),
                        "kms_data_key_reuse_period_seconds": attributes.get(
                            "KmsDataKeyReusePeriodSeconds", "300"
                        ),
                        "deduplication_scope": attributes.get("DeduplicationScope", ""),
                        "fifo_throughput_limit": attributes.get(
                            "FifoThroughputLimit", ""
                        ),
                        "redrive_allow_policy": attributes.get(
                            "RedriveAllowPolicy", ""
                        ),
                        "sqs_managed_sse_enabled": attributes.get(
                            "SqsManagedSseEnabled", "false"
                        ).lower()
                        == "true",
                    }

                    queue_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                queue_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                queue_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/sqs/v2/home?region={region}#/queues/{queue_url}"
                    resource_id = queue_url
                    reference = self.get_reference(resource_id, link)

                    queue_vo = Queue(queue_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=queue_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=queue_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=queue_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_sqs_queues] [{queue.get("QueueName")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_sqs_queues] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_queue_attributes(self, queue_url):
        """Get queue attributes"""
        try:
            return self.connector.get_queue_attributes(queue_url)
        except Exception as e:
            _LOGGER.warning(f"Failed to get attributes for queue {queue_url}: {e}")
            return {}

    def _get_queue_tags(self, queue_url):
        """Get queue tags"""
        try:
            return self.connector.get_queue_tags(queue_url)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for queue {queue_url}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
