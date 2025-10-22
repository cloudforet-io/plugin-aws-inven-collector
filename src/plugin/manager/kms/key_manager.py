from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.kms import Key


class KeyManager(ResourceManager):
    cloud_service_group = "KMS"
    cloud_service_type = "Key"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "KMS"
        self.cloud_service_type = "Key"
        self.metadata_path = "metadata/kms/key.yaml"

    def create_cloud_service_type(self):
        result = []
        key_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AWSKMS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-kms.svg"
            },
            labels=["Security"],
        )
        result.append(key_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_keys(options, region)

    def _collect_keys(self, options, region):
        region_name = region

        try:
            keys, account_id = self.connector.list_kms_keys()

            for key in keys:
                try:
                    key_id = key.get("KeyId")
                    key_arn = key.get("Arn")

                    # Get key tags
                    tags = self._get_key_tags(key_id)

                    # Get key aliases
                    aliases = self._get_key_aliases(key_id)

                    # Get key policy
                    policy = self._get_key_policy(key_id)

                    # Get key grants
                    grants = self._get_key_grants(key_id)

                    key_data = {
                        "key_id": key_id,
                        "arn": key_arn,
                        "aws_account_id": key.get("AWSAccountId", ""),
                        "creation_date": key.get("CreationDate"),
                        "enabled": key.get("Enabled", False),
                        "description": key.get("Description", ""),
                        "key_usage": key.get("KeyUsage", ""),
                        "key_state": key.get("KeyState", ""),
                        "deletion_date": key.get("DeletionDate"),
                        "valid_to": key.get("ValidTo"),
                        "origin": key.get("Origin", ""),
                        "custom_key_store_id": key.get("CustomKeyStoreId", ""),
                        "cloud_hsm_cluster_id": key.get("CloudHsmClusterId", ""),
                        "expiration_model": key.get("ExpirationModel", ""),
                        "key_manager": key.get("KeyManager", ""),
                        "customer_master_key_spec": key.get(
                            "CustomerMasterKeySpec", ""
                        ),
                        "key_spec": key.get("KeySpec", ""),
                        "encryption_algorithms": key.get("EncryptionAlgorithms", []),
                        "signing_algorithms": key.get("SigningAlgorithms", []),
                        "multi_region": key.get("MultiRegion", False),
                        "multi_region_configuration": key.get(
                            "MultiRegionConfiguration", {}
                        ),
                        "pending_deletion_window_in_days": key.get(
                            "PendingDeletionWindowInDays", 0
                        ),
                        "mac_algorithms": key.get("MacAlgorithms", []),
                        "xks_key_configuration": key.get("XksKeyConfiguration", {}),
                        "aliases": aliases,
                        "policy": policy,
                        "grants": grants,
                    }

                    key_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                key_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                key_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/kms/home?region={region}#/kms/keys/{key_id}"
                    resource_id = key_arn
                    reference = self.get_reference(resource_id, link)

                    key_vo = Key(key_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=key_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=key_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=key_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_kms_keys] [{key.get("KeyId")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_kms_keys] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_key_tags(self, key_id):
        """Get key tags"""
        try:
            return self.connector.get_key_tags(key_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for key {key_id}: {e}")
            return []

    def _get_key_aliases(self, key_id):
        """Get key aliases"""
        try:
            return self.connector.get_key_aliases(key_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get aliases for key {key_id}: {e}")
            return []

    def _get_key_policy(self, key_id):
        """Get key policy"""
        try:
            return self.connector.get_key_policy(key_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get policy for key {key_id}: {e}")
            return {}

    def _get_key_grants(self, key_id):
        """Get key grants"""
        try:
            return self.connector.get_key_grants(key_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get grants for key {key_id}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
