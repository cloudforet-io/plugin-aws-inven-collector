from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.route53 import HostedZone


class HostedZoneManager(ResourceManager):
    cloud_service_group = "Route53"
    cloud_service_type = "HostedZone"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Route53"
        self.cloud_service_type = "HostedZone"
        self.metadata_path = "metadata/route53/hosted_zone.yaml"

    def create_cloud_service_type(self):
        result = []
        hosted_zone_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonRoute53",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-route53.svg"
            },
            labels=["Networking"],
        )
        result.append(hosted_zone_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_hosted_zones(options, region)

    def _collect_hosted_zones(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Route53::HostedZone"

        try:
            hosted_zones, account_id = self.connector.list_route53_hosted_zones()

            for hosted_zone in hosted_zones:
                try:
                    hosted_zone_id = hosted_zone.get("Id")
                    hosted_zone_name = hosted_zone.get("Name")

                    # Get hosted zone tags
                    tags = self._get_hosted_zone_tags(hosted_zone_id)

                    # Get record sets
                    record_sets = self._get_hosted_zone_record_sets(hosted_zone_id)

                    # Get hosted zone details
                    hosted_zone_details = self._get_hosted_zone_details(hosted_zone_id)

                    hosted_zone_data = {
                        "id": hosted_zone_id,
                        "name": hosted_zone_name,
                        "caller_reference": hosted_zone.get("CallerReference", ""),
                        "config": hosted_zone.get("Config", {}),
                        "resource_record_set_count": hosted_zone.get(
                            "ResourceRecordSetCount", 0
                        ),
                        "linked_service": hosted_zone.get("LinkedService", {}),
                        "tags": hosted_zone.get("Tags", []),
                        "record_sets": record_sets,
                        "hosted_zone_details": hosted_zone_details,
                    }

                    hosted_zone_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://console.aws.amazon.com/route53/v2/hostedzones#{hosted_zone_id}"
                    resource_id = hosted_zone_id
                    reference = self.get_reference(resource_id, link)

                    hosted_zone_vo = HostedZone(hosted_zone_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=hosted_zone_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=hosted_zone_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=hosted_zone_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_route53_hosted_zones] [{hosted_zone.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_route53_hosted_zones] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_hosted_zone_tags(self, hosted_zone_id):
        """Get hosted zone tags"""
        try:
            return self.connector.get_hosted_zone_tags(hosted_zone_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for hosted zone {hosted_zone_id}: {e}")
            return []

    def _get_hosted_zone_record_sets(self, hosted_zone_id):
        """Get hosted zone record sets"""
        try:
            return self.connector.get_hosted_zone_record_sets(hosted_zone_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get record sets for hosted zone {hosted_zone_id}: {e}"
            )
            return []

    def _get_hosted_zone_details(self, hosted_zone_id):
        """Get hosted zone details"""
        try:
            return self.connector.get_hosted_zone_details(hosted_zone_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get details for hosted zone {hosted_zone_id}: {e}"
            )
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
