from plugin.connector.base import ResourceConnector


class IdentityProviderConnector(ResourceConnector):
    service_name = "iam"
    cloud_service_group = "IAM"
    cloud_service_type = "IdentityProvider"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "iam"
        self.cloud_service_group = "IAM"
        self.cloud_service_type = "IdentityProvider"
        self.rest_service_name = "iam"

    def list_open_id_connect_providers(self):
        response = self.client.list_open_id_connect_providers()
        return response.get("OpenIDConnectProviderList", [])

    def get_open_id_connect_provider(self, open_id_connect_provider_arn):
        response = self.client.get_open_id_connect_provider(
            OpenIDConnectProviderArn=open_id_connect_provider_arn
        )
        return response

    def list_saml_providers(self):
        response = self.client.list_saml_providers()
        return response.get("SAMLProviderList", [])

    def get_saml_provider(self, saml_provider_arn):
        response = self.client.get_saml_provider(SAMLProviderArn=saml_provider_arn)
        return response
