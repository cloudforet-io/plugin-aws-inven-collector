import logging
from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, BooleanType, IntType

_LOGGER = logging.getLogger(__name__)


class Layer(Model):
    layer_name = StringType(deserialize_from="LayerName")
    layer_arn = StringType(deserialize_from="LayerArn")
    version = IntType(deserialize_from="Version")
    description = StringType(deserialize_from="Description")
    created_date = DateTimeType(deserialize_from="CreatedDate")
    layer_version_arn = StringType(deserialize_from="LayerVersionArn")
    compatible_runtimes = ListType(StringType, deserialize_from="CompatibleRuntimes")
    license_info = StringType(deserialize_from="LicenseInfo")
    compatible_architectures = ListType(
        StringType, deserialize_from="CompatibleArchitectures"
    )
