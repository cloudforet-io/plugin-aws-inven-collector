from plugin.connector.base import ResourceConnector


class CertificateConnector(ResourceConnector):
    service_name = "acm"
    cloud_service_group = "CertificateManager"
    cloud_service_type = "Certificate"
    include_vpc_default = False

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "acm"
        self.cloud_service_type = "AMI"
        self.cloud_service_group = "CertificateManager"
        self.rest_service_name = "acm"

    def get_certificates(self):
        paginator = self.client.get_paginator("list_certificates")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_certificate(self, certificate_arn):
        return self.client.describe_certificate(CertificateArn=certificate_arn)

    def list_tags_for_certificate(self, certificate_arn):
        return self.client.list_tags_for_certificate(CertificateArn=certificate_arn)
