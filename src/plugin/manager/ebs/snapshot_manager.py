# from typing import List
#
# from spaceone.inventory.plugin.collector.lib import (
#     make_cloud_service_type,
#     make_cloud_service,
#     make_error_response,
# )
#
# from ..base import ResourceManager, _LOGGER
# from ...model.ebs import Snapshot
#
#
# class SnapshotManager(ResourceManager):
#     cloud_service_group = "EC2"
#     cloud_service_type = "Snapshot"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.cloud_service_group = "EC2"
#         self.cloud_service_type = "Snapshot"
#         self.metadata_path = "metadata/ebs/snapshot.yaml"
#
#     def create_cloud_service_type(self):
#         result = []
#         snapshot_cst_result = make_cloud_service_type(
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
#         result.append(snapshot_cst_result)
#         return result
#
#     def create_cloud_service(
#         self, region: str, options: dict, secret_data: dict, schema: str
#     ):
#         yield from self._collect_snapshots(options, region)
#
#     def _collect_snapshots(self, options, region):
#         cloudtrail_resource_type = 'AWS::EC2::Snapshot'
#
#         try:
#             snapshots, account_id = self.connector.list_ebs_snapshots()
#
#             for snapshot in snapshots:
#                 try:
#                     snapshot_id = snapshot.get("SnapshotId")
#
#                     if name := self._get_name_from_tags(snapshot.get("Tags", [])):
#                         snapshot['name'] = name
#
#                     snapshot.update({
#                         'cloudtrail': self.set_cloudtrail(region, cloudtrail_resource_type, snapshot['SnapshotId']),
#                         'arn': self.generate_arn(service="ec2", region=region,
#                                                  account_id=options.get("account_ud"), resource_type="snapshot",
#                                                  resource_id=snapshot.get('SnapshotId'))
#                     })
#
#                     if kms_arn := snapshot.get('KmsKeyId'):
#                         snapshot.update({
#                             'kms_key_arn': kms_arn,
#                             'kms_key_id': self._get_kms_key_id(kms_arn)
#                         })
#
#                     link = f"https://{region}.console.aws.amazon.com/ec2/home?region={region}#Snapshots:search={snapshot_id}"
#                     resource_id = snapshot_id
#                     reference = self.get_reference(resource_id, link)
#
#                     snapshot_vo = Snapshot(snapshot, strict=False)
#                     cloud_service = make_cloud_service(
#                         name=snapshot_id,
#                         cloud_service_type=self.cloud_service_type,
#                         cloud_service_group=self.cloud_service_group,
#                         provider=self.provider,
#                         data=snapshot_vo.to_primitive(),
#                         account=options.get("account_id"),
#                         reference=reference,
#                         tags=snapshot.tags,
#                         region_code=region,
#                     )
#                     yield cloud_service
#
#                 except Exception as e:
#                     _LOGGER.error(
#                         f'[list_ebs_snapshots] [{snapshot.get("SnapshotId")}] {e}'
#                     )
#                     yield make_error_response(
#                         error=e,
#                         provider=self.provider,
#                         cloud_service_group=self.cloud_service_group,
#                         cloud_service_type=self.cloud_service_type,
#                         region_name=region,
#                     )
#
#         except Exception as e:
#             _LOGGER.error(f"[list_ebs_snapshots] [{region_name}] {e}")
#             yield make_error_response(
#                 error=e,
#                 provider=self.provider,
#                 cloud_service_group=self.cloud_service_group,
#                 cloud_service_type=self.cloud_service_type,
#                 region_name=region,
#             )
#
#     @staticmethod
#     def _get_name_from_tags(tags):
#         for _tag in tags:
#             if 'Name' in _tag.get('Key'):
#                 return _tag.get('Value')
#
#         return None
#
#     @staticmethod
#     def _get_kms_key_id(kms_arn):
#         try:
#             return kms_arn.split('/')[1]
#         except IndexError:
#             return ''
