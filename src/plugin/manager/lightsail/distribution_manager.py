from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Distribution


class DistributionManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Distribution"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Distribution"
        self.metadata_path = "metadata/lightsail/distribution.yaml"

    def create_cloud_service_type(self):
        result = []
        distribution_cst_result = make_cloud_service_type(
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
            labels=["Networking"],
        )
        result.append(distribution_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_distributions(options, region)

    def _collect_distributions(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Lightsail::Distribution"

        try:
            distributions, account_id = self.connector.list_lightsail_distributions()

            for distribution in distributions:
                try:
                    distribution_name = distribution.get("Name")
                    distribution_arn = distribution.get("Arn")

                    # Get distribution tags
                    tags = self._get_distribution_tags(distribution_arn)

                    # Get distribution cache behaviors
                    cache_behaviors = self._get_distribution_cache_behaviors(
                        distribution_name
                    )

                    distribution_data = {
                        "name": distribution_name,
                        "arn": distribution_arn,
                        "created_at": distribution.get("CreatedAt"),
                        "location": distribution.get("Location", {}),
                        "resource_type": distribution.get("ResourceType", ""),
                        "tags": distribution.get("Tags", []),
                        "alternative_domain_names": distribution.get(
                            "AlternativeDomainNames", []
                        ),
                        "status": distribution.get("Status", ""),
                        "is_enabled": distribution.get("IsEnabled", False),
                        "domain_name": distribution.get("DomainName", ""),
                        "bundle_id": distribution.get("BundleId", ""),
                        "certificate_name": distribution.get("CertificateName", ""),
                        "origin": distribution.get("Origin", {}),
                        "origin_public_dns": distribution.get("OriginPublicDNS", ""),
                        "default_cache_behavior": distribution.get(
                            "DefaultCacheBehavior", {}
                        ),
                        "cache_behavior_settings": distribution.get(
                            "CacheBehaviorSettings", {}
                        ),
                        "cache_behaviors": cache_behaviors,
                        "able_to_update_bundle": distribution.get(
                            "AbleToUpdateBundle", False
                        ),
                        "ip_address_type": distribution.get("IpAddressType", ""),
                        "cache_behaviors_count": distribution.get(
                            "CacheBehaviorsCount", 0
                        ),
                    }

                    distribution_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/networking/distributions/{distribution_name}"
                    resource_id = distribution_arn
                    reference = self.get_reference(resource_id, link)

                    distribution_vo = Distribution(distribution_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=distribution_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=distribution_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=distribution_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_distributions] [{distribution.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_distributions] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_distribution_tags(self, distribution_arn):
        """Get distribution tags"""
        try:
            return self.connector.get_distribution_tags(distribution_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for distribution {distribution_arn}: {e}"
            )
            return []

    def _get_distribution_cache_behaviors(self, distribution_name):
        """Get distribution cache behaviors"""
        try:
            return self.connector.get_distribution_cache_behaviors(distribution_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get cache behaviors for distribution {distribution_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
