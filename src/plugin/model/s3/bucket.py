import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Bucket(Model):
    name = StringType(deserialize_from="Name")
    creation_date = DateTimeType(deserialize_from="CreationDate")
    bucket_location_constraint = StringType(deserialize_from="BucketLocationConstraint")
    versioning = StringType(deserialize_from="Versioning")
    website = StringType(deserialize_from="Website")
    logging = StringType(deserialize_from="Logging")
    cors = StringType(deserialize_from="Cors")
    lifecycle = StringType(deserialize_from="Lifecycle")
    policy = StringType(deserialize_from="Policy")
    policy_status = StringType(deserialize_from="PolicyStatus")
    acl = StringType(deserialize_from="Acl")
    server_side_encryption_configuration = StringType(
        deserialize_from="ServerSideEncryptionConfiguration"
    )
    request_payment = StringType(deserialize_from="RequestPayment")
    notification = StringType(deserialize_from="Notification")
    replication = StringType(deserialize_from="Replication")
    tagging = StringType(deserialize_from="Tagging")
    accelerate_configuration = StringType(deserialize_from="AccelerateConfiguration")
    public_access_block_configuration = StringType(
        deserialize_from="PublicAccessBlockConfiguration"
    )
    object_lock_configuration = StringType(deserialize_from="ObjectLockConfiguration")
    intelligent_tiering_configurations = StringType(
        deserialize_from="IntelligentTieringConfigurations"
    )
    inventory_configurations = StringType(deserialize_from="InventoryConfigurations")
    analytics_configurations = StringType(deserialize_from="AnalyticsConfigurations")
    metrics_configurations = StringType(deserialize_from="MetricsConfigurations")
    ownership_controls = StringType(deserialize_from="OwnershipControls")
