import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Function(Model):
    function_name = StringType(deserialize_from="FunctionName")
    function_arn = StringType(deserialize_from="FunctionArn")
    runtime = StringType(deserialize_from="Runtime")
    role = StringType(deserialize_from="Role")
    handler = StringType(deserialize_from="Handler")
    code_size = IntType(deserialize_from="CodeSize")
    description = StringType(deserialize_from="Description")
    timeout = IntType(deserialize_from="Timeout")
    memory_size = IntType(deserialize_from="MemorySize")
    last_modified = DateTimeType(deserialize_from="LastModified")
    code_sha256 = StringType(deserialize_from="CodeSha256")
    version = StringType(deserialize_from="Version")
    vpc_config = StringType(deserialize_from="VpcConfig")
    dead_letter_config = StringType(deserialize_from="DeadLetterConfig")
    environment = StringType(deserialize_from="Environment")
    kms_key_arn = StringType(deserialize_from="KMSKeyArn")
    tracing_config = StringType(deserialize_from="TracingConfig")
    master_arn = StringType(deserialize_from="MasterArn")
    revision_id = StringType(deserialize_from="RevisionId")
    layers = StringType(deserialize_from="Layers")
    state = StringType(
        deserialize_from="State", choices=("Pending", "Active", "Inactive", "Failed")
    )
    state_reason = StringType(deserialize_from="StateReason")
    state_reason_code = StringType(
        deserialize_from="StateReasonCode",
        choices=(
            "Idle",
            "Creating",
            "Restoring",
            "EniLimitExceeded",
            "InsufficientRolePermissions",
            "InvalidConfiguration",
            "InternalError",
            "SubnetOutOfIPAddresses",
            "InvalidSubnet",
            "InvalidSecurityGroup",
            "ImageDeleted",
            "ImageAccessDenied",
            "InvalidImage",
            "KMSKeyAccessDenied",
            "KMSKeyNotFound",
            "InvalidStateKMSKey",
            "DisabledKMSKey",
            "EFSIOError",
            "EFSMountConnectivityError",
            "EFSMountFailure",
            "EFSMountTimeout",
            "InvalidRuntime",
            "InvalidZipFileException",
            "FunctionError",
        ),
    )
    last_update_status = StringType(
        deserialize_from="LastUpdateStatus",
        choices=("InProgress", "Successful", "Failed"),
    )
    last_update_status_reason = StringType(deserialize_from="LastUpdateStatusReason")
    last_update_status_reason_code = StringType(
        deserialize_from="LastUpdateStatusReasonCode",
        choices=(
            "EniLimitExceeded",
            "InsufficientRolePermissions",
            "InvalidConfiguration",
            "InternalError",
            "SubnetOutOfIPAddresses",
            "InvalidSubnet",
            "InvalidSecurityGroup",
            "ImageDeleted",
            "ImageAccessDenied",
            "InvalidImage",
            "KMSKeyAccessDenied",
            "KMSKeyNotFound",
            "InvalidStateKMSKey",
            "DisabledKMSKey",
            "EFSIOError",
            "EFSMountConnectivityError",
            "EFSMountFailure",
            "EFSMountTimeout",
            "InvalidRuntime",
            "InvalidZipFileException",
            "FunctionError",
        ),
    )
    file_system_configs = StringType(deserialize_from="FileSystemConfigs")
    package_type = StringType(deserialize_from="PackageType", choices=("Zip", "Image"))
    image_config_response = StringType(deserialize_from="ImageConfigResponse")
    signing_profile_version_arn = StringType(
        deserialize_from="SigningProfileVersionArn"
    )
    signing_job_arn = StringType(deserialize_from="SigningJobArn")
    architectures = ListType(StringType, deserialize_from="Architectures")
    ephemeral_storage = StringType(deserialize_from="EphemeralStorage")
    snap_start = StringType(deserialize_from="SnapStart")
    runtime_version_config = StringType(deserialize_from="RuntimeVersionConfig")
    logging_config = StringType(deserialize_from="LoggingConfig")
