from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import LoadBalancer


class LoadBalancerManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "LoadBalancer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "LoadBalancer"
        self.metadata_path = "metadata/lightsail/loadbalancer.yaml"

    def create_cloud_service_type(self):
        result = []
        loadbalancer_cst_result = make_cloud_service_type(
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
        result.append(loadbalancer_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_loadbalancers(options, region)

    def _collect_loadbalancers(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Lightsail::LoadBalancer"

        try:
            loadbalancers, account_id = self.connector.list_lightsail_loadbalancers()

            for loadbalancer in loadbalancers:
                try:
                    loadbalancer_name = loadbalancer.get("Name")
                    loadbalancer_arn = loadbalancer.get("Arn")

                    # Get load balancer tags
                    tags = self._get_loadbalancer_tags(loadbalancer_arn)

                    # Get load balancer target health
                    target_health = self._get_loadbalancer_target_health(
                        loadbalancer_name
                    )

                    loadbalancer_data = {
                        "name": loadbalancer_name,
                        "arn": loadbalancer_arn,
                        "created_at": loadbalancer.get("CreatedAt"),
                        "location": loadbalancer.get("Location", {}),
                        "resource_type": loadbalancer.get("ResourceType", ""),
                        "tags": loadbalancer.get("Tags", []),
                        "support_code": loadbalancer.get("SupportCode", ""),
                        "dns_name": loadbalancer.get("DnsName", ""),
                        "state": loadbalancer.get("State", ""),
                        "protocol": loadbalancer.get("Protocol", ""),
                        "public_ports": loadbalancer.get("PublicPorts", []),
                        "health_check_path": loadbalancer.get("HealthCheckPath", ""),
                        "instance_port": loadbalancer.get("InstancePort", 0),
                        "instance_health_summary": loadbalancer.get(
                            "InstanceHealthSummary", []
                        ),
                        "tls_certificate_summaries": loadbalancer.get(
                            "TlsCertificateSummaries", []
                        ),
                        "configuration_options": loadbalancer.get(
                            "ConfigurationOptions", {}
                        ),
                        "ip_address_type": loadbalancer.get("IpAddressType", ""),
                        "https_redirection_enabled": loadbalancer.get(
                            "HttpsRedirectionEnabled", False
                        ),
                        "target_health": target_health,
                    }

                    loadbalancer_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/networking/load-balancers/{loadbalancer_name}"
                    resource_id = loadbalancer_arn
                    reference = self.get_reference(resource_id, link)

                    loadbalancer_vo = LoadBalancer(loadbalancer_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=loadbalancer_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=loadbalancer_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=loadbalancer_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_loadbalancers] [{loadbalancer.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_loadbalancers] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_loadbalancer_tags(self, loadbalancer_arn):
        """Get load balancer tags"""
        try:
            return self.connector.get_loadbalancer_tags(loadbalancer_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for load balancer {loadbalancer_arn}: {e}"
            )
            return []

    def _get_loadbalancer_target_health(self, loadbalancer_name):
        """Get load balancer target health"""
        try:
            return self.connector.get_loadbalancer_target_health(loadbalancer_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get target health for load balancer {loadbalancer_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
