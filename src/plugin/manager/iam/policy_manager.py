from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER


class PolicyManager(ResourceManager):
    cloud_service_group = "IAM"
    cloud_service_type = "Policy"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "Policy"
        self.metadata_path = "metadata/iam/policy.yaml"

    def create_cloud_service_type(self):
        result = []
        policy_cst_result = make_cloud_service_type(
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
        result.append(policy_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_policies(options, region)

    def _collect_policies(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::IAM::Policy"

        try:
            policies, account_id = self.connector.list_iam_policies()

            for policy in policies:
                try:
                    policy_arn = policy.get("Arn")
                    policy_name = policy.get("PolicyName")

                    # Get policy tags
                    tags = self._get_policy_tags(policy_arn)

                    # Get policy version
                    policy_version = self._get_policy_version(policy_arn)

                    policy_data = {
                        "policy_name": policy_name,
                        "arn": policy_arn,
                        "policy_id": policy.get("PolicyId", ""),
                        "path": policy.get("Path", ""),
                        "default_version_id": policy.get("DefaultVersionId", ""),
                        "attachment_count": policy.get("AttachmentCount", 0),
                        "permissions_boundary_usage_count": policy.get(
                            "PermissionsBoundaryUsageCount", 0
                        ),
                        "is_attachable": policy.get("IsAttachable", False),
                        "description": policy.get("Description", ""),
                        "create_date": policy.get("CreateDate"),
                        "update_date": policy.get("UpdateDate"),
                        "policy_version": policy_version,
                    }

                    policy_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/iam/home?region={region}#/policies/{policy_arn}"
                    resource_id = policy_arn
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=policy_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=policy_data,
                        account=options.get("account_id"),
                        reference=reference,
                        tags=policy_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_iam_policies] [{policy.get("PolicyName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_iam_policies] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_policy_tags(self, policy_arn):
        """Get policy tags"""
        try:
            return self.connector.get_policy_tags(policy_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for policy {policy_arn}: {e}")
            return []

    def _get_policy_version(self, policy_arn):
        """Get policy version"""
        try:
            return self.connector.get_policy_version(policy_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get version for policy {policy_arn}: {e}")
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
