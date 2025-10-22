from typing import List

from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service,
    make_error_response,
)

from ..base import ResourceManager, _LOGGER
from ...model.lambda_model import Function


class FunctionManager(ResourceManager):
    cloud_service_group = "Lambda"
    cloud_service_type = "Function"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "Lambda"
        self.cloud_service_type = "Function"
        self.metadata_path = "metadata/lambda_model/function.yaml"

    def create_cloud_service_type(self):
        result = []
        function_cst_result = make_cloud_service_type(
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
        result.append(function_cst_result)
        return result

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ):
        yield from self._collect_functions(options, region)

    def _collect_functions(self, options, region):
        region_name = region

        try:
            functions, account_id = self.connector.list_lambda_functions()

            for function in functions:
                try:
                    function_name = function.get("FunctionName")
                    function_arn = function.get("FunctionArn")

                    # Get function tags
                    tags = self._get_function_tags(function_arn)

                    # Get function configuration
                    configuration = self._get_function_configuration(function_name)

                    # Get function code
                    code = self._get_function_code(function_name)

                    # Get function policy
                    policy = self._get_function_policy(function_name)

                    function_data = {
                        "function_name": function_name,
                        "function_arn": function_arn,
                        "runtime": function.get("Runtime", ""),
                        "role": function.get("Role", ""),
                        "handler": function.get("Handler", ""),
                        "code_size": function.get("CodeSize", 0),
                        "description": function.get("Description", ""),
                        "timeout": function.get("Timeout", 0),
                        "memory_size": function.get("MemorySize", 0),
                        "last_modified": function.get("LastModified", ""),
                        "code_sha256": function.get("CodeSha256", ""),
                        "version": function.get("Version", ""),
                        "vpc_config": function.get("VpcConfig", {}),
                        "dead_letter_config": function.get("DeadLetterConfig", {}),
                        "environment": function.get("Environment", {}),
                        "kms_key_arn": function.get("KMSKeyArn", ""),
                        "tracing_config": function.get("TracingConfig", {}),
                        "master_arn": function.get("MasterArn", ""),
                        "revision_id": function.get("RevisionId", ""),
                        "layers": function.get("Layers", []),
                        "state": function.get("State", ""),
                        "state_reason": function.get("StateReason", ""),
                        "state_reason_code": function.get("StateReasonCode", ""),
                        "last_update_status": function.get("LastUpdateStatus", ""),
                        "last_update_status_reason": function.get(
                            "LastUpdateStatusReason", ""
                        ),
                        "last_update_status_reason_code": function.get(
                            "LastUpdateStatusReasonCode", ""
                        ),
                        "file_system_configs": function.get("FileSystemConfigs", []),
                        "package_type": function.get("PackageType", ""),
                        "image_config_response": function.get(
                            "ImageConfigResponse", {}
                        ),
                        "signing_profile_version_arn": function.get(
                            "SigningProfileVersionArn", ""
                        ),
                        "signing_job_arn": function.get("SigningJobArn", ""),
                        "architectures": function.get("Architectures", []),
                        "ephemeral": function.get("Ephemeral", {}),
                        "snap_start": function.get("SnapStart", {}),
                        "runtime_version_config": function.get(
                            "RuntimeVersionConfig", {}
                        ),
                        "configuration": configuration,
                        "code": code,
                        "policy": policy,
                    }

                    function_data.update(
                        {
                            "region_code": region_name,
                            "account": account_id,
                            "tags": self.convert_tags(tags),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                function_name,
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                function_name,
                                region,
                            ),
                        }
                    )

                    link = f"https://{region}.console.aws.amazon.com/lambda_model/home?region={region}#/functions/{function_name}"
                    resource_id = function_arn
                    reference = self.get_reference(resource_id, link)

                    function_vo = Function(function_data, strict=False)
                    cloud_service = make_cloud_service(
                        name=function_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=function_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=function_data.get("tags", {}),
                        region_code=region,
                    )
                    yield cloud_service

                except Exception as e:
                    _LOGGER.error(
                        f'[list_lambda_functions] [{function.get("FunctionName")}] {e}'
                    )
                    yield make_error_response(
                        error=e,
                        provider=self.provider,
                        cloud_service_group=self.cloud_service_group,
                        cloud_service_type=self.cloud_service_type,
                        region_name=region,
                    )

        except Exception as e:
            _LOGGER.error(f"[list_lambda_functions] [{region_name}] {e}")
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
                region_name=region,
            )

    def _get_function_tags(self, function_arn):
        """Get function tags"""
        try:
            return self.connector.get_function_tags(function_arn)
        except Exception as e:
            _LOGGER.warning(f"Failed to get tags for function {function_arn}: {e}")
            return []

    def _get_function_configuration(self, function_name):
        """Get function configuration"""
        try:
            return self.connector.get_function_configuration(function_name)
        except Exception as e:
            _LOGGER.warning(
                f"Failed to get configuration for function {function_name}: {e}"
            )
            return {}

    def _get_function_code(self, function_name):
        """Get function code"""
        try:
            return self.connector.get_function_code(function_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get code for function {function_name}: {e}")
            return {}

    def _get_function_policy(self, function_name):
        """Get function policy"""
        try:
            return self.connector.get_function_policy(function_name)
        except Exception as e:
            _LOGGER.warning(f"Failed to get policy for function {function_name}: {e}")
            return {}

    def convert_tags(self, tags):
        """Convert tags to dictionary format"""
        dict_tags = {}
        for tag in tags:
            dict_tags[tag.get("Key")] = tag.get("Value")
        return dict_tags
