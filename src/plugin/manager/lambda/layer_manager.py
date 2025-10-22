from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lambda_model import Layer


class LayerManager(ResourceManager):
    cloud_service_group = "Lambda"
    cloud_service_type = "Layer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lambda"
        self.cloud_service_type = "Layer"
        self.metadata_path = "metadata/lambda_model/layer.yaml"

    def create_cloud_service_type(self):
        result = []
        layer_cst_result = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AWSLambda",
            tags={
                "spaceone:icon": "https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-lambda.svg"
            },
            labels=["Compute"],
        )
        result.append(layer_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_layers(options, region)

    def _collect_layers(self, options, region):
        region_name = region
        cloudtrail_resource_type = "AWS::Lambda::LayerVersion"

        try:
            layers, account_id = self.connector.list_lambda_layers()

            for layer in layers:
                try:
                    layer_name = layer.get("LayerName")
                    layer_arn = layer.get("LayerArn")
                    version = layer.get("Version")

                    # Get layer tags
                    tags = self._get_layer_tags(layer_arn)

                    # Get layer version details
                    layer_version = self._get_layer_version(layer_name, version)

                    layer_data = {
                        "layer_name": layer_name,
                        "layer_arn": layer_arn,
                        "version": version,
                        "description": layer.get("Description", ""),
                        "created_date": layer.get("CreatedDate", ""),
                        "layer_version_arn": layer.get("LayerVersionArn", ""),
                        "compatible_runtimes": layer.get("CompatibleRuntimes", []),
                        "license_info": layer.get("LicenseInfo", ""),
                        "compatible_architectures": layer.get(
                            "CompatibleArchitectures", []
                        ),
                        "layer_version": layer_version,
                    }

                    layer_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lambda_model/home?region={region}#/layers/{layer_name}"
                    resource_id = layer_arn
                    reference = self.get_reference(resource_id, link)

                    layer_vo = Layer(layer_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=f"{layer_name}:{version}",
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=layer_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=layer_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lambda_layers] [{layer.get("LayerName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lambda_layers] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_layer_tags(self, layer_arn):
        """Get layer tags"""
        try:
            return self.connector.get_layer_tags(layer_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for layer {layer_arn}: {e}")
            return []

    def _get_layer_version(self, layer_name, version):
        """Get layer version details"""
        try:
            return self.connector.get_layer_version(layer_name, version)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get version for layer {layer_name}:{version}: {e}"
            )
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
