from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.secrets_manager import Secret


class SecretManager(ResourceManager):
    cloud_service_group = "SecretsManager"
    cloud_service_type = "Secret"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "SecretsManager"
        self.cloud_service_type = "Secret"
        self.metadata_path = "metadata/secrets_manager/secret.yaml"

    def create_cloud_service_type(self):
        result = []
        secret_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonSecretsManager",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-secrets-manager.svg"
            },
            labels=["Security"],
        )
        result.append(secret_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_secrets(options, region)

    def _collect_secrets(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::SecretsManager::Secret"

        try:
            secrets, account_id = self.connector.list_secrets()

            for secret in secrets:
                try:
                    secret_name = secret.get("Name")
                    secret_arn = secret.get("ARN")

                    # Get secret tags
                    tags = self._get_secret_tags(secret_arn)

                    # Get secret value (metadata only, not actual secret value)
                    secret_value = self._get_secret_metadata(secret_arn)

                    secret_data = {
                        "arn": secret_arn,
                        "name": secret_name,
                        "description": secret.get("Description", ""),
                        "kms_key_id": secret.get("KmsKeyId", ""),
                        "rotation_enabled": secret.get("RotationEnabled", False),
                        "rotation_lambda_arn": secret.get("RotationLambdaArn", ""),
                        "rotation_rules": secret.get("RotationRules", {}),
                        "last_rotated_date": secret.get("LastRotatedDate"),
                        "last_changed_date": secret.get("LastChangedDate"),
                        "last_accessed_date": secret.get("LastAccessedDate"),
                        "deleted_date": secret.get("DeletedDate"),
                        "next_rotation_date": secret.get("NextRotationDate"),
                        "tags": secret.get("Tags", []),
                        "secret_versions_to_stages": secret.get(
                            "SecretVersionsToStages", {}
                        ),
                        "owning_service": secret.get("OwningService", ""),
                        "created_date": secret.get("CreatedDate"),
                        "primary_region": secret.get("PrimaryRegion", ""),
                        "replication_status": secret.get("ReplicationStatus", []),
                        "secret_value": secret_value,
                    }

                    secret_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/secretsmanager/secret?name={secret_name}"
                    resource_id = secret_arn
                    reference = self.get_reference(resource_id, link)

                    secret_vo = Secret(secret_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=secret_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=secret_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=secret_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_secrets] [{secret.get("Name")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_secrets] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_secret_tags(self, secret_arn):
        """Get secret tags"""
        try:
            return self.connector.get_secret_tags(secret_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for secret {secret_arn}: {e}")
            return []

    def _get_secret_metadata(self, secret_arn):
        """Get secret metadata (not the actual secret value)"""
        try:
            return self.connector.get_secret_metadata(secret_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get metadata for secret {secret_arn}: {e}")
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
