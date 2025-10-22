from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.documentdb import ParameterGroup


class ParameterGroupManager(ResourceManager):
    cloud_service_group = "DocumentDB"
    cloud_service_type = "ParameterGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DocumentDB"
        self.cloud_service_type = "ParameterGroup"
        self.metadata_path = "metadata/documentdb/parameter.yaml"

    def create_cloud_service_type(self):
        result = []
        parameter_group_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonDocDB",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-documentdb.svg"
            },
            labels=["Database"],
        )
        result.append(parameter_group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        if region in self.EXCLUDE_REGION.get(self.cloud_service_group, []):
            return {}

        yield from self._collect_parameter_groups(options, region)

    def _collect_parameter_groups(self, options, region):
        res_pgs = self.connector.get_db_cluster_parameter_groups()

        for pg_data in res_pgs.get("DBClusterParameterGroups", []):
            try:
                pg_data.update(
                    {
                        "cloudtrail": self.set_cloudtrail(
                            self.cloud_service_group,
                            pg_data["DBClusterParameterGroupName"],
                            region,
                        ),
                        "parameters": self.request_parameter_data(
                            pg_data["DBClusterParameterGroupName"]
                        ),
                    }
                )

                pg_vo = ParameterGroup(
                    pg_data, strict=False
                )
                parameter_arn = pg_vo.db_cluster_parameter_group_arn
                parameter_name = pg_vo.db_cluster_parameter_group_name
                link = f"https://console.aws.amazon.com/docdb/home?region={region}#parameterGroup-details/{parameter_name}"
                reference = self.get_reference(parameter_arn, link)

                cloud_service = make_cloud_service(
                    name=parameter_name,
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=pg_vo.to_primitive(),
                    account=options.get("account_id"),
                    reference=reference,
                    instance_type=pg_vo.db_parameter_group_family,
                    tags=self.request_tags(parameter_arn),
                    region_code=region,
                )
                yield cloud_service

            except Exception as e:
                yield make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=self.cloud_service_type,
                    region_name=region,
                    resource_type="inventory.CloudService",
                )

    def request_tags(self, resource_arn):
        response = self.connector.list_tags_for_resource(resource_arn)
        return self.convert_tags_to_dict_type(response.get("TagList", []))

    def request_parameter_data(self, pg_name):
        res_params = self.connector.describe_db_cluster_parameters(pg_name)
        return list(
            map(
                lambda param: param,
                res_params.get("Parameters", []),
            )
        )
