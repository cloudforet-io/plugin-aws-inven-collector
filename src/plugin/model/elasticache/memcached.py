import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Memcached(Model):
    cache_cluster_id = StringType(deserialize_from="CacheClusterId")
    configuration_endpoint = StringType(deserialize_from="ConfigurationEndpoint")
    client_download_landing_page = StringType(
        deserialize_from="ClientDownloadLandingPage"
    )
    cache_node_type = StringType(deserialize_from="CacheNodeType")
    engine = StringType(deserialize_from="Engine")
    engine_version = StringType(deserialize_from="EngineVersion")
    cache_parameter_group = StringType(deserialize_from="CacheParameterGroup")
    cache_subnet_group_name = StringType(deserialize_from="CacheSubnetGroupName")
    cache_cluster_status = StringType(
        deserialize_from="CacheClusterStatus",
        choices=(
            "available",
            "creating",
            "deleting",
            "incompatible-network",
            "modifying",
            "rebooting cluster",
            "restore-failed",
            "snapshotting",
        ),
    )
    num_cache_nodes = IntType(deserialize_from="NumCacheNodes")
    preferred_availability_zone = StringType(
        deserialize_from="PreferredAvailabilityZone"
    )
    preferred_outpost_arn = StringType(deserialize_from="PreferredOutpostArn")
    cache_cluster_create_time = DateTimeType(deserialize_from="CacheClusterCreateTime")
    preferred_maintenance_window = StringType(
        deserialize_from="PreferredMaintenanceWindow"
    )
    pending_modified_values = StringType(deserialize_from="PendingModifiedValues")
    notification_configuration = StringType(
        deserialize_from="NotificationConfiguration"
    )
    cache_security_groups = StringType(deserialize_from="CacheSecurityGroups")
    cache_parameter_group = StringType(deserialize_from="CacheParameterGroup")
    cache_subnet_group_name = StringType(deserialize_from="CacheSubnetGroupName")
    cache_nodes = StringType(deserialize_from="CacheNodes")
    auto_minor_version_upgrade = BooleanType(deserialize_from="AutoMinorVersionUpgrade")
    security_groups = StringType(deserialize_from="SecurityGroups")
    replication_group_id = StringType(deserialize_from="ReplicationGroupId")
    snapshot_retention_limit = IntType(deserialize_from="SnapshotRetentionLimit")
    snapshot_window = StringType(deserialize_from="SnapshotWindow")
    auth_token_enabled = BooleanType(deserialize_from="AuthTokenEnabled")
    auth_token_last_modified_date = DateTimeType(
        deserialize_from="AuthTokenLastModifiedDate"
    )
    log_delivery_configurations = StringType(
        deserialize_from="LogDeliveryConfigurations"
    )
    replication_group_log_delivery_enabled = BooleanType(
        deserialize_from="ReplicationGroupLogDeliveryEnabled"
    )
    network_type = StringType(
        deserialize_from="NetworkType", choices=("ipv4", "ipv6", "dual_stack")
    )
    ip_discovery = StringType(deserialize_from="IpDiscovery", choices=("ipv4", "ipv6"))
    transit_encryption_enabled = BooleanType(
        deserialize_from="TransitEncryptionEnabled"
    )
    transit_encryption_mode = StringType(
        deserialize_from="TransitEncryptionMode", choices=("preferred", "required")
    )
    cluster_mode = StringType(
        deserialize_from="ClusterMode", choices=("enabled", "disabled", "compatible")
    )
