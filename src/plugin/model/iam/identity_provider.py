import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType

_LOGGER = logging.getLogger(__name__)


class IdentityProvider(Model):
    url = StringType(deserialize_from="Url")
    create_date = DateTimeType(deserialize_from="CreateDate")
    thumbprint_list = ListType(StringType, deserialize_from="ThumbprintList")
    tags = StringType(deserialize_from="Tags")
