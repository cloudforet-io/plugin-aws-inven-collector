from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import StaticIP


class StaticIPManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "StaticIP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "StaticIP"
        self.metadata_path = "metadata/lightsail/static_ip.yaml"

    def create_cloud_service_type(self):
        result = []
        static_ip_cst_result = make_cloud_service_type(
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
        result.append(static_ip_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_static_ips(options, region)

    def _collect_static_ips(self, options, region):
        region_name = region

        try:
            static_ips, account_id = self.connector.list_lightsail_static_ips()

            for static_ip in static_ips:
                try:
                    static_ip_name = static_ip.get("Name")
                    static_ip_arn = static_ip.get("Arn")

                    # Get static IP tags
                    tags = self._get_static_ip_tags(static_ip_arn)

                    static_ip_data = {
                        "name": static_ip_name,
                        "arn": static_ip_arn,
                        "created_at": static_ip.get("CreatedAt"),
                        "location": static_ip.get("Location", {}),
                        "resource_type": static_ip.get("ResourceType", ""),
                        "tags": static_ip.get("Tags", []),
                        "support_code": static_ip.get("SupportCode", ""),
                        "ip_address": static_ip.get("IpAddress", ""),
                        "attached_to": static_ip.get("AttachedTo", ""),
                        "is_attached": static_ip.get("IsAttached", False),
                        "attachment_state": static_ip.get("AttachmentState", ""),
                    }

                    static_ip_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                static_ip_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                static_ip_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/networking/static-ips/{static_ip_name}"
                    resource_id = static_ip_arn
                    reference = self.get_reference(resource_id, link)

                    static_ip_vo = StaticIP(static_ip_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=static_ip_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=static_ip_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=static_ip_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_static_ips] [{static_ip.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_static_ips] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_static_ip_tags(self, static_ip_arn):
        """Get static IP tags"""
        try:
            return self.connector.get_static_ip_tags(static_ip_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for static IP {static_ip_arn}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
