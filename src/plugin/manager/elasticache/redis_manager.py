from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.elasticache import Redis


class RedisManager(ResourceManager):
    cloud_service_group = "ElastiCache"
    cloud_service_type = "Redis"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "ElastiCache"
        self.cloud_service_type = "Redis"
        self.metadata_path = "metadata/elasticache/redis.yaml"

    def create_cloud_service_type(self):
        result = []
        redis_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonElastiCache",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-elasticache.svg"
            },
            labels=["Database"],
        )
        result.append(redis_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_redis_clusters(options, region)

    def _collect_redis_clusters(self, options, region):
        region_name = region

        try:
            redis_clusters, account_id = (
                self.connector.list_elasticache_redis_clusters()
            )

            for cluster in redis_clusters:
                try:
                    cluster_id = cluster.get("CacheClusterId")

                    # Get cluster tags
                    tags = self._get_cluster_tags(cluster_id)

                    # Get cluster parameter group
                    parameter_group = self._get_cluster_parameter_group(
                        cluster.get("CacheParameterGroup", {})
                    )

                    # Get cluster security groups
                    security_groups = self._get_cluster_security_groups(
                        cluster.get("SecurityGroups", [])
                    )

                    cluster_data = {
                        "cache_cluster_id": cluster_id,
                        "cache_node_type": cluster.get("CacheNodeType", ""),
                        "engine": cluster.get("Engine", ""),
                        "engine_version": cluster.get("EngineVersion", ""),
                        "cache_cluster_status": cluster.get("CacheClusterStatus", ""),
                        "num_cache_nodes": cluster.get("NumCacheNodes", 0),
                        "preferred_availability_zone": cluster.get(
                            "PreferredAvailabilityZone", ""
                        ),
                        "preferred_outpost_arn": cluster.get("PreferredOutpostArn", ""),
                        "cache_cluster_create_time": cluster.get(
                            "CacheClusterCreateTime"
                        ),
                        "preferred_maintenance_window": cluster.get(
                            "PreferredMaintenanceWindow", ""
                        ),
                        "notification_configuration": cluster.get(
                            "NotificationConfiguration", {}
                        ),
                        "cache_security_groups": cluster.get("CacheSecurityGroups", []),
                        "cache_subnet_group_name": cluster.get(
                            "CacheSubnetGroupName", ""
                        ),
                        "cache_nodes": cluster.get("CacheNodes", []),
                        "auto_minor_version_upgrade": cluster.get(
                            "AutoMinorVersionUpgrade", False
                        ),
                        "security_groups": cluster.get("SecurityGroups", []),
                        "replication_group_id": cluster.get("ReplicationGroupId", ""),
                        "snapshot_retention_limit": cluster.get(
                            "SnapshotRetentionLimit", 0
                        ),
                        "snapshot_window": cluster.get("SnapshotWindow", ""),
                        "auth_token_enabled": cluster.get("AuthTokenEnabled", False),
                        "auth_token_last_modified_date": cluster.get(
                            "AuthTokenLastModifiedDate"
                        ),
                        "transit_encryption_enabled": cluster.get(
                            "TransitEncryptionEnabled", False
                        ),
                        "at_rest_encryption_enabled": cluster.get(
                            "AtRestEncryptionEnabled", False
                        ),
                        "arn": cluster.get("ARN", ""),
                        "replication_group_log_delivery_enabled": cluster.get(
                            "ReplicationGroupLogDeliveryEnabled", False
                        ),
                        "log_delivery_configurations": cluster.get(
                            "LogDeliveryConfigurations", []
                        ),
                        "network_type": cluster.get("NetworkType", ""),
                        "ip_discovery": cluster.get("IpDiscovery", ""),
                        "transit_encryption_mode": cluster.get(
                            "TransitEncryptionMode", ""
                        ),
                        "parameter_group": parameter_group,
                        "security_groups": security_groups,
                    }

                    cluster_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                cluster_id,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                cluster_id,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/elasticache/home?region={region}#redis:"
                    resource_id = cluster_id
                    reference = self.get_reference(resource_id, link)

                    redis_vo = Redis(cluster_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=cluster_id,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=redis_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=cluster_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_elasticache_redis_clusters] [{cluster.get("CacheClusterId")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_elasticache_redis_clusters] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_cluster_tags(self, cluster_id):
        """Get cluster tags"""
        try:
            return self.connector.get_cluster_tags(cluster_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for cluster {cluster_id}: {e}")
            return []

    def _get_cluster_parameter_group(self, parameter_group):
        """Get cluster parameter group details"""
        if not parameter_group:
            return {}

        try:
            return self.connector.get_cluster_parameter_group(parameter_group)
        except Exception as e:
            _LOGGER.warning(f"Failed to get parameter group: {e}")
            return {}

    def _get_cluster_security_groups(self, security_groups):
        """Get cluster security groups details"""
        if not security_groups:
            return []

        try:
            return self.connector.get_cluster_security_groups(security_groups)
        except Exception as e:
            _LOGGER.warning(f"Failed to get security groups: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
