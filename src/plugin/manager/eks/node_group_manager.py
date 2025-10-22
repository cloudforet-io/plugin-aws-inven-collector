from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.eks import NodeGroup


class NodeGroupManager(ResourceManager):
    cloud_service_group = "EKS"
    cloud_service_type = "NodeGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EKS"
        self.cloud_service_type = "NodeGroup"
        self.metadata_path = "metadata/eks/node_group.yaml"

    def create_cloud_service_type(self):
        result = []
        node_group_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEKS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-eks.svg"
            },
            labels=["Container"],
        )
        result.append(node_group_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_node_groups(options, region)

    def _collect_node_groups(self, options, region):
        region_name = region

        try:
            node_groups, account_id = self.connector.list_eks_node_groups()

            for node_group in node_groups:
                try:
                    node_group_name = node_group.get("NodegroupName")
                    node_group_arn = node_group.get("NodegroupArn")
                    cluster_name = node_group.get("ClusterName")

                    # Get node group tags
                    tags = self._get_node_group_tags(node_group_arn)

                    node_group_data = {
                        "nodegroup_name": node_group_name,
                        "nodegroup_arn": node_group_arn,
                        "cluster_name": cluster_name,
                        "version": node_group.get("Version", ""),
                        "release_version": node_group.get("ReleaseVersion", ""),
                        "created_at": node_group.get("CreatedAt"),
                        "modified_at": node_group.get("ModifiedAt"),
                        "status": node_group.get("Status", ""),
                        "capacity_type": node_group.get("CapacityType", ""),
                        "scaling_config": node_group.get("ScalingConfig", {}),
                        "instance_types": node_group.get("InstanceTypes", []),
                        "subnets": node_group.get("Subnets", []),
                        "remote_access": node_group.get("RemoteAccess", {}),
                        "ami_type": node_group.get("AmiType", ""),
                        "node_role": node_group.get("NodeRole", ""),
                        "labels": node_group.get("Labels", {}),
                        "taints": node_group.get("Taints", []),
                        "resources": node_group.get("Resources", {}),
                        "disk_size": node_group.get("DiskSize", 0),
                        "health": node_group.get("Health", {}),
                        "update_config": node_group.get("UpdateConfig", {}),
                        "launch_template": node_group.get("LaunchTemplate", {}),
                        "tags": node_group.get("Tags", {}),
                    }

                    node_group_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                node_group_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                node_group_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/eks/home?region={region}#/clusters/{cluster_name}/node-groups/{node_group_name}"
                    resource_id = node_group_arn
                    reference = self.get_reference(resource_id, link)

                    node_group_vo = NodeGroup(node_group_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=node_group_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=node_group_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=node_group_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_eks_node_groups] [{node_group.get("NodegroupName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_eks_node_groups] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_node_group_tags(self, node_group_arn):
        """Get node group tags"""
        try:
            return self.connector.get_node_group_tags(node_group_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for node group {node_group_arn}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
