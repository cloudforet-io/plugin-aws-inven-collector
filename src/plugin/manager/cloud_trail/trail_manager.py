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
        return make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AWSCloudTrail",
            tags={"spaceone:icon": f"{ASSET_URL}/AWS-Cloudtrail.svg"},
            labels=["Management"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        cloudwatch_namespace = "CloudTrailMetrics"
        cloudtrail_resource_type = "AWS::CloudTrail::Trail"
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

                # yield Trail(raw, strict=False), self._match_tags(raw['TrailARN'], tags)

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
                # resource_id = raw.get("ARN", "")
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

    # def _get_tags(self, trail, region_name):
    #     # self.reset_region(region_name)
    #     response = self.client.list_tags(ResourceIdList=[trail.get('TrailARN')])
    #     for _resource_tag in response.get('ResourceTagList', []):
    #         tags_list = _resource_tag.get('TagsList', [])
    #         print(tags_list)
    #         return self.convert_tags_to_dict_type(tags_list)
    #
    #     return {}

    # def _list_tags(self, trails):
    #     tags = []
    #     trails_from_region = self._sort_trail_from_region(trails)
    #
    #     for _region in trails_from_region:
    #         self.reset_region(_region)
    #         response = self.client.list_tags(ResourceIdList=trails_from_region[_region])
    #         tags.extend(response.get('ResourceTagList', []))
    #
    #     return tags

    def _get_insight_selectors(self, trail_name):
        response = self.connector.get_insight_selectors(trail_name)

        insight_selectors = response.get("InsightSelectors", [])
        if len(insight_selectors) == 0:
            return None
        else:
            return insight_selectors[0]

    # def _match_tags(self, trail_arn, tags):
    #     tag_dict = {}
    #
    #     try:
    #         for tag in tags:
    #             if tag['ResourceId'] == trail_arn:
    #                 tag_dict.update(self.convert_tags_to_dict_type(tag['TagsList']))
    #     except Exception as e:
    #         _LOGGER.error(e)
    #
    #     return tag_dict

    # @staticmethod
    # def _sort_trail_from_region(trails):
    #     return_dic = {}
    #
    #     for _trail in trails:
    #         trail_arn = _trail.get('TrailARN', '')
    #         split_trail = trail_arn.split(':')
    #         try:
    #             region = split_trail[3]
    #             if region in return_dic:
    #                 return_dic[region].append(trail_arn)
    #             else:
    #                 return_dic[region] = [trail_arn]
    #         except IndexError:
    #             pass
    #
    #     return return_dic
