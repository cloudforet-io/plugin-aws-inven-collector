from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.ecs import Cluster


class ClusterManager(ResourceManager):
    cloud_service_group = "ECS"
    cloud_service_type = "Cluster"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "ECS"
        self.cloud_service_type = "Cluster"
        self.metadata_path = "metadata/ecs/cluster.yaml"

    def create_cloud_service_type(self):
        result = []
        cluster_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonECS",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-ecs.svg"
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
            clusters, account_id = self.connector.list_ecs_clusters()

            for cluster in clusters:
                try:
                    cluster_name = cluster.get("ClusterName")
                    cluster_arn = cluster.get("ClusterArn")

                    # Get cluster tags
                    tags = self._get_cluster_tags(cluster_arn)

                    # Get cluster services
                    services = self._get_cluster_services(cluster_name)

                    # Get cluster tasks
                    tasks = self._get_cluster_tasks(cluster_name)

                    # Get cluster container instances
                    container_instances = self._get_cluster_container_instances(
                        cluster_name
                    )

                    cluster_data = {
                        "cluster_name": cluster_name,
                        "cluster_arn": cluster_arn,
                        "status": cluster.get("Status", ""),
                        "running_tasks_count": cluster.get("RunningTasksCount", 0),
                        "pending_tasks_count": cluster.get("PendingTasksCount", 0),
                        "active_services_count": cluster.get("ActiveServicesCount", 0),
                        "registered_container_instances_count": cluster.get(
                            "RegisteredContainerInstancesCount", 0
                        ),
                        "running_tasks_count": cluster.get("RunningTasksCount", 0),
                        "pending_tasks_count": cluster.get("PendingTasksCount", 0),
                        "active_services_count": cluster.get("ActiveServicesCount", 0),
                        "statistics": cluster.get("Statistics", []),
                        "tags": cluster.get("Tags", []),
                        "settings": cluster.get("Settings", []),
                        "capacity_providers": cluster.get("CapacityProviders", []),
                        "default_capacity_provider_strategy": cluster.get(
                            "DefaultCapacityProviderStrategy", []
                        ),
                        "cluster_service_connect_defaults": cluster.get(
                            "ClusterServiceConnectDefaults", {}
                        ),
                        "attachments": cluster.get("Attachments", []),
                        "attachments_status": cluster.get("AttachmentsStatus", ""),
                        "services": services,
                        "tasks": tasks,
                        "container_instances": container_instances,
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

                    link = f"https://{region}.console.aws.amazon.com/ecs/home?region={region}#/clusters/{cluster_name}"
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
                    _LOGGER.error(
                        f'[list_ecs_clusters] [{cluster.get("ClusterName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_ecs_clusters] [{region_name}] {e}")
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

    def _get_cluster_services(self, cluster_name):
        """Get cluster services"""
        try:
            return self.connector.get_cluster_services(cluster_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get services for cluster {cluster_name}: {e}")
            return []

    def _get_cluster_tasks(self, cluster_name):
        """Get cluster tasks"""
        try:
            return self.connector.get_cluster_tasks(cluster_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tasks for cluster {cluster_name}: {e}")
            return []

    def _get_cluster_container_instances(self, cluster_name):
        """Get cluster container instances"""
        try:
            return self.connector.get_cluster_container_instances(cluster_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get container instances for cluster {cluster_name}: {e}"
            )
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
