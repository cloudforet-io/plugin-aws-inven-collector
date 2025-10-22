import logging

from schematics import Model
from schematics.types import StringType, ModelType, ListType, DateTimeType

_LOGGER = logging.getLogger(__name__)

"""
Alarms
"""

class Action(Model):
    type = StringType(deserialize_from="type")
    arn = StringType(deserialize_from="arn")


class History(Model):
    date = DateTimeType(deserialize_from="date")
    type = StringType(
        choices=("ConfigurationUpdate", "StateUpdate", "Action"),
        deserialize_from="type",
    )
    description = StringType(deserialize_from="description")


class Alarms(Model):
    alarm_arn = StringType(deserialize_from="AlarmArn")
    name = StringType(deserialize_from="AlarmName")
    state_value = StringType(
        choices=("OK", "ALARM", "INSUFFICIENT_DATA"), deserialize_from="StateValue"
    )
    state_updated_timestamp = DateTimeType(deserialize_from="StateUpdatedTimestamp")
    actions_enabled = StringType(deserialize_from="actions_enabled")
    namespace = StringType(deserialize_from="Namespace")
    metric_name = StringType(deserialize_from="MetricName")
    statistic = StringType(
        choices=("SampleCount", "Average", "Sum", "Minimum", "Maximum"),
        deserialize_from="Statistic",
    )
    period = StringType(deserialize_from="Period")
    conditions = StringType(deserialize_from="conditions")
    actions = ListType(
        ModelType(Action, deserialize_from="action"), deserialize_from="actions"
    )
    history = ListType(
        ModelType(History, deserialize_from="history"), deserialize_from="history"
    )
