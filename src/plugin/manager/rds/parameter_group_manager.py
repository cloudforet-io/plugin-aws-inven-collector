from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.rds import ParameterGroup


class ParameterGroupManager(ResourceManager):
    cloud_service_group = "RDS"
    cloud_service_type = "ParameterGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "ParameterGroup"
        self.metadata_path = "metadata/rds/parameter_group.yaml"

    def create_cloud_service_type(self):
        result = []
        parameter_group_cst_result = make_cloud_service_type(
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
        result.append(parameter_group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_parameter_groups(options, region)

    def _collect_parameter_groups(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::RDS::DBParameterGroup"

        try:
            parameter_groups, account_id = self.connector.list_rds_parameter_groups()

            for parameter_group in parameter_groups:
                try:
                    parameter_group_name = parameter_group.get("DBParameterGroupName")

                    # Get parameter group tags
                    tags = self._get_parameter_group_tags(parameter_group_name)

                    # Get parameter group parameters
                    parameters = self._get_parameter_group_parameters(
                        parameter_group_name
                    )

                    parameter_group_data = {
                        "db_parameter_group_name": parameter_group_name,
                        "db_parameter_group_family": parameter_group.get(
                            "DBParameterGroupFamily", ""
                        ),
                        "description": parameter_group.get("Description", ""),
                        "db_parameter_group_arn": parameter_group.get(
                            "DBParameterGroupArn"
                        ),
                        "parameters": parameters,
                    }

                    parameter_group_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/rds/home?region={region}#parameter-groups:parameter-group-family={parameter_group.get('DBParameterGroupFamily', '')}"
                    resource_id = parameter_group_name
                    reference = self.get_reference(resource_id, link)

                    parameter_group_vo = ParameterGroup(
                        parameter_group_data, strict=False
                    )
                    cloud_service = make_cloud_service(
                        name=parameter_group_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=parameter_group_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=parameter_group_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_rds_parameter_groups] [{parameter_group.get("DBParameterGroupName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_rds_parameter_groups] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_parameter_group_tags(self, parameter_group_name):
        """Get parameter group tags"""
        try:
            return self.connector.get_parameter_group_tags(parameter_group_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for parameter group {parameter_group_name}: {e}"
            )
            return []

    def _get_parameter_group_parameters(self, parameter_group_name):
        """Get parameter group parameters"""
        try:
            return self.connector.get_parameter_group_parameters(parameter_group_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get parameters for parameter group {parameter_group_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
