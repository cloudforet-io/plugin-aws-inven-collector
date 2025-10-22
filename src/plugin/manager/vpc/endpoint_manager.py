from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.vpc import Endpoint


class EndpointManager(ResourceManager):
    cloud_service_group = "VPC"
    cloud_service_type = "Endpoint"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "VPC"
        self.cloud_service_type = "Endpoint"
        self.metadata_path = "metadata/vpc/endpoint.yaml"

    def create_cloud_service_type(self):
        result = []
        endpoint_cst_result = make_cloud_service_type(
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
        result.append(endpoint_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_endpoints(options, region)

    def _collect_endpoints(self, options, region):
        region_name = region

        try:
            endpoints, account_id = self.connector.list_vpc_endpoints()

            for endpoint in endpoints:
                try:
                    endpoint_id = endpoint.get("VpcEndpointId")

                    # Get endpoint tags
                    tags = self._get_endpoint_tags(endpoint_id)

                    # Get endpoint policy
                    policy = self._get_endpoint_policy(endpoint_id)

                    endpoint_data = {
                        "vpc_endpoint_id": endpoint_id,
                        "vpc_endpoint_type": endpoint.get("VpcEndpointType", ""),
                        "vpc_id": endpoint.get("VpcId", ""),
                        "service_name": endpoint.get("ServiceName", ""),
                        "state": endpoint.get("State", ""),
                        "policy_document": endpoint.get("PolicyDocument", ""),
                        "route_table_ids": endpoint.get("RouteTableIds", []),
                        "subnet_ids": endpoint.get("SubnetIds", []),
                        "groups": endpoint.get("Groups", []),
                        "ip_address_type": endpoint.get("IpAddressType", ""),
                        "dns_entries": endpoint.get("DnsEntries", []),
                        "network_interface_ids": endpoint.get(
                            "NetworkInterfaceIds", []
                        ),
                        "dns_options": endpoint.get("DnsOptions", {}),
                        "private_dns_enabled": endpoint.get("PrivateDnsEnabled", False),
                        "requester_managed": endpoint.get("RequesterManaged", False),
                        "tags": endpoint.get("Tags", []),
                        "creation_timestamp": endpoint.get("CreationTimestamp"),
                        "owner_id": endpoint.get("OwnerId", ""),
                        "last_error": endpoint.get("LastError", {}),
                        "policy": policy,
                    }

                    endpoint_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                endpoint_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                endpoint_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/vpc/home?region={region}#Endpoints:search={endpoint_id}"
                    resource_id = endpoint_id
                    reference = self.get_reference(resource_id, link)

                    endpoint_vo = Endpoint(endpoint_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=endpoint_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=endpoint_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=endpoint_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_vpc_endpoints] [{endpoint.get("VpcEndpointId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_vpc_endpoints] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_endpoint_tags(self, endpoint_id):
        """Get endpoint tags"""
        try:
            return self.connector.get_endpoint_tags(endpoint_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for endpoint {endpoint_id}: {e}")
            return []

    def _get_endpoint_policy(self, endpoint_id):
        """Get endpoint policy"""
        try:
            return self.connector.get_endpoint_policy(endpoint_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get policy for endpoint {endpoint_id}: {e}")
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
