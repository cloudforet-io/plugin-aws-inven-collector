import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class TargetGroup(Model):
    target_group_arn = StringType(deserialize_from="TargetGroupArn")
    target_group_name = StringType(deserialize_from="TargetGroupName")
    protocol = StringType(
        deserialize_from="Protocol",
        choices=("HTTP", "HTTPS", "TCP", "TLS", "UDP", "TCP_UDP", "GENEVE"),
    )
    port = IntType(deserialize_from="Port")
    vpc_id = StringType(deserialize_from="VpcId")
    health_check_protocol = StringType(
        deserialize_from="HealthCheckProtocol",
        choices=("HTTP", "HTTPS", "TCP", "TLS", "UDP", "TCP_UDP", "GENEVE"),
    )
    health_check_port = StringType(deserialize_from="HealthCheckPort")
    health_check_enabled = BooleanType(deserialize_from="HealthCheckEnabled")
    health_check_interval_seconds = IntType(
        deserialize_from="HealthCheckIntervalSeconds"
    )
    health_check_timeout_seconds = IntType(deserialize_from="HealthCheckTimeoutSeconds")
    healthy_threshold_count = IntType(deserialize_from="HealthyThresholdCount")
    unhealthy_threshold_count = IntType(deserialize_from="UnhealthyThresholdCount")
    health_check_path = StringType(deserialize_from="HealthCheckPath")
    matcher = StringType(deserialize_from="Matcher")
    load_balancer_arns = ListType(StringType, deserialize_from="LoadBalancerArns")
    target_type = StringType(
        deserialize_from="TargetType", choices=("instance", "ip", "lambda_model", "alb")
    )
    protocol_version = StringType(deserialize_from="ProtocolVersion")
    tags = StringType(deserialize_from="Tags")
