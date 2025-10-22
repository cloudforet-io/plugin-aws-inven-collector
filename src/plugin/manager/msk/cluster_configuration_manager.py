from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.msk import ClusterConfiguration


class ClusterConfigurationManager(ResourceManager):
    cloud_service_group = "MSK"
    cloud_service_type = "ClusterConfiguration"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "MSK"
        self.cloud_service_type = "ClusterConfiguration"
        self.metadata_path = "metadata/msk/cluster_configuration.yaml"

    def create_cloud_service_type(self):
        result = []
        configuration_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonMSK",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-msk.svg"
            },
            labels=["Analytics", "Streaming"],
        )
        result.append(configuration_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_cluster_configurations(options, region)

    def _collect_cluster_configurations(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::MSK::Configuration"

        try:
            configurations, account_id = self.connector.list_msk_configurations()

            for configuration in configurations:
                try:
                    configuration_arn = configuration.get("Arn")
                    configuration_name = configuration.get("Name")

                    # Get configuration tags
                    tags = self._get_configuration_tags(configuration_arn)

                    configuration_data = {
                        "arn": configuration_arn,
                        "name": configuration_name,
                        "description": configuration.get("Description", ""),
                        "kafka_versions": configuration.get("KafkaVersions", []),
                        "creation_time": configuration.get("CreationTime"),
                        "latest_revision": configuration.get("LatestRevision", {}),
                        "state": configuration.get("State", ""),
                    }

                    configuration_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/msk/home?region={region}#/configuration/{configuration_name}"
                    resource_id = configuration_arn
                    reference = self.get_reference(resource_id, link)

                    configuration_vo = ClusterConfiguration(
                        configuration_data, strict=False
                    )
                    cloud_service = make_cloud_service(
                        name=configuration_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=configuration_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=configuration_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_msk_configurations] [{configuration.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_msk_configurations] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_configuration_tags(self, configuration_arn):
        """Get configuration tags"""
        try:
            return self.connector.get_configuration_tags(configuration_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for configuration {configuration_arn}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
