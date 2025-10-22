from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.s3 import Bucket


class BucketManager(ResourceManager):
    cloud_service_group = "S3"
    cloud_service_type = "Bucket"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "S3"
        self.cloud_service_type = "Bucket"
        self.metadata_path = "metadata/s3/bucket.yaml"

    def create_cloud_service_type(self):
        result = []
        bucket_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonS3",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-s3.svg"
            },
            labels=["Storage"],
        )
        result.append(bucket_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_buckets(options, region)

    def _collect_buckets(self, options, region):
        region_name = region

        try:
            buckets, account_id = self.connector.list_s3_buckets()

            for bucket in buckets:
                try:
                    bucket_name = bucket.get("Name")

                    # Get bucket tags
                    tags = self._get_bucket_tags(bucket_name)

                    # Get bucket versioning
                    versioning = self._get_bucket_versioning(bucket_name)

                    # Get bucket encryption
                    encryption = self._get_bucket_encryption(bucket_name)

                    # Get bucket policy
                    policy = self._get_bucket_policy(bucket_name)

                    # Get bucket ACL
                    acl = self._get_bucket_acl(bucket_name)

                    # Get bucket location
                    location = self._get_bucket_location(bucket_name)

                    # Get bucket notification configuration
                    notification = self._get_bucket_notification(bucket_name)

                    # Get bucket website configuration
                    website = self._get_bucket_website(bucket_name)

                    # Get bucket cors configuration
                    cors = self._get_bucket_cors(bucket_name)

                    # Get bucket lifecycle configuration
                    lifecycle = self._get_bucket_lifecycle(bucket_name)

                    # Get bucket logging
                    logging = self._get_bucket_logging(bucket_name)

                    # Get bucket request payment
                    request_payment = self._get_bucket_request_payment(bucket_name)

                    # Get bucket transfer acceleration
                    transfer_acceleration = self._get_bucket_transfer_acceleration(
                        bucket_name
                    )

                    # Get bucket object lock configuration
                    object_lock = self._get_bucket_object_lock(bucket_name)

                    bucket_data = {
                        "name": bucket_name,
                        "creation_date": bucket.get("CreationDate"),
                        "versioning": versioning,
                        "encryption": encryption,
                        "policy": policy,
                        "acl": acl,
                        "location": location,
                        "notification_configuration": notification,
                        "website_configuration": website,
                        "cors_configuration": cors,
                        "lifecycle_configuration": lifecycle,
                        "logging": logging,
                        "request_payment": request_payment,
                        "transfer_acceleration": transfer_acceleration,
                        "object_lock_configuration": object_lock,
                    }

                    bucket_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                bucket_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                bucket_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/s3/buckets/{bucket_name}"
                    resource_id = bucket_name
                    reference = self.get_reference(resource_id, link)

                    bucket_vo = Bucket(bucket_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=bucket_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=bucket_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=bucket_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_s3_buckets] [{bucket.get("Name")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_s3_buckets] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_bucket_tags(self, bucket_name):
        """Get bucket tags"""
        try:
            return self.connector.get_bucket_tags(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for bucket {bucket_name}: {e}")
            return []

    def _get_bucket_versioning(self, bucket_name):
        """Get bucket versioning"""
        try:
            return self.connector.get_bucket_versioning(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get versioning for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_encryption(self, bucket_name):
        """Get bucket encryption"""
        try:
            return self.connector.get_bucket_encryption(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get encryption for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_policy(self, bucket_name):
        """Get bucket policy"""
        try:
            return self.connector.get_bucket_policy(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get policy for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_acl(self, bucket_name):
        """Get bucket ACL"""
        try:
            return self.connector.get_bucket_acl(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get ACL for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_location(self, bucket_name):
        """Get bucket location"""
        try:
            return self.connector.get_bucket_location(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get location for bucket {bucket_name}: {e}")
            return ""

    def _get_bucket_notification(self, bucket_name):
        """Get bucket notification configuration"""
        try:
            return self.connector.get_bucket_notification(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get notification for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_website(self, bucket_name):
        """Get bucket website configuration"""
        try:
            return self.connector.get_bucket_website(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get website for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_cors(self, bucket_name):
        """Get bucket CORS configuration"""
        try:
            return self.connector.get_bucket_cors(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get CORS for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_lifecycle(self, bucket_name):
        """Get bucket lifecycle configuration"""
        try:
            return self.connector.get_bucket_lifecycle(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get lifecycle for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_logging(self, bucket_name):
        """Get bucket logging"""
        try:
            return self.connector.get_bucket_logging(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get logging for bucket {bucket_name}: {e}")
            return {}

    def _get_bucket_request_payment(self, bucket_name):
        """Get bucket request payment"""
        try:
            return self.connector.get_bucket_request_payment(bucket_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get request payment for bucket {bucket_name}: {e}"
            )
            return {}

    def _get_bucket_transfer_acceleration(self, bucket_name):
        """Get bucket transfer acceleration"""
        try:
            return self.connector.get_bucket_transfer_acceleration(bucket_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get transfer acceleration for bucket {bucket_name}: {e}"
            )
            return {}

    def _get_bucket_object_lock(self, bucket_name):
        """Get bucket object lock configuration"""
        try:
            return self.connector.get_bucket_object_lock(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get object lock for bucket {bucket_name}: {e}")
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
