from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.cloudwatch.alarms import Alarms


class AlarmsManager(ResourceManager):
    cloud_service_group = "CloudWatch"
    cloud_service_type = "Alarms"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudWatch"
        self.cloud_service_type = "Alarms"
        self.metadata_path = "metadata/cloudwatch/alarms.yaml"

    def create_cloud_service_type(self):
        result = []
        alarms_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonCloudWatch",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-cloudwatch.svg"
            },
            labels=["Management", "Monitoring"],
        )
        result.append(alarms_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_alarms(options, region)

    def _collect_alarms(self, options, region):
        region_name = region
        account_id = options.get("account_id")

        try:
            for alarm in self.connector.get_alarms():
                try:
                    alarm_name = alarm.get("AlarmName")
                    alarm_arn = alarm.get("AlarmArn")

                    self._set_alarm_conditions(alarm)
                    self._set_alarm_actions(alarm)
                    self._set_alarm_history(alarm)

                    alarm.update(
                        {
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group, None, region_name
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group, alarm_arn, region_name
                            ),
                        }
                    )

                    tags = self.connector.get_alarm_tags(alarm_arn)

                    link = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{alarm_name}"
                    reference = self.get_reference(alarm_arn, link)

                    alarm_vo = Alarms(alarm, strict=False)
                    cloud_service = make_cloud_service(
                        name=alarm_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=alarm_vo.to_primitive(),
                        account=account_id,
                        reference=reference,
                        tags=tags,
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(f'[list_alarms] [{alarm.get("AlarmName")}] {e}')
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_alarms] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _set_alarm_conditions(self, alarm):
        metric_name = alarm.get("MetricName", "?")
        period = alarm.get("Period", None)
        evaluation_periods = self._convert_int_type(
            alarm.get("EvaluationPeriods", "?")
        )
        threshold = self._convert_int_type(alarm.get("Threshold", "?"))
        comparison_operator = alarm.get("ComparisonOperator", "?")

        period_minutes = period // 60 if period and isinstance(period, int) else "?"

        comparison_operator_map = {
            "GreaterThanOrEqualToThreshold": ">=",
            "GreaterThanThreshold": ">",
            "LessThanThreshold": "<",
            "LessThanOrEqualToThreshold": "<=",
            "LessThanLowerOrGreaterThanUpperThreshold": "<>",
            "LessThanLowerThreshold": "<",
            "GreaterThanUpperThreshold": ">",
        }
        operator = comparison_operator_map.get(comparison_operator, "?")

        alarm["conditions"] = (
            f"{metric_name} {operator} {threshold} for {evaluation_periods} datapoionts within {period_minutes} minutes"
        )

    def _set_alarm_actions(self, alarm):
        alarm["actions"] = []
        actions = alarm["actions"]

        alarm_actions = alarm.get("AlarmActions", [])
        ok_actions = alarm.get("OKActions", [])
        insufficient_data_actions = alarm.get("InsufficientDataActions", [])

        alarm["actions_enabled"] = (
            "Actions enabled" if alarm.get("ActionsEnabled", False) else "No actions"
        )

        for action in alarm_actions:
            actions.append({"type": "AlarmAction", "arn": action})

        for action in ok_actions:
            actions.append({"type": "OKAction", "arn": action})

        for action in insufficient_data_actions:
            actions.append({"type": "InsufficientDataAction", "arn": action})

    def _set_alarm_history(self, alarm):
        alarm["history"] = []
        history = alarm["history"]

        alarm_histories = self.connector.get_alarm_history(
            alarm["AlarmName"]
        )
        for alarm_history in alarm_histories:
            history.append(
                {
                    "date": alarm_history.get("Timestamp"),
                    "type": alarm_history.get("HistoryItemType"),
                    "description": alarm_history.get("HistorySummary"),
                }
            )

    @staticmethod
    def _convert_int_type(value):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value
