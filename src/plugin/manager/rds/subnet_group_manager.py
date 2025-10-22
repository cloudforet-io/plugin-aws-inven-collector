from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.rds import SubnetGroup


class SubnetGroupManager(ResourceManager):
    cloud_service_group = "RDS"
    cloud_service_type = "SubnetGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "RDS"
        self.cloud_service_type = "SubnetGroup"
        self.metadata_path = "metadata/rds/subnet_group.yaml"

    def create_cloud_service_type(self):
        result = []
        subnet_group_cst_result = make_cloud_service_type(
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
        result.append(subnet_group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_subnet_groups(options, region)

    def _collect_subnet_groups(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::RDS::DBSubnetGroup"

        try:
            subnet_groups, account_id = self.connector.list_rds_subnet_groups()

            for subnet_group in subnet_groups:
                try:
                    subnet_group_name = subnet_group.get("DBSubnetGroupName")

                    # Get subnet group tags
                    tags = self._get_subnet_group_tags(subnet_group_name)

                    subnet_group_data = {
                        "db_subnet_group_name": subnet_group_name,
                        "db_subnet_group_description": subnet_group.get(
                            "DBSubnetGroupDescription", ""
                        ),
                        "vpc_id": subnet_group.get("VpcId", ""),
                        "subnet_group_status": subnet_group.get(
                            "SubnetGroupStatus", ""
                        ),
                        "subnets": subnet_group.get("Subnets", []),
                        "db_subnet_group_arn": subnet_group.get("DBSubnetGroupArn"),
                        "supported_network_types": subnet_group.get(
                            "SupportedNetworkTypes", []
                        ),
                    }

                    subnet_group_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/rds/home?region={region}#subnet-groups:db-subnet-group-name={subnet_group_name}"
                    resource_id = subnet_group_name
                    reference = self.get_reference(resource_id, link)

                    subnet_group_vo = SubnetGroup(subnet_group_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=subnet_group_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=subnet_group_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=subnet_group_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_rds_subnet_groups] [{subnet_group.get("DBSubnetGroupName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_rds_subnet_groups] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_subnet_group_tags(self, subnet_group_name):
        """Get subnet group tags"""
        try:
            return self.connector.get_subnet_group_tags(subnet_group_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for subnet group {subnet_group_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
