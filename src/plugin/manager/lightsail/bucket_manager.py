from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Bucket


class BucketManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Bucket"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Bucket"
        self.metadata_path = "metadata/lightsail/bucket.yaml"

    def create_cloud_service_type(self):
        result = []
        bucket_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonLightsail",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-lightsail.svg"
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
        cloudtrail_resource_type = "AWS::Lightsail::Bucket"

        try:
            buckets, account_id = self.connector.list_lightsail_buckets()

            for bucket in buckets:
                try:
                    bucket_name = bucket.get("Name")
                    bucket_arn = bucket.get("Arn")

                    # Get bucket tags
                    tags = self._get_bucket_tags(bucket_arn)

                    # Get bucket objects
                    objects = self._get_bucket_objects(bucket_name)

                    # Get bucket access keys
                    access_keys = self._get_bucket_access_keys(bucket_name)

                    bucket_data = {
                        "name": bucket_name,
                        "arn": bucket_arn,
                        "created_at": bucket.get("CreatedAt"),
                        "location": bucket.get("Location", {}),
                        "resource_type": bucket.get("ResourceType", ""),
                        "tags": bucket.get("Tags", []),
                        "support_code": bucket.get("SupportCode", ""),
                        "url": bucket.get("Url", ""),
                        "location_regional_domain_name": bucket.get(
                            "LocationRegionalDomainName", ""
                        ),
                        "state": bucket.get("State", {}),
                        "access_rules": bucket.get("AccessRules", {}),
                        "readonly_access_accounts": bucket.get(
                            "ReadonlyAccessAccounts", []
                        ),
                        "resource_receiving_access": bucket.get(
                            "ResourceReceivingAccess", ""
                        ),
                        "access_log_config": bucket.get("AccessLogConfig", {}),
                        "versioning": bucket.get("Versioning", ""),
                        "object_versioning": bucket.get("ObjectVersioning", ""),
                        "transfer_acceleration": bucket.get("TransferAcceleration", {}),
                        "notification_config": bucket.get("NotificationConfig", {}),
                        "objects": objects,
                        "access_keys": access_keys,
                    }

                    bucket_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/storage/buckets/{bucket_name}"
                    resource_id = bucket_arn
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
                    _LOGGER.error(
                        f'[list_lightsail_buckets] [{bucket.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_buckets] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_bucket_tags(self, bucket_arn):
        """Get bucket tags"""
        try:
            return self.connector.get_bucket_tags(bucket_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for bucket {bucket_arn}: {e}")
            return []

    def _get_bucket_objects(self, bucket_name):
        """Get bucket objects"""
        try:
            return self.connector.get_bucket_objects(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get objects for bucket {bucket_name}: {e}")
            return []

    def _get_bucket_access_keys(self, bucket_name):
        """Get bucket access keys"""
        try:
            return self.connector.get_bucket_access_keys(bucket_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get access keys for bucket {bucket_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
