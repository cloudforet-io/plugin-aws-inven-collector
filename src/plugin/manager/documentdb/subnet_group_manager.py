from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.documentdb import SubnetGroup


class SubnetGroupManager(ResourceManager):
    cloud_service_group = "DocumentDB"
    cloud_service_type = "SubnetGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DocumentDB"
        self.cloud_service_type = "SubnetGroup"
        self.metadata_path = "metadata/documentdb/subnet.yaml"

    def create_cloud_service_type(self):
        result = []
        subnet_group_cst_result = make_cloud_service_type(
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
        result.append(subnet_group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        if region in self.EXCLUDE_REGION.get(self.cloud_service_group, []):
            return {}

        yield from self._collect_subnet_groups(options, region)

    def _collect_subnet_groups(self, options, region):
        response = self.connector.get_db_subnet_groups()
        for data in response:
            for raw in data.get("DBSubnetGroups", []):
                try:
                    raw.update(
                        {
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                raw["DBSubnetGroupName"],
                                region,
                            )
                        }
                    )

                    subnet_group_vo = SubnetGroup(raw, strict=False)

                    subnet_arn = subnet_group_vo.db_subnet_group_arn
                    subnet_name = subnet_group_vo.db_subnet_group_name
                    link = f"https://console.aws.amazon.com/docdb/home?region={region}#subnetGroup-details/{subnet_name}"
                    reference = self.get_reference(subnet_arn, link)

                    cloud_service = make_cloud_service(
                        name=subnet_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=subnet_group_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=self.request_tags(
                            subnet_group_vo.get("DBSubnetGroupArn", "")
                        ),
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
