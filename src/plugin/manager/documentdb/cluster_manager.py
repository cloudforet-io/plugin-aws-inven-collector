from ..base import ResourceManager, _LOGGER
from ...conf.cloud_service_conf import ASSET_URL
from spaceone.inventory.plugin.collector.lib import *


EXCLUDE_REGION = [
    "us-west-1",
    "af-south-1",
    "ap-east-1",
    "ap-southeast-3",
    "ap-northeast-3",
    "eu-north-1",
    "me-south-1",
]


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
        yield from self._create_parameter_group_type()
        yield from self._create_subnet_group_type()

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
        if region in EXCLUDE_REGION:
            return {}
        self.connector.set_account_id()
        self.cloud_service_type = "Cluster"
        cloudwatch_namespace = "AWS/DocDB"
        cloudwatch_dimension_name = "DBClusterIdentifier"
        cloudtrail_resource_type = "AWS::RDS::DBCluster"

        self._raw_instances = self._get_instances()
        self._raw_snapshots = self._get_snapshots()

        pre_collect_list = [
            self._create_parameter_groups,
            self._create_subnet_groups,
        ]
        for pre_collect in pre_collect_list:
            yield from pre_collect(region)

        results = self.connector.get_db_clusters()
        account_id = self.connector.get_account_id()

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
                            "snapshots": self._match_snapshots(
                                self._raw_snapshots, raw.get("DBClusterIdentifier")
                            ),
                            "subnet_group": self._match_subnet_group(
                                raw.get("DBSubnetGroup")
                            ),
                            "parameter_group": self._match_parameter_group(
                                raw.get("DBClusterParameterGroup")
                            ),
                            "cloudwatch": self.set_cloudwatch(
                                cloudwatch_namespace,
                                cloudwatch_dimension_name,
                                raw["DBClusterIdentifier"],
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region,
                                cloudtrail_resource_type,
                                raw["DBClusterIdentifier"],
                            ),
                        }
                    )

                    if subnet_group := self._match_subnet_group(
                        raw.get("DBSubnetGroup")
                    ):
                        raw.update({"subnet_group": subnet_group})

                    if parameter_group := self._match_parameter_group(
                        raw.get("DBClusterParameterGroup")
                    ):
                        raw.update({"parameter_group": parameter_group})

                    cluster_vo = raw
                    self._update_cluster_times(cluster_vo)
                    cluster_arn = cluster_vo.get("DBClusterArn", "")
                    cluster_identifier = cluster_vo.get("DBClusterIdentifier", "")
                    link = f"https://console.aws.amazon.com/docdb/home?region={region}#cluster-details/{cluster_identifier}"
                    reference = self.get_reference(cluster_arn, link)

                    cloud_service = make_cloud_service(
                        name=cluster_vo.get("DBClusterIdentifier", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=cluster_vo,
                        account=account_id,
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

    def _create_parameter_group_type(self):
        cloud_service_type = "ParameterGroup"
        metadata_path = "metadata/documentdb/parameter.yaml"

        yield make_cloud_service_type(
            name=cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonDocDB",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-DocumentDB.svg"},
            labels=["Database"],
        )

    def _create_subnet_group_type(self):
        cloud_service_type = "SubnetGroup"
        metadata_path = "metadata/documentdb/subnet.yaml"

        yield make_cloud_service_type(
            name=cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonDocDB",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-DocumentDB.svg"},
            labels=["Database"],
        )

    def _create_parameter_groups(self, region):
        cloud_service_type = "ParameterGroup"
        cloudtrail_resource_type = "AWS::RDS::DBClusterParameterGroup"

        res_pgs = self.connector.get_db_cluster_parameter_groups()
        account_id = self.connector.get_account_id()

        for pg_data in res_pgs.get("DBClusterParameterGroups", []):
            try:
                pg_data.update(
                    {
                        "cloudtrail": self.set_cloudtrail(
                            region,
                            cloudtrail_resource_type,
                            pg_data["DBClusterParameterGroupName"],
                        ),
                        "parameters": self.request_parameter_data(
                            pg_data["DBClusterParameterGroupName"]
                        ),
                    }
                )
                param_group_vo = pg_data
                parameter_arn = param_group_vo.get("DBClusterParameterGroupArn", "")
                parameter_name = param_group_vo.get("DBClusterParameterGroupName", "")
                link = f"https://console.aws.amazon.com/docdb/home?region={region}#parameterGroup-details/{parameter_name}"
                reference = self.get_reference(parameter_arn, link)

                cloud_service = make_cloud_service(
                    name=param_group_vo.get("DBClusterParameterGroupName", ""),
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=param_group_vo,
                    account=account_id,
                    reference=reference,
                    instance_type=param_group_vo.get("DBParameterGroupFamily", ""),
                    tags=self.request_tags(
                        param_group_vo.get("DBClusterParameterGroupArn", "")
                    ),
                    region_code=region,
                )
                yield cloud_service

            except Exception as e:
                yield make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=cloud_service_type,
                    region_name=region,
                    resource_type="inventory.CloudService",
                )

    def _create_subnet_groups(self, region):
        cloud_service_type = "SubnetGroup"
        cloudtrail_resource_type = "AWS::RDS::DBSubnetGroup"

        response = self.connector.get_db_subnet_groups()
        account_id = self.connector.get_account_id()
        for data in response:
            for raw in data.get("DBSubnetGroups", []):
                try:
                    raw.update(
                        {
                            "cloudtrail": self.set_cloudtrail(
                                region,
                                cloudtrail_resource_type,
                                raw["DBSubnetGroupName"],
                            )
                        }
                    )
                    subnet_grp_vo = raw
                    subnet_arn = subnet_grp_vo.get("DBSubnetGroupArn", "")
                    subnet_name = subnet_grp_vo.get("DBClusterParameterGroupName", "")
                    link = f"https://console.aws.amazon.com/docdb/home?region={region}#subnetGroup-details/{subnet_name}"
                    reference = self.get_reference(subnet_arn, link)

                    cloud_service = make_cloud_service(
                        name=subnet_grp_vo.get("DBSubnetGroupName", ""),
                        cloud_service_type=cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=subnet_grp_vo,
                        account=account_id,
                        reference=reference,
                        tags=self.request_tags(
                            subnet_grp_vo.get("DBSubnetGroupArn", "")
                        ),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=cloud_service_type,
                        region_name=region,
                        resource_type="inventory.CloudService",
                    )

    def request_tags(self, resource_arn):
        response = self.connector.list_tags_for_resource(resource_arn)
        return self.convert_tags_to_dict_type(response.get("TagList", []))

    def request_parameter_data(self, pg_name):
        res_params = self.connector.describe_db_cluster_parameters(pg_name)
        return list(
            map(
                lambda param: param,
                res_params.get("Parameters", []),
            )
        )

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
