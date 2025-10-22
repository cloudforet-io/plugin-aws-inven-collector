import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class LoadBalancer(Model):
    name = StringType(deserialize_from="name")
    arn = StringType(deserialize_from="arn")
    support_code = StringType(deserialize_from="supportCode")
    created_at = DateTimeType(deserialize_from="createdAt")
    location = StringType(deserialize_from="location")
    resource_type = StringType(deserialize_from="resourceType")
    tags = StringType(deserialize_from="Tags")
    dns_name = StringType(deserialize_from="dnsName")
    state = StringType(
        deserialize_from="state",
        choices=("active", "provisioning", "active_impaired", "failed", "unknown"),
    )
    protocol = StringType(deserialize_from="protocol", choices=("HTTP", "HTTPS"))
    public_ports = ListType(IntType, deserialize_from="publicPorts")
    health_check_path = StringType(deserialize_from="healthCheckPath")
    instance_port = IntType(deserialize_from="instancePort")
    instance_health_summary = StringType(deserialize_from="instanceHealthSummary")
    tls_certificate_summaries = StringType(deserialize_from="tlsCertificateSummaries")
    configuration_options = StringType(deserialize_from="configurationOptions")
    ip_address_type = StringType(deserialize_from="ipAddressType")
    https_redirection_enabled = BooleanType(deserialize_from="httpsRedirectionEnabled")
    tls_policy_name = StringType(deserialize_from="tlsPolicyName")
