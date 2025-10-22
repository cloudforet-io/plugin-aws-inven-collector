import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class NetworkACL(Model):
    associations = StringType(deserialize_from="Associations")
    entries = StringType(deserialize_from="Entries")
    is_default = BooleanType(deserialize_from="IsDefault")
    network_acl_id = StringType(deserialize_from="NetworkAclId")
    tags = StringType(deserialize_from="Tags")
    vpc_id = StringType(deserialize_from="VpcId")
    owner_id = StringType(deserialize_from="OwnerId")
