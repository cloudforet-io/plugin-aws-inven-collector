import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Distribution(Model):
    name = StringType(deserialize_from="name")
    arn = StringType(deserialize_from="arn")
    support_code = StringType(deserialize_from="supportCode")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    alternative_domain_names = ListType(
        StringType, deserialize_from="alternativeDomainNames"
    )
    status = StringType(
        deserialize_from="status",
        choices=("Deployed", "Failed", "InProgress", "Origin"),
    )
    is_enabled = BooleanType(deserialize_from="isEnabled")
    domain_name = StringType(deserialize_from="domainName")
    bundle_id = StringType(deserialize_from="bundleId")
    certificate_name = StringType(deserialize_from="certificateName")
    origin = StringType(deserialize_from="origin")
    origin_public_dns = StringType(deserialize_from="originPublicDNS")
    default_cache_behavior = StringType(deserialize_from="defaultCacheBehavior")
    cache_behavior_settings = StringType(deserialize_from="cacheBehaviorSettings")
    cache_behaviors = StringType(deserialize_from="cacheBehaviors")
    able_to_update_bundle = BooleanType(deserialize_from="ableToUpdateBundle")
    ip_address_type = StringType(deserialize_from="ipAddressType")
    tags = StringType(deserialize_from="Tags")
