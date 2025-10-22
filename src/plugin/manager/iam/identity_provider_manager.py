from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER


class IdentityProviderManager(ResourceManager):
    cloud_service_group = "IAM"
    cloud_service_type = "IdentityProvider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "IdentityProvider"
        self.metadata_path = "metadata/iam/identity_provider.yaml"

    def create_cloud_service_type(self):
        result = []
        identity_provider_cst_result = make_cloud_service_type(
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
        result.append(identity_provider_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_identity_providers(options, region)

    def _collect_identity_providers(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::IAM::SAMLProvider"

        try:
            identity_providers, account_id = (
                self.connector.list_iam_identity_providers()
            )

            for identity_provider in identity_providers:
                try:
                    provider_arn = identity_provider.get("Arn")
                    provider_name = identity_provider.get("ProviderName")

                    # Get identity provider tags
                    tags = self._get_identity_provider_tags(provider_arn)

                    identity_provider_data = {
                        "provider_name": provider_name,
                        "arn": provider_arn,
                        "create_date": identity_provider.get("CreateDate"),
                        "valid_until": identity_provider.get("ValidUntil"),
                        "tags": identity_provider.get("Tags", []),
                    }

                    identity_provider_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/iam/home?region={region}#/providers"
                    resource_id = provider_arn
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=provider_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=identity_provider_data,
                        account=options.get("account_id"),
                        reference=reference,
                        tags=identity_provider_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_iam_identity_providers] [{identity_provider.get("ProviderName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_iam_identity_providers] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_identity_provider_tags(self, provider_arn):
        """Get identity provider tags"""
        try:
            return self.connector.get_identity_provider_tags(provider_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for identity provider {provider_arn}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
