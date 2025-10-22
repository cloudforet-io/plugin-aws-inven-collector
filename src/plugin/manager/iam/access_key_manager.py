from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER


class AccessKeyManager(ResourceManager):
    cloud_service_group = "IAM"
    cloud_service_type = "AccessKey"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "AccessKey"
        self.metadata_path = "metadata/iam/access_key.yaml"

    def create_cloud_service_type(self):
        result = []
        access_key_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonIAM",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-iam.svg"
            },
            labels=["Security"],
        )
        result.append(access_key_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_access_keys(options, region)

    def _collect_access_keys(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::IAM::AccessKey"

        try:
            access_keys, account_id = self.connector.list_iam_access_keys()

            for access_key in access_keys:
                try:
                    access_key_id = access_key.get("AccessKeyId")
                    user_name = access_key.get("UserName")

                    # Get access key last used
                    last_used = self._get_access_key_last_used(access_key_id)

                    access_key_data = {
                        "access_key_id": access_key_id,
                        "user_name": user_name,
                        "status": access_key.get("Status", ""),
                        "create_date": access_key.get("CreateDate"),
                        "last_used": last_used,
                    }

                    access_key_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": {},
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/iam/home?region={region}#/users/{user_name}"
                    resource_id = access_key_id
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=access_key_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=access_key_data,
                        account=options.get("account_id"),
                        reference=reference,
                        tags={},
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_iam_access_keys] [{access_key.get("AccessKeyId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_iam_access_keys] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_access_key_last_used(self, access_key_id):
        """Get access key last used"""
        try:
            return self.connector.get_access_key_last_used(access_key_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get last used for access key {access_key_id}: {e}"
            )
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
