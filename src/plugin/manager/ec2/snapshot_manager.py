from ..base import ResourceManager
from spaceone.inventory.plugin.collector.lib import *

from ...conf.cloud_service_conf import ASSET_URL


class SnapshotManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "Snapshot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "Snapshot"
        self.metadata_path = "metadata/ec2/snapshot.yaml"

    def create_cloud_service_type(self):
        result = []
        snapshot_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=False,
            is_major=False,
            service_code="AmazonEC2",
            tags={
                "spaceone:icon": f"{ASSET_URL}/Amazon-Elastic-Block-Store-EBS.svg",
            },
            labels=["Compute", "Storage"],
        )
        result.append(snapshot_cst_result)
        return result

    def create_cloud_service(self, region, options, secret_data, schema):
        cloudtrail_resource_type = "AWS::EC2::Snapshot"
        account_id = options.get("account_id", "")
        self.connector.load_account_id(account_id)
        results = self.connector.get_snapshots()

        for data in results:
            for raw in data.get("Snapshots", []):
                try:
                    if name := self._get_name_from_tags(raw.get("Tags", [])):
                        raw["name"] = name
                    raw.update(
                        {
                            "cloudtrail": self.set_cloudtrail(
                                region, cloudtrail_resource_type, raw["SnapshotId"]
                            ),
                            "arn": self.generate_arn(
                                service="ec2",
                                region=region,
                                account_id=account_id,
                                resource_type="snapshot",
                                resource_id=raw.get("SnapshotId"),
                            ),
                        }
                    )

                    if kms_arn := raw.get("KmsKeyId"):
                        raw.update(
                            {
                                "kms_key_arn": kms_arn,
                                "kms_key_id": self._get_kms_key_id(kms_arn),
                            }
                        )

                    print(type(raw.get("StartTime")))
                    self._update_times(raw)
                    print(raw.get("StartTime"))
                    print(type(raw.get("StartTime")))

                    snapshot_vo = raw

                    print(type(snapshot_vo.get("StartTime")))
                    print(f"DATA : {snapshot_vo}")

                    resource_id = snapshot_vo.get("arn", "")
                    snapshot_id = snapshot_vo.get("SnapshotId", "")
                    link = f"https://console.aws.amazon.com/ec2/v2/home?region={region}#Snapshots:visibility=owned-by-me;snapshotId={snapshot_id};sort=snapshotId"
                    reference = self.get_reference(resource_id, link)
                    cloud_service = make_cloud_service(
                        name=snapshot_vo.get("name", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        instance_size=float(snapshot_vo.get("VolumeSize", 0)),
                        provider=self.provider,
                        data=snapshot_vo,
                        account=account_id,
                        tags=self.convert_tags_to_dict_type(raw.get("Tags", [])),
                        region_code=region,
                        reference=reference,
                    )
                    yield cloud_service

                    # yield {
                    #     "data": snapshot_vo,
                    #     "name": snapshot_vo.name,
                    #     "instance_size": float(snapshot_vo.volume_size),
                    #     "launched_at": self.datetime_to_iso8601(snapshot_vo.start_time),
                    #     "account": self.account_id,
                    #     "tags": self.convert_tags_to_dict_type(raw.get("Tags", [])),
                    # }

                except Exception as e:
                    # resource_id = raw.get("SnapshotId", "")
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

    @staticmethod
    def _get_name_from_tags(tags):
        for _tag in tags:
            if "Name" in _tag.get("Key"):
                return _tag.get("Value")

        return None

    @staticmethod
    def _get_kms_key_id(kms_arn):
        try:
            return kms_arn.split("/")[1]
        except IndexError:
            return ""

    @staticmethod
    def get_size_gb_to_bytes(gb_size):
        return gb_size * 1024 * 1024 * 1024

    def _update_times(self, snapshot_info: dict) -> None:
        snapshot_info.update(
            {
                "StartTime": self.datetime_to_iso8601(snapshot_info.get("StartTime")),
            }
        )
