from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *


class TrailManager(ResourceManager):
    cloud_service_group = "CloudTrail"
    cloud_service_type = "Trail"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudTrail"
        self.cloud_service_type = "Trail"
        self.metadata_path = "metadata/cloudtrail/trail.yaml"

    def create_cloud_service_type(self):
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AWSCloudTrail",
            tags={"spaceone:icon": f"{ASSET_URL}/AWS-Cloudtrail.svg"},
            labels=["Security"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        cloudwatch_namespace = "CloudTrailMetrics"
        cloudtrail_resource_type = "AWS::CloudTrail::Trail"
        self.connector.set_account_id()
        results = self.connector.get_trails()
        account_id = self.connector.get_account_id()
        trails = results.get("trailList", [])
        # tags = self._list_tags(trails)

        for raw in trails:
            region_name = raw.get("HomeRegion", "")
            try:
                raw["event_selectors"] = list(
                    map(
                        lambda event_selector: event_selector,
                        self._get_event_selector(raw["TrailARN"]),
                    )
                )

                if raw["HasInsightSelectors"]:
                    insight_selectors = self._get_insight_selectors(raw.get("Name"))
                    if insight_selectors is not None:
                        raw["insight_selectors"] = insight_selectors

                raw.update(
                    {
                        "cloudwatch": self.set_cloudwatch(
                            cloudwatch_namespace, None, None, region_name
                        ),
                        "cloudtrail": self.set_cloudtrail(
                            region_name, cloudtrail_resource_type, raw["TrailARN"]
                        ),
                    }
                )

                trail_vol = raw
                trail_arn = trail_vol.get("TrailARN", "")
                link = f"https://console.aws.amazon.com/cloudtrail/home?region={trail_vol.get('HomeRegion', '')}#/configuration/{trail_arn.replace('/', '@')}"
                reference = self.get_reference(trail_arn, link)

                cloud_service = make_cloud_service(
                    name=trail_vol.get("Name", ""),
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=trail_vol,
                    account=account_id,
                    reference=reference,
                    region_code=region_name,
                )
                yield cloud_service

            except Exception as e:
                yield make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=self.cloud_service_type,
                    region_name=region,
                )

    def _get_event_selector(self, trail_arn):
        response = self.connector.get_event_selectors(trail_arn)
        return response.get("EventSelectors", [])

    def _get_insight_selectors(self, trail_name):
        response = self.connector.get_insight_selectors(trail_name)

        insight_selectors = response.get("InsightSelectors", [])
        if len(insight_selectors) == 0:
            return None
        else:
            return insight_selectors[0]
