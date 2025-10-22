import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Key(Model):
    aws_account_id = StringType(deserialize_from="AWSAccountId")
    key_id = StringType(deserialize_from="KeyId")
    arn = StringType(deserialize_from="Arn")
    creation_date = DateTimeType(deserialize_from="CreationDate")
    enabled = BooleanType(deserialize_from="Enabled")
    description = StringType(deserialize_from="Description")
    key_usage = StringType(
        deserialize_from="KeyUsage",
        choices=("SIGN_VERIFY", "ENCRYPT_DECRYPT", "GENERATE_VERIFY_MAC"),
    )
    key_state = StringType(
        deserialize_from="KeyState",
        choices=(
            "Creating",
            "Enabled",
            "Disabled",
            "PendingDeletion",
            "PendingImport",
            "PendingReplicaDeletion",
            "Unavailable",
            "Updating",
        ),
    )
    deletion_date = DateTimeType(deserialize_from="DeletionDate")
    valid_to = DateTimeType(deserialize_from="ValidTo")
    origin = StringType(
        deserialize_from="Origin",
        choices=("AWS_KMS", "EXTERNAL", "AWS_CLOUDHSM", "EXTERNAL_KEY_STORE"),
    )
    custom_key_store_id = StringType(deserialize_from="CustomKeyStoreId")
    cloud_hsm_cluster_id = StringType(deserialize_from="CloudHsmClusterId")
    expiration_model = StringType(
        deserialize_from="ExpirationModel",
        choices=("KEY_MATERIAL_EXPIRES", "KEY_MATERIAL_DOES_NOT_EXPIRE"),
    )
    key_manager = StringType(deserialize_from="KeyManager", choices=("AWS", "CUSTOMER"))
    customer_master_key_spec = StringType(
        deserialize_from="CustomerMasterKeySpec",
        choices=(
            "RSA_2048",
            "RSA_3072",
            "RSA_4096",
            "ECC_NIST_P256",
            "ECC_NIST_P384",
            "ECC_NIST_P521",
            "ECC_SECG_P256K1",
            "SYMMETRIC_DEFAULT",
        ),
    )
    key_spec = StringType(
        deserialize_from="KeySpec",
        choices=(
            "RSA_2048",
            "RSA_3072",
            "RSA_4096",
            "ECC_NIST_P256",
            "ECC_NIST_P384",
            "ECC_NIST_P521",
            "ECC_SECG_P256K1",
            "SYMMETRIC_DEFAULT",
        ),
    )
    encryption_algorithms = ListType(
        StringType, deserialize_from="EncryptionAlgorithms"
    )
    signing_algorithms = ListType(StringType, deserialize_from="SigningAlgorithms")
    multi_region = BooleanType(deserialize_from="MultiRegion")
    multi_region_configuration = StringType(deserialize_from="MultiRegionConfiguration")
    pending_deletion_window_in_days = IntType(
        deserialize_from="PendingDeletionWindowInDays"
    )
    mac_algorithms = ListType(StringType, deserialize_from="MacAlgorithms")
    xks_key_configuration = StringType(deserialize_from="XksKeyConfiguration")
