from ..base import ResourceManager
from spaceone.inventory.plugin.collector.lib import *

from ...conf.cloud_service_conf import ASSET_URL


class VolumeManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "Volume"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "Volume"
        self.metadata_path = "metadata/ec2/volume.yaml"

    def create_cloud_service_type(self):
        result = []
        volume_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonEC2",
            tags={
                "spaceone:icon": f"{ASSET_URL}/Amazon-Elastic-Block-Store-EBS.svg",
                "spaceone:display_name": "EBS",
            },
            labels=["Compute", "Storage"],
        )
        result.append(volume_cst_result)
        return result

    def create_cloud_service(self, region, options, secret_data, schema):
        cloudtrail_resource_type = "AWS::EC2::Volume"
        account_id = options.get("account_id", "")
        self.connector.load_account_id(account_id)
        cloudwatch_namespace = "AWS/EBS"
        cloudwatch_dimension_name = "VolumeId"
        results = self.connector.get_volumes()

        for data in results:
            for raw in data.get("Volumes", []):
                try:
                    if name := self._get_name_from_tags(raw.get("Tags", [])):
                        raw["name"] = name

                    attr = self.connector.get_volume_attribute(
                        "productCodes", raw["VolumeId"]
                    )
                    raw.update(
                        {
                            "attribute": attr,
                            "cloudwatch": self.set_cloudwatch(
                                cloudwatch_namespace,
                                cloudwatch_dimension_name,
                                raw["VolumeId"],
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                region, cloudtrail_resource_type, raw["VolumeId"]
                            ),
                            "size": self.get_size_gb_to_bytes(raw.get("Size", 0)),
                            "arn": self.generate_arn(
                                service="ec2",
                                region=region,
                                account_id=account_id,
                                resource_type="volume",
                                resource_id=raw.get("VolumeId"),
                            ),
                            "launched_at": self.datetime_to_iso8601(
                                raw.get("CreateTime")
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

                    self._update_times(raw)

                    volume_vo = raw

                    resource_id = volume_vo.get("arn", "")
                    volume_id = volume_vo.get("VolumeId", "")
                    link = f"https://console.aws.amazon.com/ec2/v2/home?region={region}#Volumes:search={volume_id};sort=state"
                    reference = self.get_reference(resource_id, link)

                    cloud_service = make_cloud_service(
                        name=volume_vo.get("name", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        instance_type=volume_vo.get("VolumeType", ""),
                        instance_size=float(volume_vo.get("size", 0)),
                        provider=self.provider,
                        data=volume_vo,
                        account=account_id,
                        tags=self.convert_tags_to_dict_type(raw.get("Tags", [])),
                        region_code=region,
                        reference=reference,
                    )
                    yield cloud_service
                    # yield {
                    #     "data": volume_vo,
                    #     "name": volume_vo.name,
                    #     "instance_size": float(volume_vo.size),
                    #     "instance_type": volume_vo.volume_type,
                    #     "launched_at": self.datetime_to_iso8601(volume_vo.create_time),
                    #     "account": account_id,
                    #     "tags": self.convert_tags_to_dict_type(raw.get("Tags", [])),
                    # }

                except Exception as e:
                    # resource_id = raw.get("VolumeId", "")
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

    def _update_times(self, volume_info: dict) -> None:
        volume_info.update(
            {
                "CreateTime": self.datetime_to_iso8601(volume_info.get("CreateTime")),
            }
        )
        attachments_info = volume_info.get("Attachments", {})
        for attachment_info in attachments_info:
            attachment_info.update(
                {
                    "AttachTime": self.datetime_to_iso8601(
                        attachment_info.get("AttachTime")
                    )
                }
            )
