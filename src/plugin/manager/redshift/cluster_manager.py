from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.redshift import Cluster


class ClusterManager(ResourceManager):
    cloud_service_group = "Redshift"
    cloud_service_type = "Cluster"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Redshift"
        self.cloud_service_type = "Cluster"
        self.metadata_path = "metadata/redshift/cluster.yaml"

    def create_cloud_service_type(self):
        result = []
        cluster_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonRedshift",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-redshift.svg"
            },
            labels=["Database", "Analytics"],
        )
        result.append(cluster_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_clusters(options, region)

    def _collect_clusters(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Redshift::Cluster"

        try:
            clusters, account_id = self.connector.list_redshift_clusters()

            for cluster in clusters:
                try:
                    cluster_id = cluster.get("ClusterIdentifier")

                    # Get cluster snapshots
                    snapshots = self._get_cluster_snapshots(cluster_id)

                    # Get cluster parameter groups
                    parameter_groups = self._get_cluster_parameter_groups(
                        cluster.get("ClusterParameterGroups", [])
                    )

                    # Get cluster security groups
                    security_groups = self._get_cluster_security_groups(
                        cluster.get("ClusterSecurityGroups", [])
                    )

                    # Get cluster subnet groups
                    subnet_groups = self._get_cluster_subnet_groups(
                        cluster.get("ClusterSubnetGroupName")
                    )

                    cluster_data = {
                        "cluster_identifier": cluster_id,
                        "cluster_namespace_arn": cluster.get("ClusterNamespaceArn"),
                        "node_type": cluster.get("NodeType", ""),
                        "cluster_status": cluster.get("ClusterStatus", ""),
                        "cluster_availability_status": cluster.get(
                            "ClusterAvailabilityStatus", ""
                        ),
                        "master_username": cluster.get("MasterUsername", ""),
                        "db_name": cluster.get("DBName", ""),
                        "endpoint": cluster.get("Endpoint", {}),
                        "cluster_create_time": cluster.get("ClusterCreateTime"),
                        "automated_snapshot_retention_period": cluster.get(
                            "AutomatedSnapshotRetentionPeriod", 0
                        ),
                        "manual_snapshot_retention_period": cluster.get(
                            "ManualSnapshotRetentionPeriod", 0
                        ),
                        "cluster_security_groups": cluster.get(
                            "ClusterSecurityGroups", []
                        ),
                        "vpc_security_groups": cluster.get("VpcSecurityGroups", []),
                        "cluster_parameter_groups": cluster.get(
                            "ClusterParameterGroups", []
                        ),
                        "cluster_subnet_group_name": cluster.get(
                            "ClusterSubnetGroupName", ""
                        ),
                        "vpc_id": cluster.get("VpcId", ""),
                        "availability_zone": cluster.get("AvailabilityZone", ""),
                        "preferred_maintenance_window": cluster.get(
                            "PreferredMaintenanceWindow", ""
                        ),
                        "pending_modified_values": cluster.get(
                            "PendingModifiedValues", {}
                        ),
                        "cluster_version": cluster.get("ClusterVersion", ""),
                        "allow_version_upgrade": cluster.get(
                            "AllowVersionUpgrade", False
                        ),
                        "number_of_nodes": cluster.get("NumberOfNodes", 0),
                        "publicly_accessible": cluster.get("PubliclyAccessible", False),
                        "encrypted": cluster.get("Encrypted", False),
                        "restore_status": cluster.get("RestoreStatus", {}),
                        "data_transfer_progress": cluster.get(
                            "DataTransferProgress", {}
                        ),
                        "hsm_status": cluster.get("HsmStatus", {}),
                        "cluster_snapshot_copy_status": cluster.get(
                            "ClusterSnapshotCopyStatus", {}
                        ),
                        "cluster_public_key": cluster.get("ClusterPublicKey", ""),
                        "cluster_nodes": cluster.get("ClusterNodes", []),
                        "elastic_ip_status": cluster.get("ElasticIpStatus", {}),
                        "cluster_revision_number": cluster.get(
                            "ClusterRevisionNumber", ""
                        ),
                        "tags": cluster.get("Tags", []),
                        "kms_key_id": cluster.get("KmsKeyId", ""),
                        "enhanced_vpc_routing": cluster.get(
                            "EnhancedVpcRouting", False
                        ),
                        "iam_roles": cluster.get("IamRoles", []),
                        "pending_actions": cluster.get("PendingActions", []),
                        "maintenance_track_name": cluster.get(
                            "MaintenanceTrackName", ""
                        ),
                        "elastic_resize_number_of_node_options": cluster.get(
                            "ElasticResizeNumberOfNodeOptions", ""
                        ),
                        "deferred_maintenance_windows": cluster.get(
                            "DeferredMaintenanceWindows", []
                        ),
                        "snapshot_schedule_identifier": cluster.get(
                            "SnapshotScheduleIdentifier", ""
                        ),
                        "snapshot_schedule_state": cluster.get(
                            "SnapshotScheduleState", ""
                        ),
                        "expected_next_snapshot_schedule_time": cluster.get(
                            "ExpectedNextSnapshotScheduleTime"
                        ),
                        "expected_next_snapshot_schedule_time_status": cluster.get(
                            "ExpectedNextSnapshotScheduleTimeStatus", ""
                        ),
                        "next_maintenance_window_start_time": cluster.get(
                            "NextMaintenanceWindowStartTime"
                        ),
                        "resize_info": cluster.get("ResizeInfo", {}),
                        "availability_zone_relocation_status": cluster.get(
                            "AvailabilityZoneRelocationStatus", ""
                        ),
                        "cluster_namespace_arn": cluster.get("ClusterNamespaceArn", ""),
                        "total_storage_capacity_in_mega_bytes": cluster.get(
                            "TotalStorageCapacityInMegaBytes", 0
                        ),
                        "aqua_configuration": cluster.get("AquaConfiguration", {}),
                        "default_iam_role_arn": cluster.get("DefaultIamRoleArn", ""),
                        "reserved_node_exchange_status": cluster.get(
                            "ReservedNodeExchangeStatus", {}
                        ),
                        "custom_domain_name": cluster.get("CustomDomainName", ""),
                        "custom_domain_certificate_arn": cluster.get(
                            "CustomDomainCertificateArn", ""
                        ),
                        "custom_domain_certificate_expiry_date": cluster.get(
                            "CustomDomainCertificateExpiryDate"
                        ),
                        "master_password_secret_arn": cluster.get(
                            "MasterPasswordSecretArn", ""
                        ),
                        "master_password_secret_kms_key_id": cluster.get(
                            "MasterPasswordSecretKmsKeyId", ""
                        ),
                        "ip_address_type": cluster.get("IpAddressType", ""),
                        "multi_az": cluster.get("MultiAZ", ""),
                        "snapshots": snapshots,
                        "parameter_groups": parameter_groups,
                        "security_groups": security_groups,
                        "subnet_groups": subnet_groups,
                    }

                    cluster_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(cluster.get("Tags", [])),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/redshiftv2/home?region={region}#cluster-details?cluster={cluster_id}"
                    resource_id = cluster_id
                    reference = self.get_reference(resource_id, link)

                    cluster_vo = Cluster(cluster_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=cluster_id,
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
                        f'[list_redshift_clusters] [{cluster.get("ClusterIdentifier")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_redshift_clusters] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_cluster_snapshots(self, cluster_id):
        """Get cluster snapshots"""
        try:
            return self.connector.get_cluster_snapshots(cluster_id)
        except Exception as e:
            _LOGGER.warning(f"Failed to get snapshots for cluster {cluster_id}: {e}")
            return []

    def _get_cluster_parameter_groups(self, parameter_groups):
        """Get cluster parameter groups details"""
        if not parameter_groups:
            return []

        try:
            return self.connector.get_cluster_parameter_groups(parameter_groups)
        except Exception as e:
            _LOGGER.warning(f"Failed to get parameter groups: {e}")
            return []

    def _get_cluster_security_groups(self, security_groups):
        """Get cluster security groups details"""
        if not security_groups:
            return []

        try:
            return self.connector.get_cluster_security_groups(security_groups)
        except Exception as e:
            _LOGGER.warning(f"Failed to get security groups: {e}")
            return []

    def _get_cluster_subnet_groups(self, subnet_group_name):
        """Get cluster subnet groups details"""
        if not subnet_group_name:
            return {}

        try:
            return self.connector.get_cluster_subnet_groups(subnet_group_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get subnet groups: {e}")
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
