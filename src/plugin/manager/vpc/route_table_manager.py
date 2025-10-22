from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import RouteTable


class RouteTableManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "RouteTable"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "RouteTable"
        self.metadata_path = "metadata/vpc/route_table.yaml"

    def create_cloud_service_type(self):
        result = []
        route_table_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonVPC",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-vpc.svg"
            },
            labels=["Networking"],
        )
        result.append(route_table_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_route_tables(options, region)

    def _collect_route_tables(self, options, region):
        region_name = region

        try:
            route_tables, account_id = self.connector.list_vpc_route_tables()

            for route_table in route_tables:
                try:
                    route_table_id = route_table.get("RouteTableId")

                    # Get route table tags
                    tags = self._get_route_table_tags(route_table_id)

                    # Get route table routes
                    routes = self._get_route_table_routes(route_table_id)

                    # Get route table associations
                    associations = self._get_route_table_associations(route_table_id)

                    route_table_data = {
                        "route_table_id": route_table_id,
                        "vpc_id": route_table.get("VpcId", ""),
                        "associations": route_table.get("Associations", []),
                        "routes": route_table.get("Routes", []),
                        "propagating_vgws": route_table.get("PropagatingVgws", []),
                        "tags": route_table.get("Tags", []),
                        "owner_id": route_table.get("OwnerId", ""),
                        "route_table_routes": routes,
                        "route_table_associations": associations,
                    }

                    route_table_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                route_table_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                route_table_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#RouteTables:search={route_table_id}"
                    resource_id = route_table_id
                    reference = self.get_reference(resource_id, link)

                    route_table_vo = RouteTable(route_table_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=route_table_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=route_table_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=route_table_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_route_tables] [{route_table.get("RouteTableId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_route_tables] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_route_table_tags(self, route_table_id):
        """Get route table tags"""
        try:
            return self.connector.get_route_table_tags(route_table_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for route table {route_table_id}: {e}")
            return []

    def _get_route_table_routes(self, route_table_id):
        """Get route table routes"""
        try:
            return self.connector.get_route_table_routes(route_table_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get routes for route table {route_table_id}: {e}"
            )
            return []

    def _get_route_table_associations(self, route_table_id):
        """Get route table associations"""
        try:
            return self.connector.get_route_table_associations(route_table_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get associations for route table {route_table_id}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
