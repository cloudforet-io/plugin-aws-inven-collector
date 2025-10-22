from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import PeeringConnection


class PeeringConnectionManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "PeeringConnection"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "PeeringConnection"
        self.metadata_path = "metadata/vpc/peering_connection.yaml"

    def create_cloud_service_type(self):
        result = []
        peering_connection_cst_result = make_cloud_service_type(
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
        result.append(peering_connection_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_peering_connections(options, region)

    def _collect_peering_connections(self, options, region):
        region_name = region

        try:
            peering_connections, account_id = (
                self.connector.list_vpc_peering_connections()
            )

            for peering_connection in peering_connections:
                try:
                    peering_connection_id = peering_connection.get(
                        "VpcPeeringConnectionId"
                    )

                    # Get peering connection tags
                    tags = self._get_peering_connection_tags(peering_connection_id)

                    peering_connection_data = {
                        "vpc_peering_connection_id": peering_connection_id,
                        "status": peering_connection.get("Status", {}),
                        "requester_vpc_info": peering_connection.get(
                            "RequesterVpcInfo", {}
                        ),
                        "accepter_vpc_info": peering_connection.get(
                            "AccepterVpcInfo", {}
                        ),
                        "expiration_time": peering_connection.get("ExpirationTime"),
                        "tags": peering_connection.get("Tags", []),
                    }

                    peering_connection_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                peering_connection_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                peering_connection_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#PeeringConnections:search={peering_connection_id}"
                    resource_id = peering_connection_id
                    reference = self.get_reference(resource_id, link)

                    peering_connection_vo = PeeringConnection(
                        peering_connection_data, strict=False
                    )
                    cloud_service = make_cloud_service(
                        name=peering_connection_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=peering_connection_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=peering_connection_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_peering_connections] [{peering_connection.get("VpcPeeringConnectionId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_peering_connections] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_peering_connection_tags(self, peering_connection_id):
        """Get peering connection tags"""
        try:
            return self.connector.get_peering_connection_tags(peering_connection_id)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get tags for peering connection {peering_connection_id}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
