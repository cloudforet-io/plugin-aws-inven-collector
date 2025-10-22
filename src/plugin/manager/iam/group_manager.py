from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER


class GroupManager(ResourceManager):
    cloud_service_group = "IAM"
    cloud_service_type = "Group"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "Group"
        self.metadata_path = "metadata/iam/group.yaml"

    def create_cloud_service_type(self):
        result = []
        group_cst_result = make_cloud_service_type(
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
        result.append(group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_groups(options, region)

    def _collect_groups(self, options, region):
        region_name = region

        try:
            groups, account_id = self.connector.list_iam_groups()

            for group in groups:
                try:
                    group_name = group.get("GroupName")
                    group_arn = group.get("Arn")

                    # Get group tags
                    tags = self._get_group_tags(group_name)

                    # Get group policies
                    policies = self._get_group_policies(group_name)

                    # Get group users
                    users = self._get_group_users(group_name)

                    group_data = {
                        "group_name": group_name,
                        "arn": group_arn,
                        "group_id": group.get("GroupId", ""),
                        "path": group.get("Path", ""),
                        "create_date": group.get("CreateDate"),
                        "policies": policies,
                        "users": users,
                    }

                    group_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                group_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                group_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/iam/home?region={region}#/groups/{group_name}"
                    resource_id = group_arn
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=group_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=group_data,
                        account=options.get("account_id"),
                        reference=reference,
                        tags=group_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_iam_groups] [{group.get("GroupName")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_iam_groups] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_group_tags(self, group_name):
        """Get group tags"""
        try:
            return self.connector.get_group_tags(group_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for group {group_name}: {e}")
            return []

    def _get_group_policies(self, group_name):
        """Get group policies"""
        try:
            return self.connector.get_group_policies(group_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get policies for group {group_name}: {e}")
            return []

    def _get_group_users(self, group_name):
        """Get group users"""
        try:
            return self.connector.get_group_users(group_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get users for group {group_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
