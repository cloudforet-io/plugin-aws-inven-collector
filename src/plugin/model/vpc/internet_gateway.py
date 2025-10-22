import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class InternetGateway(Model):
    attachments = StringType(deserialize_from="Attachments")
    internet_gateway_id = StringType(deserialize_from="InternetGatewayId")
    owner_id = StringType(deserialize_from="OwnerId")
    tags = StringType(deserialize_from="Tags")
