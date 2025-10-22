from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.elb import LoadBalancer


class LoadBalancerManager(ResourceManager):
    cloud_service_group = "ELB"
    cloud_service_type = "LoadBalancer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "ELB"
        self.cloud_service_type = "LoadBalancer"
        self.metadata_path = "metadata/elb/loadbalancer.yaml"

    def create_cloud_service_type(self):
        result = []
        loadbalancer_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonElasticLoadBalancing",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-elb.svg"
            },
            labels=["Networking"],
        )
        result.append(loadbalancer_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_load_balancers(options, region)

    def _collect_load_balancers(self, options, region):
        region_name = region

        try:
            load_balancers, account_id = self.connector.list_elb_load_balancers()

            for load_balancer in load_balancers:
                try:
                    load_balancer_arn = load_balancer.get("LoadBalancerArn")
                    load_balancer_name = load_balancer.get("LoadBalancerName")

                    # Get load balancer attributes
                    attributes = self._get_load_balancer_attributes(load_balancer_arn)

                    # Get load balancer tags
                    tags = self._get_load_balancer_tags(load_balancer_arn)

                    # Get listeners
                    listeners = self._get_load_balancer_listeners(load_balancer_arn)

                    # Get target groups
                    target_groups = self._get_load_balancer_target_groups(
                        load_balancer_arn
                    )

                    load_balancer_data = {
                        "load_balancer_arn": load_balancer_arn,
                        "load_balancer_name": load_balancer_name,
                        "dns_name": load_balancer.get("DNSName", ""),
                        "canonical_hosted_zone_id": load_balancer.get(
                            "CanonicalHostedZoneId", ""
                        ),
                        "created_time": load_balancer.get("CreatedTime"),
                        "load_balancer_type": load_balancer.get("Type", ""),
                        "scheme": load_balancer.get("Scheme", ""),
                        "vpc_id": load_balancer.get("VpcId", ""),
                        "state": load_balancer.get("State", {}),
                        "availability_zones": load_balancer.get(
                            "AvailabilityZones", []
                        ),
                        "security_groups": load_balancer.get("SecurityGroups", []),
                        "ip_address_type": load_balancer.get("IpAddressType", ""),
                        "customer_owned_ipv4_pool": load_balancer.get(
                            "CustomerOwnedIpv4Pool", ""
                        ),
                        "enforce_security_group_inbound_rules_on_private_link_traffic": load_balancer.get(
                            "EnforceSecurityGroupInboundRulesOnPrivateLinkTraffic", ""
                        ),
                        "attributes": attributes,
                        "listeners": listeners,
                        "target_groups": target_groups,
                    }

                    load_balancer_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                load_balancer_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                load_balancer_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#LoadBalancers:search={load_balancer_arn}"
                    resource_id = load_balancer_arn
                    reference = self.get_reference(resource_id, link)

                    load_balancer_vo = LoadBalancer(load_balancer_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=load_balancer_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=load_balancer_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=load_balancer_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_elb_load_balancers] [{load_balancer.get("LoadBalancerName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_elb_load_balancers] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_load_balancer_attributes(self, load_balancer_arn):
        """Get load balancer attributes"""
        try:
            return self.connector.get_load_balancer_attributes(load_balancer_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get attributes for load balancer {load_balancer_arn}: {e}"
            )
            return {}

    def _get_load_balancer_tags(self, load_balancer_arn):
        """Get load balancer tags"""
        try:
            return self.connector.get_load_balancer_tags(load_balancer_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for load balancer {load_balancer_arn}: {e}"
            )
            return []

    def _get_load_balancer_listeners(self, load_balancer_arn):
        """Get load balancer listeners"""
        try:
            return self.connector.get_load_balancer_listeners(load_balancer_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get listeners for load balancer {load_balancer_arn}: {e}"
            )
            return []

    def _get_load_balancer_target_groups(self, load_balancer_arn):
        """Get load balancer target groups"""
        try:
            return self.connector.get_load_balancer_target_groups(load_balancer_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get target groups for load balancer {load_balancer_arn}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
