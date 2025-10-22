import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class OptionGroup(Model):
    option_group_name = StringType(deserialize_from="OptionGroupName")
    option_group_description = StringType(deserialize_from="OptionGroupDescription")
    engine_name = StringType(deserialize_from="EngineName")
    major_engine_version = StringType(deserialize_from="MajorEngineVersion")
    options = StringType(deserialize_from="Options")
    allows_vpc_and_non_vpc_instance_memberships = BooleanType(
        deserialize_from="AllowsVpcAndNonVpcInstanceMemberships"
    )
    vpc_id = StringType(deserialize_from="VpcId")
    option_group_arn = StringType(deserialize_from="OptionGroupArn")
    source_option_group = StringType(deserialize_from="SourceOptionGroup")
    source_account_id = StringType(deserialize_from="SourceAccountId")
    copy_timestamp = DateTimeType(deserialize_from="CopyTimestamp")
