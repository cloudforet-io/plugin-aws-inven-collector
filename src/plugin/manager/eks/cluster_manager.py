from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.eks import Cluster


class ClusterManager(ResourceManager):
    cloud_service_group = "EKS"
    cloud_service_type = "Cluster"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EKS"
        self.cloud_service_type = "Cluster"
        self.metadata_path = "metadata/eks/cluster.yaml"

    def create_cloud_service_type(self):
        result = []
        cluster_cst_result = make_cloud_service_type(
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
        result.append(cluster_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_clusters(options, region)

    def _collect_clusters(self, options, region):
        region_name = region

        try:
            clusters, account_id = self.connector.list_eks_clusters()

            for cluster in clusters:
                try:
                    cluster_name = cluster.get("Name")
                    cluster_arn = cluster.get("Arn")

                    # Get cluster tags
                    tags = self._get_cluster_tags(cluster_arn)

                    # Get cluster node groups
                    node_groups = self._get_cluster_node_groups(cluster_name)

                    # Get cluster addons
                    addons = self._get_cluster_addons(cluster_name)

                    cluster_data = {
                        "name": cluster_name,
                        "arn": cluster_arn,
                        "created_at": cluster.get("CreatedAt"),
                        "version": cluster.get("Version", ""),
                        "endpoint": cluster.get("Endpoint", ""),
                        "role_arn": cluster.get("RoleArn", ""),
                        "resources_vpc_config": cluster.get("ResourcesVpcConfig", {}),
                        "kubernetes_network_config": cluster.get(
                            "KubernetesNetworkConfig", {}
                        ),
                        "logging": cluster.get("Logging", {}),
                        "identity": cluster.get("Identity", {}),
                        "status": cluster.get("Status", ""),
                        "certificate_authority": cluster.get(
                            "CertificateAuthority", {}
                        ),
                        "client_request_token": cluster.get("ClientRequestToken", ""),
                        "platform_version": cluster.get("PlatformVersion", ""),
                        "tags": cluster.get("Tags", {}),
                        "encryption_config": cluster.get("EncryptionConfig", []),
                        "connector_config": cluster.get("ConnectorConfig", {}),
                        "outpost_config": cluster.get("OutpostConfig", {}),
                        "access_config": cluster.get("AccessConfig", {}),
                        "node_groups": node_groups,
                        "addons": addons,
                    }

                    cluster_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                cluster_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                cluster_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/eks/home?region={region}#/clusters/{cluster_name}"
                    resource_id = cluster_arn
                    reference = self.get_reference(resource_id, link)

                    cluster_vo = Cluster(cluster_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=cluster_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=cluster_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=cluster_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_eks_clusters] [{cluster.get("Name")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_eks_clusters] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_cluster_tags(self, cluster_arn):
        """Get cluster tags"""
        try:
            return self.connector.get_cluster_tags(cluster_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for cluster {cluster_arn}: {e}")
            return []

    def _get_cluster_node_groups(self, cluster_name):
        """Get cluster node groups"""
        try:
            return self.connector.get_cluster_node_groups(cluster_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get node groups for cluster {cluster_name}: {e}"
            )
            return []

    def _get_cluster_addons(self, cluster_name):
        """Get cluster addons"""
        try:
            return self.connector.get_cluster_addons(cluster_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get addons for cluster {cluster_name}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
