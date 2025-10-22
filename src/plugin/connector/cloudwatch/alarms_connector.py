from datetime import datetime
from dateutil.relativedelta import relativedelta

from plugin.connector.base import ResourceConnector


class AlarmsConnector(ResourceConnector):
    service_name = "cloudwatch"
    cloud_service_group = "CloudWatch"
    cloud_service_type = "Alarm"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "cloudwatch"
        self.cloud_service_type = "Alarm"
        self.rest_service_name = "cloudwatch"

    def get_alarms(self):
        paginator = self.client.get_paginator("describe_alarms")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxRecords": 100,
            }
        )

        for data in response_iterator:
            # Only MetricAlarms are returned temporarily, CompositeAlarms must be applied later.
            for raw in data.get("MetricAlarms", []):
                yield raw

    def get_alarm_tags(self, alarm_arn):
        return self.client.list_tags_for_resource(ResourceARN=alarm_arn)

    def get_alarm_history(self, alarm_name):
        paginator = self.client.get_paginator("describe_alarm_history")
        end_date = datetime.now() - relativedelta(months=1)
        response_iterator = paginator.paginate(
            PaginationConfig={
                "AlarmName": alarm_name,
                "MaxItems": 100,
                "EndDate": end_date,
                "ScanBy": "TimestampDescending",
            }
        )

        for data in response_iterator:
            for raw in data.get("AlarmHistoryItems", []):
                yield raw
