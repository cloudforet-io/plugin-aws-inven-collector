from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.elb import TargetGroup


class TargetGroupManager(ResourceManager):
    cloud_service_group = "ELB"
    cloud_service_type = "TargetGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "ELB"
        self.cloud_service_type = "TargetGroup"
        self.metadata_path = "metadata/elb/target_group.yaml"

    def create_cloud_service_type(self):
        result = []
        target_group_cst_result = make_cloud_service_type(
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
        result.append(target_group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_target_groups(options, region)

    def _collect_target_groups(self, options, region):
        region_name = region

        try:
            target_groups, account_id = self.connector.list_elb_target_groups()

            for target_group in target_groups:
                try:
                    target_group_arn = target_group.get("TargetGroupArn")
                    target_group_name = target_group.get("TargetGroupName")

                    # Get target group attributes
                    attributes = self._get_target_group_attributes(target_group_arn)

                    # Get target group tags
                    tags = self._get_target_group_tags(target_group_arn)

                    # Get target health
                    target_health = self._get_target_health(target_group_arn)

                    target_group_data = {
                        "target_group_arn": target_group_arn,
                        "target_group_name": target_group_name,
                        "protocol": target_group.get("Protocol", ""),
                        "port": target_group.get("Port", 0),
                        "vpc_id": target_group.get("VpcId", ""),
                        "health_check_protocol": target_group.get(
                            "HealthCheckProtocol", ""
                        ),
                        "health_check_port": target_group.get("HealthCheckPort", ""),
                        "health_check_enabled": target_group.get(
                            "HealthCheckEnabled", False
                        ),
                        "health_check_interval_seconds": target_group.get(
                            "HealthCheckIntervalSeconds", 0
                        ),
                        "health_check_timeout_seconds": target_group.get(
                            "HealthCheckTimeoutSeconds", 0
                        ),
                        "healthy_threshold_count": target_group.get(
                            "HealthyThresholdCount", 0
                        ),
                        "unhealthy_threshold_count": target_group.get(
                            "UnhealthyThresholdCount", 0
                        ),
                        "health_check_path": target_group.get("HealthCheckPath", ""),
                        "matcher": target_group.get("Matcher", {}),
                        "load_balancer_arns": target_group.get("LoadBalancerArns", []),
                        "target_type": target_group.get("TargetType", ""),
                        "protocol_version": target_group.get("ProtocolVersion", ""),
                        "ip_address_type": target_group.get("IpAddressType", ""),
                        "attributes": attributes,
                        "target_health": target_health,
                    }

                    target_group_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                target_group_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                target_group_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#TargetGroups:search={target_group_arn}"
                    resource_id = target_group_arn
                    reference = self.get_reference(resource_id, link)

                    target_group_vo = TargetGroup(target_group_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=target_group_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=target_group_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=target_group_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_elb_target_groups] [{target_group.get("TargetGroupName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_elb_target_groups] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_target_group_attributes(self, target_group_arn):
        """Get target group attributes"""
        try:
            return self.connector.get_target_group_attributes(target_group_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get attributes for target group {target_group_arn}: {e}"
            )
            return {}

    def _get_target_group_tags(self, target_group_arn):
        """Get target group tags"""
        try:
            return self.connector.get_target_group_tags(target_group_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for target group {target_group_arn}: {e}"
            )
            return []

    def _get_target_health(self, target_group_arn):
        """Get target health"""
        try:
            return self.connector.get_target_health(target_group_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get target health for target group {target_group_arn}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
