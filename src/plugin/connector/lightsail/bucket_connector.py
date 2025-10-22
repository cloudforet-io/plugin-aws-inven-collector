from plugin.connector.base import ResourceConnector


class BucketConnector(ResourceConnector):
    service_name = "lightsail"
    cloud_service_group = "Lightsail"
    cloud_service_type = "Bucket"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "lightsail"
        self.cloud_service_group = "Lightsail"
        self.cloud_service_type = "Bucket"
        self.rest_service_name = "lightsail"

    def get_buckets(self):
        response = self.client.get_buckets()
        return response.get("buckets", [])

    def get_bucket(self, bucket_name):
        response = self.client.get_bucket(bucketName=bucket_name)
        return response.get("bucket", {})

    def get_bucket_access_keys(self, bucket_name):
        response = self.client.get_bucket_access_keys(bucketName=bucket_name)
        return response.get("accessKeys", [])

    def get_bucket_metric_data(self, bucket_name, metric_name, start_time, end_time):
        response = self.client.get_bucket_metric_data(
            bucketName=bucket_name,
            metricName=metric_name,
            startTime=start_time,
            endTime=end_time,
        )
        return response.get("metricData", [])
