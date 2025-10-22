# import logging
# from schematics import Model
# from schematics.types import StringType, IntType, DateTimeType, ListType, BooleanType
#
# _LOGGER = logging.getLogger(__name__)
#
#
# class Snapshot(Model):
#     data_encryption_key_id = StringType(deserialize_from="DataEncryptionKeyId")
#     description = StringType(deserialize_from="Description")
#     encrypted = BooleanType(deserialize_from="Encrypted")
#     kms_key_id = StringType(deserialize_from="KmsKeyId")
#     owner_id = StringType(deserialize_from="OwnerId")
#     progress = StringType(deserialize_from="Progress")
#     snapshot_id = StringType(deserialize_from="SnapshotId")
#     start_time = DateTimeType(deserialize_from="StartTime")
#     state = StringType(
#         deserialize_from="State", choices=("pending", "completed", "error")
#     )
#     state_message = StringType(deserialize_from="StateMessage")
#     volume_id = StringType(deserialize_from="VolumeId")
#     volume_size = IntType(deserialize_from="VolumeSize")
#     owner_alias = StringType(deserialize_from="OwnerAlias")
#     tags = StringType(deserialize_from="Tags")
#     storage_tier = StringType(
#         deserialize_from="StorageTier", choices=("archive", "standard")
#     )
#     restore_expiry_time = DateTimeType(deserialize_from="RestoreExpiryTime")
