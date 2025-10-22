from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.iam import User


class UserManager(ResourceManager):
    cloud_service_group = "IAM"
    cloud_service_type = "User"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "User"
        self.metadata_path = "metadata/iam/user.yaml"

    def create_cloud_service_type(self):
        result = []
        user_cst_result = make_cloud_service_type(
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
        result.append(user_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_users(options, region)

    def _collect_users(self, options, region):
        region_name = region

        try:
            users, account_id = self.connector.list_iam_users()

            for user in users:
                try:
                    user_name = user.get("UserName")
                    user_arn = user.get("Arn")

                    # Get user tags
                    tags = self._get_user_tags(user_name)

                    # Get user groups
                    groups = self._get_user_groups(user_name)

                    # Get user policies
                    policies = self._get_user_policies(user_name)

                    # Get user access keys
                    access_keys = self._get_user_access_keys(user_name)

                    # Get user MFA devices
                    mfa_devices = self._get_user_mfa_devices(user_name)

                    user_data = {
                        "user_name": user_name,
                        "arn": user_arn,
                        "user_id": user.get("UserId", ""),
                        "path": user.get("Path", ""),
                        "create_date": user.get("CreateDate"),
                        "password_last_used": user.get("PasswordLastUsed"),
                        "permissions_boundary": user.get("PermissionsBoundary", {}),
                        "tags": user.get("Tags", []),
                        "groups": groups,
                        "policies": policies,
                        "access_keys": access_keys,
                        "mfa_devices": mfa_devices,
                    }

                    user_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                user_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                user_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/iam/home?region={region}#/users/{user_name}"
                    resource_id = user_arn
                    reference = self.get_reference(resource_id, link)

                    user_vo = User(user_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=user_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=user_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=user_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_iam_users] [{user.get("UserName")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_iam_users] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_user_tags(self, user_name):
        """Get user tags"""
        try:
            return self.connector.get_user_tags(user_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for user {user_name}: {e}")
            return []

    def _get_user_groups(self, user_name):
        """Get user groups"""
        try:
            return self.connector.get_user_groups(user_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get groups for user {user_name}: {e}")
            return []

    def _get_user_policies(self, user_name):
        """Get user policies"""
        try:
            return self.connector.get_user_policies(user_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get policies for user {user_name}: {e}")
            return []

    def _get_user_access_keys(self, user_name):
        """Get user access keys"""
        try:
            return self.connector.get_user_access_keys(user_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get access keys for user {user_name}: {e}")
            return []

    def _get_user_mfa_devices(self, user_name):
        """Get user MFA devices"""
        try:
            return self.connector.get_user_mfa_devices(user_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get MFA devices for user {user_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
