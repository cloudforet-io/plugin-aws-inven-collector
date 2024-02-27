from spaceone.inventory.plugin.collector.lib import *
from ..base import ResourceManager
from ...conf.cloud_service_conf import *


class DistributionManager(ResourceManager):
    cloud_service_group = "CloudFront"
    cloud_service_type = "Distribution"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "CloudFront"
        self.cloud_service_type = "Distribution"
        self.metadata_path = "metadata/cloudfront/distribution.yaml"

    def create_cloud_service_type(self):
        return make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonCloudFront",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-CloudFront.svg"},
            labels=["Security"],
        )

    def create_cloud_service(self, region, options, secret_data, schema):
        cloudwatch_namespace = "AWS/CloudFront"
        cloudwatch_dimension_name = "DistributionId"
        cloudtrail_resource_type = "AWS::CloudFront::Distribution"
        self.connector.set_account_id()
        results = self.connector.get_distributions()
        account_id = self.connector.get_account_id()
        for data in results:
            for raw in data.get("DistributionList", {}).get("Items", []):
                try:
                    raw.update(
                        {
                            "state_display": self.get_state_display(raw.get("Enabled")),
                            "cloudwatch": self.set_cloudwatch(
                                cloudwatch_namespace,
                                cloudwatch_dimension_name,
                                raw["Id"],
                                "us-east-1",
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                "us-east-1", cloudtrail_resource_type, raw["Id"]
                            ),
                        }
                    )
                    link = f"https://console.aws.amazon.com/cloudfront/home?#distribution-settings:{raw.get('Id', '')}"
                    reference = self.get_reference(raw.get("ARN", ""), link)

                    # Converting datetime type attributes to ISO8601 format needed to meet protobuf format
                    self._update_times(raw)

                    distribution_vo = raw
                    cloud_service = make_cloud_service(
                        name=distribution_vo.get("DomainName", ""),
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=distribution_vo,
                        account=account_id,
                        tags=self.list_tags_for_resource(
                            distribution_vo.get("ARN", "")
                        ),
                        reference=reference,
                        region_code=region,
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

    def list_tags_for_resource(self, arn):
        response = self.connector.list_tags_for_resource(arn)
        return self.convert_tags_to_dict_type(response.get("Tags", {}).get("Items", []))

    def _update_times(self, raw):
        raw.update(
            {
                "LastModifiedTime": self.datetime_to_iso8601(
                    raw.get("LastModifiedTime")
                ),
            }
        )

    @staticmethod
    def get_state_display(enabled):
        if enabled:
            return "Enabled"
        else:
            return "Disabled"

    @staticmethod
    def _get_reference(distribution_arn, distribution_id):
        return {
            "resource_id": distribution_arn,
            "external_link": f"https://console.aws.amazon.com/cloudfront/home?#distribution-settings:{distribution_id}",
        }
