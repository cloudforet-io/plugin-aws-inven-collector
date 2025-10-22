from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.msk import Cluster


class ClusterManager(ResourceManager):
    cloud_service_group = "MSK"
    cloud_service_type = "Cluster"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "MSK"
        self.cloud_service_type = "Cluster"
        self.metadata_path = "metadata/msk/cluster.yaml"

    def create_cloud_service_type(self):
        result = []
        cluster_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonMSK",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-msk.svg"
            },
            labels=["Analytics", "Streaming"],
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
            clusters, account_id = self.connector.list_msk_clusters()

            for cluster in clusters:
                try:
                    cluster_arn = cluster.get("ClusterArn")
                    cluster_name = cluster.get("ClusterName")

                    # Get cluster configuration
                    configuration = self._get_cluster_configuration(cluster_arn)

                    # Get cluster tags
                    tags = self._get_cluster_tags(cluster_arn)

                    cluster_data = {
                        "cluster_arn": cluster_arn,
                        "cluster_name": cluster_name,
                        "creation_time": cluster.get("CreationTime"),
                        "current_version": cluster.get("CurrentVersion", ""),
                        "state": cluster.get("State", ""),
                        "state_info": cluster.get("StateInfo", {}),
                        "tags": cluster.get("Tags", {}),
                        "active_operation_arn": cluster.get("ActiveOperationArn", ""),
                        "cluster_type": cluster.get("ClusterType", ""),
                        "cluster_version": cluster.get("ClusterVersion", ""),
                        "broker_node_group_info": cluster.get(
                            "BrokerNodeGroupInfo", {}
                        ),
                        "client_authentication": cluster.get(
                            "ClientAuthentication", {}
                        ),
                        "encryption_info": cluster.get("EncryptionInfo", {}),
                        "enhanced_monitoring": cluster.get("EnhancedMonitoring", ""),
                        "open_monitoring": cluster.get("OpenMonitoring", {}),
                        "logging_info": cluster.get("LoggingInfo", {}),
                        "number_of_broker_nodes": cluster.get("NumberOfBrokerNodes", 0),
                        "zookeeper_connect_string": cluster.get(
                            "ZookeeperConnectString", ""
                        ),
                        "zookeeper_connect_string_tls": cluster.get(
                            "ZookeeperConnectStringTls", ""
                        ),
                        "storage_mode": cluster.get("StorageMode", ""),
                        "customer_action_status": cluster.get(
                            "CustomerActionStatus", ""
                        ),
                        "configuration": configuration,
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

                    link = f"https://{region}.console.aws.amazon.com/msk/home?region={region}#/cluster/{cluster_name}/details"
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
                        f'[list_msk_clusters] [{cluster.get("ClusterName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_msk_clusters] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_cluster_configuration(self, cluster_arn):
        """Get cluster configuration"""
        try:
            return self.connector.get_cluster_configuration(cluster_arn)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get configuration for cluster {cluster_arn}: {e}"
            )
            return {}

    def _get_cluster_tags(self, cluster_arn):
        """Get cluster tags"""
        try:
            return self.connector.get_cluster_tags(cluster_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for cluster {cluster_arn}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
