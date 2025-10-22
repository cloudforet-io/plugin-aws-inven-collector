from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.rds import OptionGroup


class OptionGroupManager(ResourceManager):
    cloud_service_group = "RDS"
    cloud_service_type = "OptionGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "OptionGroup"
        self.metadata_path = "metadata/rds/option_group.yaml"

    def create_cloud_service_type(self):
        result = []
        option_group_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonRDS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-rds.svg"
            },
            labels=["Database"],
        )
        result.append(option_group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_option_groups(options, region)

    def _collect_option_groups(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::RDS::DBOptionGroup"

        try:
            option_groups, account_id = self.connector.list_rds_option_groups()

            for option_group in option_groups:
                try:
                    option_group_name = option_group.get("OptionGroupName")

                    # Get option group tags
                    tags = self._get_option_group_tags(option_group_name)

                    # Get option group options
                    options = self._get_option_group_options(option_group_name)

                    option_group_data = {
                        "option_group_name": option_group_name,
                        "option_group_description": option_group.get(
                            "OptionGroupDescription", ""
                        ),
                        "engine_name": option_group.get("EngineName", ""),
                        "major_engine_version": option_group.get(
                            "MajorEngineVersion", ""
                        ),
                        "option_group_arn": option_group.get("OptionGroupArn"),
                        "allows_vpc_and_non_vpc_instance_memberships": option_group.get(
                            "AllowsVpcAndNonVpcInstanceMemberships", False
                        ),
                        "vpc_id": option_group.get("VpcId", ""),
                        "options": options,
                    }

                    option_group_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/rds/home?region={region}#option-groups:option-group-name={option_group_name}"
                    resource_id = option_group_name
                    reference = self.get_reference(resource_id, link)

                    option_group_vo = OptionGroup(option_group_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=option_group_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=option_group_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=option_group_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_rds_option_groups] [{option_group.get("OptionGroupName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_rds_option_groups] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_option_group_tags(self, option_group_name):
        """Get option group tags"""
        try:
            return self.connector.get_option_group_tags(option_group_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for option group {option_group_name}: {e}"
            )
            return []

    def _get_option_group_options(self, option_group_name):
        """Get option group options"""
        try:
            return self.connector.get_option_group_options(option_group_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get options for option group {option_group_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
