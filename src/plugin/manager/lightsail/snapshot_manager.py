from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lightsail import Snapshot


class SnapshotManager(ResourceManager):
    cloud_service_group = "Lightsail"
    cloud_service_type = "Snapshot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Snapshot"
        self.metadata_path = "metadata/lightsail/snapshot.yaml"

    def create_cloud_service_type(self):
        result = []
        snapshot_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AmazonLightsail",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-lightsail.svg"
            },
            labels=["Storage"],
        )
        result.append(snapshot_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_snapshots(options, region)

    def _collect_snapshots(self, options, region):
        region_name = region

        try:
            snapshots, account_id = self.connector.list_lightsail_snapshots()

            for snapshot in snapshots:
                try:
                    snapshot_name = snapshot.get("Name")
                    snapshot_arn = snapshot.get("Arn")

                    # Get snapshot tags
                    tags = self._get_snapshot_tags(snapshot_arn)

                    snapshot_data = {
                        "name": snapshot_name,
                        "arn": snapshot_arn,
                        "created_at": snapshot.get("CreatedAt"),
                        "location": snapshot.get("Location", {}),
                        "resource_type": snapshot.get("ResourceType", ""),
                        "tags": snapshot.get("Tags", []),
                        "support_code": snapshot.get("SupportCode", ""),
                        "size_in_gb": snapshot.get("SizeInGb", 0),
                        "state": snapshot.get("State", ""),
                        "progress": snapshot.get("Progress", ""),
                        "from_resource_name": snapshot.get("FromResourceName", ""),
                        "from_resource_arn": snapshot.get("FromResourceArn", ""),
                        "from_blueprint_id": snapshot.get("FromBlueprintId", ""),
                        "from_bundle_id": snapshot.get("FromBundleId", ""),
                        "is_from_auto_snapshot": snapshot.get(
                            "IsFromAutoSnapshot", False
                        ),
                        "from_attached_disks": snapshot.get("FromAttachedDisks", []),
                    }

                    snapshot_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                snapshot_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                snapshot_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lightsail/home?region={region}#/storage/snapshots/{snapshot_name}"
                    resource_id = snapshot_arn
                    reference = self.get_reference(resource_id, link)

                    snapshot_vo = Snapshot(snapshot_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=snapshot_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=snapshot_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=snapshot_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lightsail_snapshots] [{snapshot.get("Name")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lightsail_snapshots] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_snapshot_tags(self, snapshot_arn):
        """Get snapshot tags"""
        try:
            return self.connector.get_snapshot_tags(snapshot_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for snapshot {snapshot_arn}: {e}")
            return []

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
