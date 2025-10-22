from plugin.connector.base import ResourceConnector


class FileSystemConnector(ResourceConnector):
    service_name = "efs"
    cloud_service_group = "EFS"
    cloud_service_type = "FileSystem"

    def __init__(self, secret_data, region_name):
        super().__init__(secret_data, region_name)
        self.service_name = "efs"
        self.cloud_service_group = "EFS"
        self.cloud_service_type = "FileSystem"
        self.rest_service_name = "efs"

    def describe_file_systems(self):
        paginator = self.client.get_paginator("describe_file_systems")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            }
        )
        return response_iterator

    def describe_lifecycle_configuration(self, file_system_id):
        response = self.client.describe_lifecycle_configuration(
            FileSystemId=file_system_id
        )
        return response.get("LifecyclePolicies", [])

    def describe_mount_targets(self, file_system_id):
        paginator = self.client.get_paginator("describe_mount_targets")
        response_iterator = paginator.paginate(
            FileSystemId=file_system_id,
            PaginationConfig={
                "MaxItems": 10000,
                "PageSize": 50,
            },
        )
        return response_iterator

    def describe_tags(self, file_system_id):
        response = self.client.describe_tags(FileSystemId=file_system_id)
        return response.get("Tags", [])
