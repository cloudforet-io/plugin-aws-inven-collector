from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER


class RoleManager(ResourceManager):
    cloud_service_group = "IAM"
    cloud_service_type = "Role"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "Role"
        self.metadata_path = "metadata/iam/role.yaml"

    def create_cloud_service_type(self):
        result = []
        role_cst_result = make_cloud_service_type(
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
        result.append(role_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_roles(options, region)

    def _collect_roles(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::IAM::Role"

        try:
            roles, account_id = self.connector.list_iam_roles()

            for role in roles:
                try:
                    role_name = role.get("RoleName")
                    role_arn = role.get("Arn")

                    # Get role tags
                    tags = self._get_role_tags(role_name)

                    # Get role policies
                    policies = self._get_role_policies(role_name)

                    role_data = {
                        "role_name": role_name,
                        "arn": role_arn,
                        "role_id": role.get("RoleId", ""),
                        "path": role.get("Path", ""),
                        "create_date": role.get("CreateDate"),
                        "assume_role_policy_document": role.get(
                            "AssumeRolePolicyDocument", ""
                        ),
                        "description": role.get("Description", ""),
                        "max_session_duration": role.get("MaxSessionDuration", 0),
                        "permissions_boundary": role.get("PermissionsBoundary", {}),
                        "role_last_used": role.get("RoleLastUsed", {}),
                        "tags": role.get("Tags", []),
                        "policies": policies,
                    }

                    role_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/iam/home?region={region}#/roles/{role_name}"
                    resource_id = role_arn
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=role_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=role_data,
                        account=options.get("account_id"),
                        reference=reference,
                        tags=role_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_iam_roles] [{role.get("RoleName")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_iam_roles] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_role_tags(self, role_name):
        """Get role tags"""
        try:
            return self.connector.get_role_tags(role_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for role {role_name}: {e}")
            return []

    def _get_role_policies(self, role_name):
        """Get role policies"""
        try:
            return self.connector.get_role_policies(role_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get policies for role {role_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
