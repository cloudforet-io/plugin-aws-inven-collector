from spaceone.inventory.plugin.collector.lib import *
from plugin.manager.base import ResourceManager
from plugin.conf.cloud_service_conf import *


class TableManager(ResourceManager):
    cloud_service_group = "DynamoDB"
    cloud_service_type = "Table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "DynamoDB"
        self.cloud_service_type = "Table"
        self.metadata_path = "metadata/dynamodb/table.yaml"

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonDynamoDB",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-DynamoDB.svg"},
            labels=["Database"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        _auto_scaling_policies = None
        cloudwatch_namespace = "AWS/DynamoDB"
        cloudwatch_dimension_name = "TableName"
        cloudtrail_resource_type = "AWS::DynamoDB::Table"
        self.connector.set_account_id()
        results = self.connector.get_tables()
        account_id = self.connector.get_account_id()
        for data in results:
            for table_name in data.get("TableNames", []):
                try:
                    table = {}
                    # response = self.client.describe_table(TableName=table_name)
                    response = self.connector.describe_table(table_name)
                    table = response.get("Table")

                    partition_key, sort_key = self._get_key_info(
                        table.get("KeySchema", []),
                        table.get("AttributeDefinitions", []),
                    )

                    (
                        index_count,
                        total_read_capacity,
                        total_write_capacity,
                    ) = self._get_index_info(table.get("GlobalSecondaryIndexes", []))

                    if _auto_scaling_policies is None:
                        _auto_scaling_policies = self.describe_scaling_policies()

                    table.update(
                        {
                            "partition_key_display": partition_key,
                            "sort_key_display": sort_key,
                            "auto_scaling_policies": self._get_auto_scaling(
                                _auto_scaling_policies, table_name
                            ),
                            "encryption_type": self._get_encryption_type(
                                table.get("SSEDescription", {})
                            ),
                            "index_count": index_count,
                            "total_read_capacity": total_read_capacity,
                            "total_write_capacity": total_write_capacity,
                            "time_to_live": self._get_time_to_live(table_name),
                            "continuous_backup": self._get_continuous_backup(
                                table_name
                            ),
                            "contributor_insight": self._get_contributor_insights(
                                table_name
                            ),
                            "cloudwatch": self.set_cloudwatch(
                                cloudwatch_namespace,
                                cloudwatch_dimension_name,
                                table["TableName"],
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region,
                                cloudtrail_resource_type,
                                table["TableName"],
                            ),
                        }
                    )
                    table_vo = table

                    # Converting datetime type attributes to ISO8601 format needed to meet protobuf format
                    self._update_times(table_vo)

                    table_arn = table_vo.get("TableArn", "")
                    table_name = table_vo.get("TableName", "")
                    link = f"https://console.aws.amazon.com/dynamodb/home?region={region}#tables:selected={table_name};tab=overview"
                    reference = self.get_reference(table_arn, link)

                    cloud_service = make_cloud_service(
                        name=table_vo.get("TableName", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=table_vo,
                        account=account_id,
                        reference=reference,
                        instance_size=float(table_vo.get("TableSizeBytes", 0)),
                        tags=self.request_tags(table_vo.get("TableArn", "")),
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
                    )

    def _get_contributor_insights(self, table_name):
        response = self.connector.describe_contributor_insights(table_name)
        del response["ResponseMetadata"]

        return response

    def _get_continuous_backup(self, table_name):
        response = self.connector.describe_continuous_backups(table_name)
        return response.get("ContinuousBackupsDescription")

    def _get_time_to_live(self, table_name):
        response = self.connector.describe_time_to_live(table_name)
        return response.get("TimeToLiveDescription")

    def describe_scaling_policies(self):
        response = self.connector.describe_scaling_policies("dynamodb")
        return response.get("ScalingPolicies", [])

    def _get_key_info(self, keys, key_attrs):
        partition_key = ""
        sort_key = ""

        for key in keys:
            if partition_key == "":
                partition_key = self._search_key(key, "HASH", key_attrs)
            if sort_key == "":
                sort_key = self._search_key(key, "RANGE", key_attrs)

        return partition_key, sort_key

    def request_tags(self, resource_arn):
        response = self.connector.list_tags_of_resource(resource_arn)
        return self.convert_tags_to_dict_type(response.get("Tags", []))

    def _update_times(self, raw):
        raw.update(
            {
                "CreationDateTime": self.datetime_to_iso8601(
                    raw.get("CreationDateTime")
                ),
                "LatestRestorableTime": self.datetime_to_iso8601(
                    raw.get("LatestRestorableTime")
                ),
                "ClusterCreateTime": self.datetime_to_iso8601(
                    raw.get("ClusterCreateTime")
                ),
            }
        )
        throughput_info = raw.get("ProvisionedThroughput", {})
        throughput_info.update(
            {
                "LastIncreaseDateTime": self.datetime_to_iso8601(
                    throughput_info.get("LastIncreaseDateTime")
                ),
                "LastDecreaseDateTime": self.datetime_to_iso8601(
                    throughput_info.get("LastDecreaseDateTime")
                ),
            }
        )
        billing_summary_info = raw.get("BillingModeSummary", {})
        billing_summary_info.update(
            {
                "LastUpdateToPayPerRequestDateTime": self.datetime_to_iso8601(
                    billing_summary_info.get("LastUpdateToPayPerRequestDateTime")
                )
            }
        )
        restore_summary_info = raw.get("RestoreSummary", {})
        restore_summary_info.update(
            {
                "RestoreDateTime": self.datetime_to_iso8601(
                    restore_summary_info.get("RestoreDateTime")
                )
            }
        )
        sse_description_info = raw.get("SSEDescription", {})
        sse_description_info.update(
            {
                "InaccessibleEncryptionDateTime": self.datetime_to_iso8601(
                    sse_description_info.get("InaccessibleEncryptionDateTime")
                )
            }
        )
        archival_summary_info = raw.get("ArchivalSummary", {})
        archival_summary_info.update(
            {
                "ArchivalDateTime": self.datetime_to_iso8601(
                    archival_summary_info.get("ArchivalDateTime")
                )
            }
        )
        continuous_backup_info = raw.get("continuous_backup", {})
        point_in_time_info = continuous_backup_info.get(
            "PointInTimeRecoveryDescription", {}
        )
        point_in_time_info.update(
            {
                "EarliestRestorableDateTime": self.datetime_to_iso8601(
                    point_in_time_info.get("EarliestRestorableDateTime")
                ),
                "LatestRestorableDateTime": self.datetime_to_iso8601(
                    point_in_time_info.get("LatestRestorableDateTime")
                ),
            }
        )
        contributor_insight_info = raw.get("contributor_insight", {})
        contributor_insight_info.update(
            {
                "LastUpdateDateTime": self.datetime_to_iso8601(
                    contributor_insight_info.get("LastUpdateDateTime")
                )
            }
        )

    @staticmethod
    def _get_auto_scaling(as_policies, table_name):
        auto_scalings = []

        for asp in as_policies:
            if asp.get("ResourceId") == f"table/{table_name}":
                if "ReadCapacityUnits" in asp.get("ScalableDimension"):
                    auto_scalings.append("READ")
                if "WriteCapacityUnits" in asp.get("ScalableDimension"):
                    auto_scalings.append("WRITE")

        return auto_scalings

    @staticmethod
    def _get_index_info(indexes):
        read_count = 0
        write_count = 0

        for _index in indexes:
            provisioned_throughput = _index.get("ProvisionedThroughput", {})

            if "ReadCapacityUnits" in provisioned_throughput:
                read_count = read_count + provisioned_throughput.get(
                    "ReadCapacityUnits"
                )

            if "WriteCapacityUnits" in provisioned_throughput:
                write_count = write_count + provisioned_throughput.get(
                    "WriteCapacityUnits"
                )

        return len(indexes), read_count, write_count

    @staticmethod
    def _get_encryption_type(sse_description):
        if sse_type := sse_description.get("SSEType"):
            return sse_type
        else:
            return "DEFAULT"

    @staticmethod
    def _search_key(key, key_type, key_attrs):
        match_key_attr = {"S": "String", "N": "Number", "B": "Binary"}

        if key.get("KeyType") == key_type:
            key_name = key.get("AttributeName", "")

            for attr in key_attrs:
                if key_name == attr.get("AttributeName"):
                    if attr.get("AttributeType") in match_key_attr:
                        return f'{key_name} ({match_key_attr.get(attr.get("AttributeType"))})'
