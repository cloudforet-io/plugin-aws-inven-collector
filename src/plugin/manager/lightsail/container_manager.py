from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Container


class ContainerManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Container"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Container"
        self.metadata_path = "metadata/lightsail/container.yaml"

    def create_cloud_service_type(self):
        result = []
        container_cst_result = make_cloud_service_type(
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
            labels=["Container"],
        )
        result.append(container_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_containers(options, region)

    def _collect_containers(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Lightsail::ContainerService"

        try:
            containers, account_id = self.connector.list_lightsail_containers()

            for container in containers:
                try:
                    container_name = container.get("ContainerServiceName")
                    container_arn = container.get("Arn")

                    # Get container tags
                    tags = self._get_container_tags(container_arn)

                    # Get container deployments
                    deployments = self._get_container_deployments(container_name)

                    container_data = {
                        "container_service_name": container_name,
                        "arn": container_arn,
                        "created_at": container.get("CreatedAt"),
                        "location": container.get("Location", {}),
                        "resource_type": container.get("ResourceType", ""),
                        "tags": container.get("Tags", []),
                        "power": container.get("Power", ""),
                        "power_id": container.get("PowerId", ""),
                        "state": container.get("State", ""),
                        "state_detail": container.get("StateDetail", {}),
                        "scale": container.get("Scale", 0),
                        "current_deployment": container.get("CurrentDeployment", {}),
                        "next_deployment": container.get("NextDeployment", {}),
                        "is_disabled": container.get("IsDisabled", False),
                        "principal_arn": container.get("PrincipalArn", ""),
                        "private_domain_name": container.get("PrivateDomainName", ""),
                        "public_domain_names": container.get("PublicDomainNames", {}),
                        "url": container.get("Url", ""),
                        "deployments": deployments,
                    }

                    container_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/containers/{container_name}"
                    resource_id = container_arn
                    reference = self.get_reference(resource_id, link)

                    container_vo = Container(container_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=container_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=container_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=container_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_containers] [{container.get("ContainerServiceName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_containers] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_container_tags(self, container_arn):
        """Get container tags"""
        try:
            return self.connector.get_container_tags(container_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for container {container_arn}: {e}")
            return []

    def _get_container_deployments(self, container_name):
        """Get container deployments"""
        try:
            return self.connector.get_container_deployments(container_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get deployments for container {container_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
