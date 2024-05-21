from typing import List

from spaceone.inventory.plugin.collector.lib import *

from ..base import ResourceManager
from ...conf.cloud_service_conf import ASSET_URL
from ...manager.base import _LOGGER


class AMIManager(ResourceManager):
    cloud_service_group = "EC2"
    cloud_service_type = "AMI"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "EC2"
        self.cloud_service_type = "AMI"
        self.metadata_path = "metadata/ec2/ami.yaml"

    def create_cloud_service_type(self) -> List[dict]:
        result = []
        ami_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=False,
            is_major=False,
            service_code="AmazonEC2",
            tags={"spaceone:icon": f"{ASSET_URL}/Amazon-AMI.svg"},
            labels=["Compute"],
        )
        result.append(ami_cst_result)
        return result

    def create_cloud_service(self, region, options, secret_data, schema):
        self.cloud_service_type = "AMI"
        cloudtrail_resource_type = "AWS::EC2::Ami"
        results = self.connector.get_ami_images()
        account_id = options.get("account_id", "")
        self.connector.load_account_id(account_id)
        for image in results.get("Images", []):
            try:
                try:
                    permission_info = self.connector.get_ami_image_attributes(image)
                    if permission_info:
                        image.update(
                            {
                                "launch_permissions": [
                                    _permission
                                    for _permission in permission_info.get(
                                        "LaunchPermissions", []
                                    )
                                ]
                            }
                        )

                except Exception as e:
                    _LOGGER.debug(f"[ami][request_ami_data] SKIP: {e}")

                platform = image.get("Platform", "")
                image.update(
                    {
                        "Platform": platform if platform else "Other Linux",
                        "Cloudtrail": self.set_cloudtrail(
                            region, cloudtrail_resource_type, image["ImageId"]
                        ),
                    }
                )

                reference = self._get_reference(region, image.get("ImageId", ""))

                image_vo = image
                cloud_service = make_cloud_service(
                    name=image_vo.get("Name", ""),
                    cloud_service_type=self.cloud_service_type,
                    cloud_service_group=self.cloud_service_group,
                    provider=self.provider,
                    data=image_vo,
                    instance_type=image_vo.get("ImageType", ""),
                    account=account_id,
                    tags=self.convert_tags_to_dict_type(image.get("Tags", [])),
                    reference=reference,
                    region_code=region,
                )
                yield cloud_service
                # yield {
                #     'data': image_vo,
                #     'name': image_vo.get('Name', ''),
                #     'instance_type': image_vo.get('ImageType', ''),
                #     'account': account_id,
                #     'tags': self.convert_tags_to_dict_type(image.get('Tags', []))
                # }
            except Exception as e:
                # resource_id = image.get('ImageId', '')
                yield make_error_response(
                    error=e,
                    provider=self.provider,
                    cloud_service_group=self.cloud_service_group,
                    cloud_service_type=self.cloud_service_type,
                    region_name=region,
                )

    @staticmethod
    def _get_reference(region, image_id):
        return {
            "resource_id": image_id,
            "external_link": f"https://console.aws.amazon.com/ec2/v2/home?region={region}#Images:visibility=public-images;imageId={image_id};sort=name",
        }
