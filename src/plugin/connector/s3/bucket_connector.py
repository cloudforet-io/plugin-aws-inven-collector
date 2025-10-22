from plugin.connector.base import ResourceConnector


class BucketConnector(ResourceConnector):
    service_name = "s3"
    cloud_service_group = "S3"
    cloud_service_type = "Bucket"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "s3"
        self.cloud_service_group = "S3"
        self.cloud_service_type = "Bucket"
        self.rest_service_name = "s3"

    def list_buckets(self):
        response = self.client.list_buckets()
        return response.get("Buckets", [])

    def get_bucket_location(self, bucket_name):
        response = self.client.get_bucket_location(Bucket=bucket_name)
        return response.get("LocationConstraint", "us-east-1")

    def get_bucket_tags(self, bucket_name):
        response = self.client.get_bucket_tagging(Bucket=bucket_name)
        return response.get("TagSet", [])

    def get_bucket_policy(self, bucket_name):
        response = self.client.get_bucket_policy(Bucket=bucket_name)
        return response.get("Policy", "")

    def get_bucket_versioning(self, bucket_name):
        response = self.client.get_bucket_versioning(Bucket=bucket_name)
        return response

    def get_bucket_encryption(self, bucket_name):
        response = self.client.get_bucket_encryption(Bucket=bucket_name)
        return response.get("ServerSideEncryptionConfiguration", {})

    def get_bucket_acl(self, bucket_name):
        response = self.client.get_bucket_acl(Bucket=bucket_name)
        return response

    def get_bucket_lifecycle(self, bucket_name):
        response = self.client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return response.get("Rules", [])
