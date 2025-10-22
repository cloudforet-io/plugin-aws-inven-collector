from typing import List
from ..base import ResourceManager
from ...conf.cloud_service_conf import *
from spaceone.inventory.plugin.collector.lib import *

from ...model.acm import Certificate


class CertificateManager(ResourceManager):
    cloud_service_group = "ACM"
    cloud_service_type = "Certificate"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_group = "ACM"
        self.cloud_service_type = "Certificate"
        self.metadata_path = "metadata/acm/certificate.yaml"

    def create_cloud_service_type(self) -> List[dict]:
        yield make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
            service_code="AWSCertificateManager",
            tags={"spaceone:icon": f"{ASSET_URL}/AWS-Certificate-Manager.svg"},
            labels=["Security"],
        )

    def create_cloud_service(
        self, region: str, options: dict, secret_data: dict, schema: str
    ) -> List[dict]:
        yield from self._collect_certificates(options, region)

    def _collect_certificates(self, options: dict, region: str) -> List[dict]:
        results = self.connector.get_certificates()

        for data in results:
            for raw in data.get("CertificateSummaryList", []):
                try:
                    certificate_arn = raw.get("CertificateArn")
                    certificate_response = self.connector.describe_certificate(
                        certificate_arn
                    )
                    certificate_info = certificate_response.get("Certificate", {})
                    certificate_info.update(
                        {
                            "type_display": self.get_string_title(
                                certificate_info.get("Type")
                            ),
                            "renewal_eligibility_display": self.get_string_title(
                                certificate_info.get("RenewalEligibility")
                            ),
                            "identifier": self.get_identifier(
                                certificate_info.get("CertificateArn")
                            ),
                            "additional_names_display": self.get_additional_names_display(
                                certificate_info.get("SubjectAlternativeNames")
                            ),
                            "in_use_display": self.get_in_use_display(
                                certificate_info.get("InUseBy")
                            ),
                            "cloudwatch": self.set_cloudwatch(
                                self.cloud_service_group,
                                certificate_info.get("CertificateArn"),
                                region,
                            ),
                            "cloudtrail": self.set_cloudtrail(
                                self.cloud_service_group,
                                raw["CertificateArn"],
                                region,
                            ),
                        }
                    )

                    self._update_times(certificate_info)

                    certificate_vo = Certificate(certificate_info, strict=False)

                    certificate_arn = certificate_vo.certificate_arn
                    link = f"https://console.aws.amazon.com/acm/home?region={region}#/?id={certificate_info.get('identifier')}"
                    reference = self.get_reference(certificate_arn, link)

                    cloud_service = make_cloud_service(
                        name=certificate_vo.domain_name,
                        cloud_service_type=self.cloud_service_type,
                        cloud_service_group=self.cloud_service_group,
                        provider=self.provider,
                        data=certificate_vo.to_primitive(),
                        account=options.get("account_id"),
                        reference=reference,
                        tags=self.get_tags(certificate_arn),
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

    def get_tags(self, arn: str) -> dict:
        tag_response = self.connector.list_tags_for_certificate(arn)
        return self.convert_tags_to_dict_type(tag_response.get("Tags", []))

    def _update_times(self, certificate_info: dict) -> None:
        certificate_info.update(
            {
                "CreatedAt": self.datetime_to_iso8601(
                    certificate_info.get("CreatedAt")
                ),
                "IssuedAt": self.datetime_to_iso8601(certificate_info.get("IssuedAt")),
                "ImportedAt": self.datetime_to_iso8601(
                    certificate_info.get("ImportedAt")
                ),
                "RevokedAt": self.datetime_to_iso8601(
                    certificate_info.get("RevokedAt")
                ),
                "NotBefore": self.datetime_to_iso8601(
                    certificate_info.get("NotBefore")
                ),
                "NotAfter": self.datetime_to_iso8601(certificate_info.get("NotAfter")),
            }
        )
        renewal_info = certificate_info.get("RenewalSummary", {})
        renewal_info.update(
            {"UpdatedAt": self.datetime_to_iso8601(renewal_info.get("UpdatedAt"))}
        )

    @staticmethod
    def get_identifier(certificate_arn: str) -> str:
        return certificate_arn.split("/")[-1]

    @staticmethod
    def get_additional_names_display(subject_alternative_names: List[str]) -> List[str]:
        return subject_alternative_names[1:]

    @staticmethod
    def get_in_use_display(in_use_by: List[str]) -> str:
        if in_use_by:
            return "Yes"
        else:
            return "No"

    @staticmethod
    def get_string_title(s: str) -> str:
        try:
            display_title = s.replace("_", " ").title()
        except Exception as e:
            display_title = s

        return display_title
