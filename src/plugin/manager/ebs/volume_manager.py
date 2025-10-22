# from typing import List
#
# from spaceone.inventory.plugin.collector.lib import (
#     make_cloud_service_type,
#     make_cloud_service,
#     make_error_response,
# )
#
# from ..base import ResourceManager, _LOGGER
# from ...model.ebs import Volume
#
#
# class VolumeManager(ResourceManager):
#     cloud_service_group = "EBS"
#     cloud_service_type = "Volume"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.cloud_service_group = "EBS"
#         self.cloud_service_type = "Volume"
#         self.metadata_path = "metadata/ebs/volume.yaml"
#
#     def create_cloud_service_type(self):
#         result = []
#         volume_cst_result = make_cloud_service_type(
#             name=self.cloud_service_type,
#             group=self.cloud_service_group,
#             provider=self.provider,
#             metadata_path=self.metadata_path,
#             is_primary=True,
#             is_major=True,
#             service_code="AmazonEC2",
#             tags={
#                 "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-ebs.svg"
#             },
#             labels=["Storage"],
#         )
#         result.append(volume_cst_result)
#         return result
#
#     def create_cloud_service(
#         self, region: str, options: dict, secret_data: dict, schema: str
#     ):
#         yield from self._collect_volumes(options, region)
#
#     def _collect_volumes(self, options, region):
#         region_name = region
#         cloudtrail_resource_type = "AWS::EC2::Volume"
#
#         try:
#             volumes, account_id = self.connector.list_ebs_volumes()
#
#             for volume in volumes:
#                 try:
#                     volume_id = volume.get("VolumeId")
#
#                     # Get volume tags
#                     tags = self._get_volume_tags(volume_id)
#
#                     # Get volume attributes
#                     attributes = self._get_volume_attributes(volume_id)
#
#                     volume_data = {
#                         "volume_id": volume_id,
#                         "size": volume.get("Size", 0),
#                         "snapshot_id": volume.get("SnapshotId", ""),
#                         "availability_zone": volume.get("AvailabilityZone", ""),
#                         "state": volume.get("State", ""),
#                         "create_time": volume.get("CreateTime"),
#                         "volume_type": volume.get("VolumeType", ""),
#                         "iops": volume.get("Iops", 0),
#                         "encrypted": volume.get("Encrypted", False),
#                         "kms_key_id": volume.get("KmsKeyId", ""),
#                         "throughput": volume.get("Throughput", 0),
#                         "outpost_arn": volume.get("OutpostArn", ""),
#                         "multi_attach_enabled": volume.get("MultiAttachEnabled", False),
#                         "fast_restored": volume.get("FastRestored", False),
#                         "attachments": volume.get("Attachments", []),
#                         "attributes": attributes,
#                     }
#
#                     volume_data.update(
#                         {
#                             "region_code": region_name,
#                             "account": account_id,
#                             "tags": self.convert_tags(tags),
#                         }
#                     )
#
#                     link = f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#Volumes:search={volume_id}"
#                     resource_id = volume_id
#                     reference = self.get_reference(resource_id, link)
#
#                     volume_vo = Volume(volume_data, strict=False)
#                     cloud_service = make_cloud_service(
#                         name=volume_id,
#                         cloud_service_type=self.cloud_service_type,
#                         cloud_service_group=self.cloud_service_group,
#                         provider=self.provider,
#                         data=volume_vo.to_primitive(),
#                         account=options.get("account_id"),
#                         reference=reference,
#                         tags=volume_data.get("tags", {}),
#                         region_code=region,
#                     )
#                     yield cloud_service
#
#                 except Exception as e:
#                     _LOGGER.error(f'[list_ebs_volumes] [{volume.get("VolumeId")}] {e}')
#                     yield make_error_response(
#                         error=e,
#                         provider=self.provider,
#                         cloud_service_group=self.cloud_service_group,
#                         cloud_service_type=self.cloud_service_type,
#                         region_name=region,
#                     )
#
#         except Exception as e:
#             _LOGGER.error(f"[list_ebs_volumes] [{region_name}] {e}")
#             yield make_error_response(
#                 error=e,
#                 provider=self.provider,
#                 cloud_service_group=self.cloud_service_group,
#                 cloud_service_type=self.cloud_service_type,
#                 region_name=region,
#             )
#
#     def _get_volume_tags(self, volume_id):
#         """Get volume tags"""
#         try:
#             return self.connector.get_volume_tags(volume_id)
#         except Exception as e:
#             _LOGGER.warning(f"Failed to get tags for volume {volume_id}: {e}")
#             return []
#
#     def _get_volume_attributes(self, volume_id):
#         """Get volume attributes"""
#         try:
#             return self.connector.get_volume_attributes(volume_id)
#         except Exception as e:
#             _LOGGER.warning(f"Failed to get attributes for volume {volume_id}: {e}")
#             return {}
#
#     def convert_tags(self, tags):
#         """Convert tags to dictionary format"""
#         dict_tags = {}
#         for tag in tags:
#             dict_tags[tag.get("Key")] = tag.get("Value")
#         return dict_tags
