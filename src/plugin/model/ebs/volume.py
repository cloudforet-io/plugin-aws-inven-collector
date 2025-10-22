# import logging
# from schematics import Model
# from schematics.types import StringType, IntType, DateTimeType, ListType, BooleanType
#
# _LOGGER = logging.getLogger(__name__)
#
#
# class Volume(Model):
#     availability_zone = StringType(deserialize_from="AvailabilityZone")
#     create_time = DateTimeType(deserialize_from="CreateTime")
#     encrypted = BooleanType(deserialize_from="Encrypted")
#     size = IntType(deserialize_from="Size")
#     snapshot_id = StringType(deserialize_from="SnapshotId")
#     state = StringType(
#         deserialize_from="State",
#         choices=("creating", "available", "in-use", "deleting", "deleted", "error"),
#     )
#     volume_id = StringType(deserialize_from="VolumeId")
#     iops = IntType(deserialize_from="Iops")
#     tags = StringType(deserialize_from="Tags")
#     volume_type = StringType(
#         deserialize_from="VolumeType",
#         choices=("standard", "io1", "io2", "gp2", "gp3", "sc1", "st1"),
#     )
#     fast_restored = BooleanType(deserialize_from="FastRestored")
#     multi_attach_enabled = BooleanType(deserialize_from="MultiAttachEnabled")
#     throughput = IntType(deserialize_from="Throughput")
#     outpost_arn = StringType(deserialize_from="OutpostArn")
#
#     def reference(self, region_code):
#         return {
#             "resource_id": self.volume_id,
#             "external_link": f"https://console.aws.amazon.com/ec2/v2/home?region={region_code}#Volumes:search={self.volume_id}",
#         }
