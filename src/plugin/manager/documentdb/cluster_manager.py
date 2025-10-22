from ..base import ResourceManager, _LOGGER
from ...conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.plugin.collector.lib import *

from ...model.documentdb import Cluster


class ClusterManager(ResourceManager):
    cloud_service_group = "DocumentDB"
    cloud_service_type = "Cluster"
    _parameter_groups = None
    _launch_templates = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DocumentDB"
        self.cloud_service_type = "Cluster"
        self.metadata_path = "metadata/documentdb/cluster.yaml"
        self._parameter_groups = []
        self._subnet_groups = []
        self._raw_instances = []
        self._raw_snapshots = []

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonDocDB",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-DocumentDB.svg"},
            labels=["Database"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        if region in self.EXCLUDE_REGION.get(self.cloud_service_group, []):
            return {}

        yield from self._collect_clusters(options, region)

    def _collect_clusters(self, options, region):
        self.connector.set_account_id()
        self.cloud_service_type = "Cluster"

        self._raw_instances = self._get_instances()
        self._raw_snapshots = self._get_snapshots()

        results = self.connector.get_db_clusters()

        for data in results:
            for raw in data.get("DBClusters", []):
                try:
                    instances = self._match_instances(
                        self._raw_instances, raw.get("DBClusterIdentifier")
                    )
                    raw.update(
                        {
                            "instances": instances,
                            "instance_count": len(instances),
                            "DBClusterIdentifier": self._match_snapshots(
                                self._raw_snapshots, raw.get("DBClusterIdentifier")
                            ),
                            "DBSubnetGroup": self._match_subnet_group(
                                raw.get("DBSubnetGroup")
                            ),
                            "DBClusterParameterGroup": self._match_parameter_group(
                                raw.get("DBClusterParameterGroup")
                            ),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                raw["DBClusterIdentifier"],
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                raw["DBClusterIdentifier"],
                                region,
                            ),
                        }
                    )

                    self._update_cluster_times(raw)

                    cluster_vo = Cluster(raw, strict=False)
                    cluster_arn = cluster_vo.db_cluster_arn
                    cluster_identifier = cluster_vo.db_cluster_identifier
                    link = f"https://console.aws.amazon.com/docdb/home?region={region}#cluster-details/{cluster_identifier}"
                    reference = self.get_reference(cluster_arn, link)

                    cloud_service = make_cloud_service(
                        name=cluster_vo.get("DBClusterIdentifier", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=cluster_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        instance_type=cluster_vo.get("EngineVersion", ""),
                        instance_size=float(cluster_vo.get("instance_count", 0)),
                        tags=self.request_tags(cluster_vo.get("DBClusterArn", "")),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                        resource_type="inventory.CloudService",
                    )

    def request_tags(self, resource_arn):
        response = self.connector.list_tags_for_resource(resource_arn)
        return self.convert_tags_to_dict_type(response.get("TagList", []))

    def _match_subnet_group(self, subnet_group):
        for _sg in self._subnet_groups:
            if _sg.db_subnet_group_name == subnet_group:
                return _sg

        return None

    def _match_parameter_group(self, params_group):
        for _pg in self._parameter_groups:
            if _pg.db_cluster_parameter_group_name == params_group:
                return _pg

        return None

    def _get_instances(self):
        instances = []
        results = self.connector.describe_db_instances()
        for data in results:
            instances.extend(
                [
                    instance
                    for instance in data.get("DBInstances", [])
                    if instance.get("Engine") == "docdb"
                ]
            )

        return instances

    def _get_snapshots(self):
        response = self.connector.describe_db_cluster_snapshots()
        return [
            snapshot
            for snapshot in response.get("DBClusterSnapshots", [])
            if snapshot.get("Engine") == "docdb"
        ]

    def _update_cluster_times(self, raw):
        raw.update(
            {
                "EarliestRestorableTime": self.datetime_to_iso8601(
                    raw.get("EarliestRestorableTime")
                ),
                "LatestRestorableTime": self.datetime_to_iso8601(
                    raw.get("LatestRestorableTime")
                ),
                "ClusterCreateTime": self.datetime_to_iso8601(
                    raw.get("ClusterCreateTime")
                ),
            }
        )
        instances_info = raw.get("instances", {})
        for instance_info in instances_info:
            instance_info.update(
                {
                    "InstanceCreateTime": self.datetime_to_iso8601(
                        instance_info.get("InstanceCreateTime")
                    ),
                    "LastRestorableTime": self.datetime_to_iso8601(
                        instance_info.get("LastRestorableTime")
                    ),
                }
            )
            certificate_details = instance_info.get("CertificateDetails", {})
            if certificate_details:
                certificate_details.update(
                    {
                        "ValidTill": self.datetime_to_iso8601(
                            instance_info.get("ValidTill")
                        )
                    }
                )

        snapshots_info = raw.get("snapshots", {})
        for snapshot_info in snapshots_info:
            snapshot_info.update(
                {
                    "SnapshotCreateTime": self.datetime_to_iso8601(
                        snapshot_info.get("SnapshotCreateTime")
                    ),
                    "ClusterCreateTime": self.datetime_to_iso8601(
                        snapshot_info.get("ClusterCreateTime")
                    ),
                }
            )

    @staticmethod
    def _match_instances(raw_instances, cluster_name):
        return [
            _ins
            for _ins in raw_instances
            if _ins["DBClusterIdentifier"] == cluster_name
        ]

    @staticmethod
    def _match_snapshots(raw_snapshots, cluster_name):
        return [
            _ss for _ss in raw_snapshots if _ss["DBClusterIdentifier"] == cluster_name
        ]
