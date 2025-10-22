from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Domain


class DomainManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Domain"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Domain"
        self.metadata_path = "metadata/lightsail/domain.yaml"

    def create_cloud_service_type(self):
        result = []
        domain_cst_result = make_cloud_service_type(
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
        result.append(domain_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_domains(options, region)

    def _collect_domains(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Lightsail::Domain"

        try:
            domains, account_id = self.connector.list_lightsail_domains()

            for domain in domains:
                try:
                    domain_name = domain.get("Name")
                    domain_arn = domain.get("Arn")

                    # Get domain tags
                    tags = self._get_domain_tags(domain_arn)

                    # Get domain records
                    records = self._get_domain_records(domain_name)

                    domain_data = {
                        "name": domain_name,
                        "arn": domain_arn,
                        "created_at": domain.get("CreatedAt"),
                        "location": domain.get("Location", {}),
                        "resource_type": domain.get("ResourceType", ""),
                        "tags": domain.get("Tags", []),
                        "domain_entries": domain.get("DomainEntries", []),
                        "support_code": domain.get("SupportCode", ""),
                        "records": records,
                    }

                    domain_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/networking/domains/{domain_name}"
                    resource_id = domain_arn
                    reference = self.get_reference(resource_id, link)

                    domain_vo = Domain(domain_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=domain_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=domain_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=domain_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_domains] [{domain.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_domains] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_domain_tags(self, domain_arn):
        """Get domain tags"""
        try:
            return self.connector.get_domain_tags(domain_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for domain {domain_arn}: {e}")
            return []

    def _get_domain_records(self, domain_name):
        """Get domain records"""
        try:
            return self.connector.get_domain_records(domain_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get records for domain {domain_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
